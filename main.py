import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from dotenv import load_dotenv
import traceback

# --- ¡IMPORTACIÓN AÑADIDA! ---
import ollama
# -----------------------------

# Cargar variables de entorno del archivo .env al inicio
load_dotenv()

# Importar funciones de los otros módulos
from audio_processor import transcribe_audio
from llm_processor import generate_minutes
from pdf_generator import create_meeting_minutes_pdf

# --- LISTA DE MODELOS ACTUALIZADA ---
CLOUD_MODELS = {
    "OpenAI": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
    "Google": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro"]
}

class MeetingMinutesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Acta de Reunión Inteligente")
        self.root.geometry("1000x800")

        self.audio_file_path = None
        self.ollama_models = []
        
        self._create_widgets()
        self.root.after(100, self._on_provider_select)

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Sección 1: Configuración ---
        config_frame = ttk.LabelFrame(main_frame, text="1. Configuración", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        config_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(config_frame, text="Proveedor LLM:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.provider_var = tk.StringVar()
        self.provider_combobox = ttk.Combobox(config_frame, textvariable=self.provider_var, values=["Ollama", "OpenAI", "Anthropic", "Google"], state="readonly")
        self.provider_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.provider_combobox.set("Ollama")
        self.provider_combobox.bind("<<ComboboxSelected>>", self._on_provider_select)
        
        ttk.Label(config_frame, text="Modelo:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky=tk.W)
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(config_frame, textvariable=self.model_var, state="readonly")
        self.model_combobox.grid(row=0, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # --- Sección 2: Flujo de Trabajo ---
        workflow_frame = ttk.LabelFrame(main_frame, text="2. Flujo de Trabajo", padding="10")
        workflow_frame.pack(fill=tk.X, padx=5, pady=5)
        workflow_frame.grid_columnconfigure(1, weight=3)
        workflow_frame.grid_columnconfigure(2, weight=1)

        # Botón de Transcripción
        ttk.Label(workflow_frame, text="Paso 1:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.transcribe_button = ttk.Button(workflow_frame, text="Transcribir Audio", command=self._start_transcription, state=tk.DISABLED)
        self.transcribe_button.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.file_path_label = ttk.Label(workflow_frame, text="Ningún archivo seleccionado.")
        self.file_path_label.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        browse_button = ttk.Button(workflow_frame, text="Examinar Archivo...", command=self._browse_file)
        browse_button.grid(row=0, column=3, padx=5, pady=5)

        # Botón de Generación de Acta
        ttk.Label(workflow_frame, text="Paso 2:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.generate_from_text_button = ttk.Button(workflow_frame, text="Generar Acta desde Texto", command=self._start_generation, state=tk.DISABLED)
        self.generate_from_text_button.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # --- Sección 3: Transcripción y Acta ---
        output_frame = ttk.LabelFrame(main_frame, text="3. Transcripción / Acta Generada (Editable)", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_label = ttk.Label(output_frame, text="Estado: Seleccione un archivo para comenzar.", foreground="blue")
        self.status_label.pack(fill=tk.X, pady=5)

        text_scroll = ttk.Scrollbar(output_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_text = tk.Text(output_frame, wrap=tk.WORD, font=("Arial", 10), yscrollcommand=text_scroll.set)
        self.main_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_scroll.config(command=self.main_text.yview)

        action_buttons_frame = ttk.Frame(output_frame)
        action_buttons_frame.pack(pady=5)

        self.export_pdf_button = ttk.Button(action_buttons_frame, text="Exportar a PDF", command=self._export_pdf, state=tk.DISABLED)
        self.export_pdf_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = ttk.Button(action_buttons_frame, text="Copiar al Portapapeles", command=self._copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=5)

    def _on_provider_select(self, event=None):
        provider = self.provider_var.get()
        self.model_var.set('')
        
        if provider == "Ollama":
            try:
                client = ollama.Client(host=os.environ.get('OLLAMA_HOST', 'http://localhost:11434'))
                models_info = client.list()
                self.ollama_models = [m.model for m in models_info['models']]
                self.model_combobox['values'] = self.ollama_models
                if self.ollama_models:
                    self.model_var.set(self.ollama_models[0])
                else:
                    self.model_var.set("No hay modelos Ollama")
            except Exception as e:
                self.model_combobox['values'] = []
                self.model_var.set("Error de conexión")
                messagebox.showerror("Error de Ollama", f"No se pudo conectar a Ollama: {e}")
        else:
            api_key_name = f"{provider.upper()}_API_KEY"
            if not os.getenv(api_key_name):
                 messagebox.showwarning("API Key Faltante", f"La clave API para {provider} no se encontró en el archivo .env ({api_key_name}).")
                 self.model_combobox['values'] = []
            else:
                self.model_combobox['values'] = CLOUD_MODELS.get(provider, [])
                if self.model_combobox['values']:
                    self.model_var.set(self.model_combobox['values'][0])
    
    def _browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de Audio/Video", "*.mp4 *.mp3 *.wav *.m4a"), ("Todos los Archivos", "*.*")])
        if file_path:
            self.audio_file_path = file_path
            self.file_path_label.config(text=os.path.basename(file_path))
            self.transcribe_button.config(state=tk.NORMAL)
            self.generate_from_text_button.config(state=tk.DISABLED)

    def _start_transcription(self):
        if not self.audio_file_path:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un archivo primero.")
            return
        self._reset_ui_for_processing("Transcribiendo...")
        threading.Thread(target=self._transcribe_task).start()

    def _start_generation(self):
        if not self.main_text.get("1.0", tk.END).strip():
            messagebox.showwarning("Advertencia", "No hay texto en la ventana para generar el acta.")
            return
        self._reset_ui_for_processing("Generando acta...")
        threading.Thread(target=self._generate_task).start()

    def _transcribe_task(self):
        try:
            transcription = transcribe_audio(self.audio_file_path)
            
            def update_gui_success():
                self.main_text.delete(1.0, tk.END)
                self.main_text.insert(tk.END, transcription)
                self.status_label.config(text="Estado: Transcripción completa. Puede editar el texto y luego generar el acta.", foreground="green")
                self.generate_from_text_button.config(state=tk.NORMAL)
            
            self.root.after(0, update_gui_success)

        except Exception as e:
            def update_gui_error():
                messagebox.showerror("Error de Transcripción", f"Ocurrió un error: {e}")
                self.status_label.config(text=f"Estado: Error de transcripción.", foreground="red")
            
            self.root.after(0, update_gui_error)
            traceback.print_exc()
        finally:
            self.root.after(0, self._revert_ui_after_processing)
    
    def _generate_task(self):
        try:
            provider = self.provider_var.get()
            model_name = self.model_var.get()
            transcription_text = self.main_text.get("1.0", tk.END).strip()
            user_context = "" # El contexto ahora se maneja en el prompt, esta variable puede eliminarse o usarse de otra forma
            
            params = { "temperature": 0.5, "num_predict": 8192, "num_ctx": 16384 }
            
            acta_markdown = generate_minutes(provider, model_name, transcription_text, user_context, params)
            
            def update_gui_success():
                self.main_text.delete(1.0, tk.END)
                self.main_text.insert(tk.END, acta_markdown)
                self.export_pdf_button.config(state=tk.NORMAL)
                self.copy_button.config(state=tk.NORMAL)
                self.status_label.config(text="Estado: Acta generada. Puede editarla antes de exportar.", foreground="green")

            self.root.after(0, update_gui_success)

        except Exception as e:
            def update_gui_error():
                messagebox.showerror("Error de Generación", f"Ocurrió un error: {e}")
                self.status_label.config(text=f"Estado: Error de generación.", foreground="red")
            
            self.root.after(0, update_gui_error)
            traceback.print_exc()
        finally:
            self.root.after(0, self._revert_ui_after_processing)

    def _reset_ui_for_processing(self, message):
        self.status_label.config(text=f"Estado: {message}", foreground="orange")
        self.transcribe_button.config(state=tk.DISABLED)
        self.generate_from_text_button.config(state=tk.DISABLED)
        self.export_pdf_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)

    def _revert_ui_after_processing(self):
        if self.audio_file_path:
            self.transcribe_button.config(state=tk.NORMAL)
        if self.main_text.get("1.0", tk.END).strip():
            self.generate_from_text_button.config(state=tk.NORMAL)
        
    def _export_pdf(self):
        markdown_content = self.main_text.get("1.0", tk.END)
        if not markdown_content.strip():
            messagebox.showwarning("Advertencia", "No hay contenido para exportar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")], initialfile="Acta_de_Reunion.pdf")
        if file_path:
            try:
                create_meeting_minutes_pdf(markdown_content, file_path)
                messagebox.showinfo("Éxito", "Acta exportada a PDF con éxito.")
            except Exception as e:
                messagebox.showerror("Error al Exportar PDF", f"Ocurrió un error: {e}")

    def _copy_to_clipboard(self):
        texto_acta = self.main_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto_acta)
        messagebox.showinfo("Copiado", "El contenido ha sido copiado al portapapeles.")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MeetingMinutesApp(root)
        root.mainloop()
    except Exception as e:
        print("--- ERROR FATAL ---")
        traceback.print_exc()
        input("Presiona Enter para cerrar...")