import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import json
import os
import ollama # Importar ollama al inicio para mejor gestión de dependencias
from datetime import datetime # ¡Importar datetime!

# Importar las funciones de los módulos separados
from audio_processor import transcribe_audio
from llm_processor import generate_minutes_with_ollama
from pdf_generator import create_meeting_minutes_pdf

class MeetingMinutesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Acta de Reunión Inteligente")
        self.root.geometry("1000x700") # Tamaño inicial de la ventana

        self.audio_file_path = None
        self.ollama_models = [] # Se llenará dinámicamente
        self.generated_meeting_data = {} # Para almacenar el acta procesada para exportar

        self._create_widgets()
        # Llamar a _load_ollama_models después de que la ventana principal esté lista
        self.root.after(100, self._load_ollama_models) # Retraso de 100ms

    def _create_widgets(self):
        # --- Frame Principal ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Sección de Carga y Parámetros ---
        input_frame = ttk.LabelFrame(main_frame, text="1. Cargar Audio y Configuración Ollama", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # Cargar Archivo
        ttk.Label(input_frame, text="Archivo de Audio/Video:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.file_path_entry = ttk.Entry(input_frame, width=60, state="readonly") # Inicia como readonly
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.browse_button = ttk.Button(input_frame, text="Examinar...", command=self._browse_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        # Modelo Ollama
        ttk.Label(input_frame, text="Modelo Ollama:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.model_combobox = ttk.Combobox(input_frame, width=57, state="readonly")
        self.model_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        # El combobox se poblará en _load_ollama_models

        # Parámetros Ollama
        param_frame = ttk.LabelFrame(input_frame, text="Parámetros Avanzados (Opcional)", padding="10")
        param_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(param_frame, text="Temperatura (0.1-2.0):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_entry = ttk.Entry(param_frame, textvariable=self.temp_var, width=10)
        self.temp_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(param_frame, text="Tokens Máx. (200-8000):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.tokens_var = tk.IntVar(value=8192) # Aumentado por defecto
        self.tokens_entry = ttk.Entry(param_frame, textvariable=self.tokens_var, width=10)
        self.tokens_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(param_frame, text="Contexto (num_ctx):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.ctx_var = tk.IntVar(value=16384) # Aumentado por defecto
        self.ctx_entry = ttk.Entry(param_frame, textvariable=self.ctx_var, width=10)
        self.ctx_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Botón para generar
        # Deshabilitado al inicio, se habilitará si se carga un archivo y se detectan modelos
        self.generate_button = ttk.Button(input_frame, text="2. Generar Acta", command=self._start_processing, state=tk.DISABLED)
        self.generate_button.grid(row=3, column=0, columnspan=3, pady=10)

        # --- Sección de Salida y Vista Previa ---
        output_frame = ttk.LabelFrame(main_frame, text="3. Vista Previa del Acta y Exportar", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status_label = ttk.Label(output_frame, text="Estado: Listo.", foreground="blue")
        self.status_label.pack(fill=tk.X, pady=5)

        # Usar un Scrollbar para el Text widget
        text_scroll = ttk.Scrollbar(output_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.minutes_text = tk.Text(output_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 10),
                                    yscrollcommand=text_scroll.set)
        self.minutes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_scroll.config(command=self.minutes_text.yview)


        # Botones de acción final
        action_buttons_frame = ttk.Frame(output_frame)
        action_buttons_frame.pack(pady=5)

        self.export_pdf_button = ttk.Button(action_buttons_frame, text="Exportar a PDF", command=self._export_pdf, state=tk.DISABLED)
        self.export_pdf_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = ttk.Button(action_buttons_frame, text="Copiar al Portapapeles", command=self._copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        # Configurar la columna 1 para expandirse en input_frame y param_frame
        input_frame.grid_columnconfigure(1, weight=1)
        param_frame.grid_columnconfigure(1, weight=1)
        param_frame.grid_columnconfigure(3, weight=1)

    def _load_ollama_models(self):
        print("DEBUG: Intentando cargar modelos Ollama...") # DEBUG
        try:
            client = ollama.Client()
            models_info = client.list()
            print(f"DEBUG: Respuesta cruda de client.list(): {models_info}") # DEBUG
            
            # Asegurarse de que 'models' existe y es una lista antes de intentar iterar
            if 'models' in models_info and isinstance(models_info['models'], list):
                # Acceder al atributo .model del objeto Model
                self.ollama_models = [m.model for m in models_info['models']] 
                print(f"DEBUG: Modelos Ollama procesados: {self.ollama_models}") # DEBUG
            else:
                self.ollama_models = [] # No hay modelos o el formato es inesperado
                print("DEBUG: La respuesta de Ollama no contenía la clave 'models' o no era una lista.") # DEBUG
                
            self.model_combobox['values'] = self.ollama_models
            if self.ollama_models:
                self.model_combobox.set(self.ollama_models[0]) # Seleccionar el primer modelo por defecto
                # Habilitar el botón de generar si ya hay un archivo seleccionado (o dejar que browse_file lo haga)
                if self.audio_file_path:
                    self.generate_button.config(state=tk.NORMAL)
                print("DEBUG: Modelos Ollama cargados y combobox poblado exitosamente.") # DEBUG
            else:
                print("DEBUG: No hay modelos Ollama disponibles después de procesar la respuesta.") # DEBUG
                # Schedule the warning message to avoid potential issues during __init__
                self.root.after(100, lambda: messagebox.showwarning(
                    "Modelos Ollama", 
                    "No se encontraron modelos Ollama disponibles o el formato de la respuesta es inesperado.\n"
                    "Por favor, descargue uno (ej: 'ollama run mistral') y asegúrese de que el servidor Ollama esté funcionando y sus modelos estén visibles (`ollama list`)."
                ))
                self.generate_button.config(state=tk.DISABLED)
        
        except ollama.RequestError as e: # Error específico de conexión/petición a Ollama
            print(f"DEBUG: Ollama RequestError: {e}") # DEBUG
            self.root.after(100, lambda e=e: messagebox.showerror(
                "Error de Conexión Ollama", 
                f"No se pudo conectar con el servidor Ollama. Asegúrese de que Ollama esté instalado y ejecutándose (comando `ollama serve`).\nDetalle: {e}"
            ))
            self.generate_button.config(state=tk.DISABLED)
        except KeyError as e: # Error si alguna clave esperada (como 'name') no se encuentra
            print(f"DEBUG: KeyError en datos de modelos Ollama: {e}") # DEBUG
            self.root.after(100, lambda e=e: messagebox.showerror(
                "Error de Datos de Ollama",
                f"El formato de los modelos de Ollama no es el esperado (falta la clave '{e}'). "
                "Esto podría ser por una versión desactualizada de Ollama o de la librería Python.\n"
                "Asegúrese de que Ollama esté funcionando y sus modelos estén visibles (`ollama list`), y considere actualizar `pip install --upgrade ollama`."
            ))
            self.generate_button.config(state=tk.DISABLED)
        except Exception as e: # Catch any other unexpected error
            print(f"DEBUG: Error inesperado general al cargar modelos Ollama: {e}") # DEBUG
            self.root.after(100, lambda e=e: messagebox.showerror(
                "Error General de Ollama", 
                f"Ocurrió un error inesperado al interactuar con Ollama: {e}\n"
                "Asegúrese de que Ollama esté correctamente configurado."
            ))
            self.generate_button.config(state=tk.DISABLED)


    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de Audio/Video", "*.mp4 *.mp3 *.wav *.m4a"), ("Todos los Archivos", "*.*")]
        )
        if file_path:
            self.audio_file_path = file_path
            self.file_path_entry.config(state=tk.NORMAL) # Habilitar para poder borrar/insertar
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.file_path_entry.config(state="readonly") # Volver a solo lectura
            
            # Habilitar el botón de generar si ya hay un modelo seleccionado
            if self.model_combobox.get() and self.ollama_models:
                self.generate_button.config(state=tk.NORMAL)
            else:
                # Si no hay modelos, dejarlo deshabilitado y mostrar un mensaje
                if not self.ollama_models:
                     self.root.after(100, lambda: messagebox.showwarning(
                         "Modelos Ollama", 
                         "Por favor, asegúrese de que el servidor Ollama esté funcionando y tenga modelos descargados."
                     ))

    def _start_processing(self):
        if not self.audio_file_path:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un archivo de audio/video.")
            return
        if not self.model_combobox.get():
            messagebox.showwarning("Advertencia", "Por favor, seleccione un modelo Ollama.")
            return

        self._reset_ui_for_processing()

        # Ejecutar el procesamiento en un hilo separado para no bloquear la GUI
        processing_thread = threading.Thread(target=self._process_meeting)
        processing_thread.start()

    def _reset_ui_for_processing(self):
        self.minutes_text.config(state=tk.NORMAL)
        self.minutes_text.delete(1.0, tk.END)
        self.minutes_text.config(state=tk.DISABLED)
        self.export_pdf_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.generate_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        self.file_path_entry.config(state=tk.DISABLED)
        self.model_combobox.config(state=tk.DISABLED)
        self.status_label.config(text="Estado: Procesando...", foreground="orange")

    def _revert_ui_after_processing(self):
        self.generate_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        # self.file_path_entry.config(state=tk.NORMAL) # No es necesario habilitar para que se pueda borrar, es solo lectura.
        self.model_combobox.config(state="readonly")


    def _process_meeting(self):
        try:
            # 1. Transcripción
            self.status_label.config(text="Estado: Transcribiendo audio (esto puede tomar tiempo)...", foreground="blue")
            self.root.update_idletasks() # Forzar actualización de la GUI
            transcription = transcribe_audio(self.audio_file_path)
            
            # --- DEBUGGING ---
            print(f"DEBUG: Transcripción obtenida (primeros 500 chars):\n{transcription[:500]}...") 
            # -----------------

            if not transcription:
                raise ValueError("La transcripción del audio falló o no produjo texto.")

            # 2. Generación de Acta con Ollama
            self.status_label.config(text="Estado: Analizando con Ollama...", foreground="blue")
            self.root.update_idletasks() # Forzar actualización de la GUI
            selected_model = self.model_combobox.get()
            ollama_params = {
                "temperature": self.temp_var.get(),
                "num_predict": self.tokens_var.get(),
                "num_ctx": self.ctx_var.get(),
            }
            
            # --- ¡NUEVO! Obtener la fecha actual ---
            today_date = datetime.now().strftime("%Y-%m-%d")

            meeting_data_json = generate_minutes_with_ollama(
                transcription,
                selected_model,
                ollama_params,
                current_date=today_date # Pasar la fecha actual al procesador
            )
            
            # Formatear el resultado para mostrar en el Text widget
            formatted_output = self._format_meeting_data_for_display(meeting_data_json)

            self.minutes_text.config(state=tk.NORMAL)
            self.minutes_text.delete(1.0, tk.END)
            self.minutes_text.insert(tk.END, formatted_output)
            # Ya no lo deshabilitamos para permitir la edición
            # self.minutes_text.config(state=tk.DISABLED)

            self.export_pdf_button.config(state=tk.NORMAL)
            self.copy_button.config(state=tk.NORMAL)
            self.status_label.config(text="Estado: Acta generada. Puede editarla antes de exportar.", foreground="green")
            self.generated_meeting_data = meeting_data_json # Guardar para PDF

        except Exception as e:
            messagebox.showerror("Error en el Procesamiento", f"Ocurrió un error: {e}")
            self.status_label.config(text=f"Estado: Error: {e}", foreground="red")
        finally:
            self._revert_ui_after_processing()

    def _format_meeting_data_for_display(self, data):
        # Esta función convierte el JSON del acta a un formato de texto legible para la vista previa
        
        output = []
        output.append(f"--- ACTA DE REUNIÓN ---")
        
        output.append(f"\nTítulo: {data.get('titulo_reunion', 'N/A')}")
        output.append(f"Fecha: {data.get('fecha_reunion', 'N/A')} | Hora: {data.get('hora_inicio', 'N/A')} - {data.get('hora_fin', 'N/A')}")
        output.append(f"Ubicación: {data.get('ubicacion', 'N/A')}")

        # Participantes: Lista de objetos
        participantes_list = data.get('participantes', [])
        if participantes_list:
            participantes_str_list = []
            for p in participantes_list:
                nombre = p.get('nombre', 'Desconocido')
                rol = p.get('rol')
                participantes_str_list.append(f"{nombre}{f' ({rol})' if rol and rol != 'No especificado' else ''}")
            output.append(f"Participantes: {', '.join(participantes_str_list)}")
        else:
            output.append("Participantes: No identificados")
        
        # Ausentes: Lista de objetos
        ausentes_list = data.get('ausentes', [])
        if ausentes_list:
            ausentes_str_list = []
            for a in ausentes_list:
                nombre = a.get('nombre', 'Desconocido')
                motivo = a.get('motivo_ausencia')
                ausentes_str_list.append(f"{nombre}{f' ({motivo})' if motivo else ''}")
            output.append(f"Ausentes: {', '.join(ausentes_str_list)}")
        else:
            output.append("Ausentes: Ninguno")

        # Resumen Ejecutivo
        output.append("\n--- RESUMEN EJECUTIVO ---")
        output.append(data.get('resumen_ejecutivo', 'No disponible.'))
        

        # Objetivos de la Reunión
        output.append("\n--- OBJETIVOS DE LA REUNIÓN ---")
        objetivos_list = data.get('objetivos_reunion', [])
        if objetivos_list:
            for objetivo in objetivos_list:
                output.append(f"  • {objetivo}")
        else:
            output.append("No hay objetivos de reunión identificados.")


        # Temas Discutidos y Puntos Clave
        output.append("\n--- TEMAS DISCUTIDOS Y PUNTOS CLAVE ---")
        temas_list = data.get('temas_discutidos_y_puntos_clave', [])
        if temas_list:
            for tema_item in temas_list:
                tema = tema_item.get('tema', 'N/A')
                responsable_tema = tema_item.get('responsable_tema', '')
                output.append(f"  • **{tema}** {f'(Liderado por: {responsable_tema})' if responsable_tema else ''}")
                puntos_clave = tema_item.get('puntos_clave', [])
                if puntos_clave:
                    for punto in puntos_clave:
                        output.append(f"      - {punto}")
        else:
            output.append("No hay temas discutidos identificados.")

        # Decisiones Clave Tomadas
        output.append("\n--- DECISIONES CLAVE TOMADAS ---")
        decisiones_list = data.get('decisiones_clave_tomadas', [])
        if decisiones_list:
            for decision_item in decisiones_list:
                decision = decision_item.get('decision', 'N/A')
                acordada_por = decision_item.get('acordada_por', 'No especificado')
                output.append(f"  • Decisión: {decision}\n    Acordada por: {acordada_por}")
        else:
            output.append("No hay decisiones clave identificadas.")

        # Tareas Pendientes
        output.append("\n--- TAREAS PENDIENTES ---")
        tareas_list = data.get('tareas_pendientes', [])
        if tareas_list:
            for tarea_item in tareas_list:
                tarea = tarea_item.get('tarea', 'N/A')
                responsable = tarea_item.get('responsable', 'N/A')
                fecha_limite = tarea_item.get('fecha_limite', 'N/A')
                output.append(f"  • Tarea: {tarea}\n    Responsable: {responsable}\n    Fecha Límite: {fecha_limite}")
        else:
            output.append("No hay tareas pendientes identificadas.")
            
        # Próximos Pasos o Siguiente Reunión
        output.append("\n--- PRÓXIMOS PASOS O SIGUIENTE REUNIÓN ---")
        output.append(data.get('proximos_pasos_o_siguiente_reunion', 'No especificado.'))

        # Notas Adicionales
        output.append("\n--- NOTAS ADICIONALES ---")
        output.append(data.get('notas_adicionales', 'Ninguna.'))

        # Documentos Referenciados
        output.append("\n--- DOCUMENTOS REFERENCIADOS ---")
        documentos_list = data.get('documentos_referenciados', [])
        if documentos_list:
            for doc in documentos_list:
                output.append(f"  • {doc}")
        else:
            output.append("Ninguno.")


        return "\n".join(output)

    def _export_pdf(self):
        if not hasattr(self, 'generated_meeting_data') or not self.generated_meeting_data:
            messagebox.showwarning("Advertencia", "No hay un acta generada para exportar.")
            return
        
        pdf_data = self.generated_meeting_data

        if not pdf_data: 
            messagebox.showwarning("Advertencia", "Los datos del acta generada están vacíos o no tienen el formato esperado para PDF.")
            return

        title = pdf_data.get('titulo_reunion', 'Acta_Reunion') 
        valid_filename = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
        default_filename = valid_filename.replace(" ", "_") + ".pdf"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialfile=default_filename
        )
        if file_path:
            try:
                create_meeting_minutes_pdf(pdf_data, file_path) 
                messagebox.showinfo("Éxito", f"Acta exportada a PDF: {file_path}")
            except Exception as e:
                messagebox.showerror("Error al Exportar PDF", f"Ocurrió un error al guardar el PDF: {e}")

    def _copy_to_clipboard(self):
        try:
            # Habilitar temporalmente el Text widget para copiar su contenido
            self.minutes_text.config(state=tk.NORMAL)
            text_to_copy = self.minutes_text.get(1.0, tk.END)
            # Volver a deshabilitar si no quieres que el usuario edite
            self.minutes_text.config(state=tk.DISABLED) 

            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)
            messagebox.showinfo("Copiar", "Acta copiada al portapapeles.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar al portapapeles: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MeetingMinutesApp(root)
    root.mainloop()