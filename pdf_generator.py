from fpdf import FPDF # Usaremos PyFPDF por simplicidad
import os

class PDF(FPDF):
    def header(self):
        # Puedes añadir un logo aquí (opcional)
        # self.image('logo.png', 10, 8, 33) 
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Acta de Reunión', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230) # Fondo gris claro para los títulos
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        # Manejar posibles caracteres especiales o saltos de línea para que multi_cell funcione bien
        body = str(body).replace('\r\n', '\n').replace('\r', '\n')
        self.multi_cell(0, 6, body)
        self.ln(5)
    
    def add_list_item(self, item_text, indent=0):
        self.set_font('Arial', '', 10)
        # Eliminar las negritas si el LLM las genera y PyFPDF no las procesa
        item_text = str(item_text).replace('**', '') 
        self.multi_cell(0, 6, "  " * indent + f'• {item_text}')


def create_meeting_minutes_pdf(meeting_data: dict, output_filepath: str):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15) # Margen para saltos de página

    # Información general
    pdf.set_font('Arial', '', 10)
    
    pdf.multi_cell(0, 6, f"Título de la Reunión: {meeting_data.get('titulo_reunion', 'N/A')}")
    pdf.multi_cell(0, 6, f"Fecha: {meeting_data.get('fecha_reunion', 'N/A')} | Hora: {meeting_data.get('hora_inicio', 'N/A')} - {meeting_data.get('hora_fin', 'N/A')}")
    pdf.multi_cell(0, 6, f"Ubicación: {meeting_data.get('ubicacion', 'N/A')}")
    
    # Participantes
    participantes_list = meeting_data.get('participantes', [])
    if participantes_list:
        participantes_str_list = []
        for p in participantes_list:
            nombre = p.get('nombre', 'Desconocido')
            rol = p.get('rol')
            participantes_str_list.append(f"{nombre}{f' ({rol})' if rol and rol != 'No especificado' else ''}")
        pdf.multi_cell(0, 6, f"Participantes: {', '.join(participantes_str_list)}")
    else:
        pdf.multi_cell(0, 6, "Participantes: No identificados")

    # Ausentes
    ausentes_list = meeting_data.get('ausentes', [])
    if ausentes_list:
        ausentes_str_list = []
        for a in ausentes_list:
            nombre = a.get('nombre', 'Desconocido')
            motivo = a.get('motivo_ausencia')
            ausentes_str_list.append(f"{nombre}{f' ({motivo})' if motivo else ''}")
        pdf.multi_cell(0, 6, f"Ausentes: {', '.join(ausentes_str_list)}")
    else:
        pdf.multi_cell(0, 6, "Ausentes: Ninguno")
    pdf.ln(5)

    # Resumen Ejecutivo
    pdf.chapter_title('Resumen Ejecutivo')
    pdf.chapter_body(meeting_data.get('resumen_ejecutivo', 'No disponible.'))
    pdf.ln(5)

    # Objetivos de la Reunión
    pdf.chapter_title('Objetivos de la Reunión')
    objetivos_list = meeting_data.get('objetivos_reunion', [])
    if objetivos_list:
        for objetivo in objetivos_list:
            pdf.add_list_item(objetivo)
    else:
        pdf.chapter_body('No hay objetivos de reunión identificados.')
    pdf.ln(5)

    # Temas Discutidos y Puntos Clave
    pdf.chapter_title('Temas Discutidos y Puntos Clave')
    temas_list = meeting_data.get('temas_discutidos_y_puntos_clave', [])
    if temas_list:
        for tema_item in temas_list:
            tema = tema_item.get('tema', 'N/A')
            responsable_tema = tema_item.get('responsable_tema', '')
            pdf.add_list_item(f"**{tema}** {f'(Liderado por: {responsable_tema})' if responsable_tema else ''}", indent=0)
            puntos_clave = tema_item.get('puntos_clave', [])
            if puntos_clave:
                for punto in puntos_clave:
                    pdf.add_list_item(punto, indent=1)
    else:
        pdf.chapter_body('No hay temas discutidos identificados.')
    pdf.ln(5)

    # Decisiones Clave Tomadas
    pdf.chapter_title('Decisiones Clave Tomadas')
    decisiones_list = meeting_data.get('decisiones_clave_tomadas', [])
    if decisiones_list:
        for decision_item in decisiones_list:
            decision = decision_item.get('decision', 'N/A')
            acordada_por = decision_item.get('acordada_por', 'No especificado')
            pdf.add_list_item(f"Decisión: {decision} (Acordada por: {acordada_por})")
    else:
        pdf.chapter_body('No hay decisiones clave identificadas.')
    pdf.ln(5)

    # Tareas Pendientes
    pdf.chapter_title('Tareas Pendientes')
    tareas_list = meeting_data.get('tareas_pendientes', [])
    if tareas_list:
        for tarea_item in tareas_list:
            tarea = tarea_item.get('tarea', 'N/A')
            responsable = tarea_item.get('responsable', 'N/A')
            fecha_limite = tarea_item.get('fecha_limite', 'N/A')
            pdf.add_list_item(f"Tarea: {tarea} (Responsable: {responsable}) (Fecha Límite: {fecha_limite})")
    else:
        pdf.chapter_body('No hay tareas pendientes identificadas.')
    pdf.ln(5)
    
    # Próximos Pasos o Siguiente Reunión
    pdf.chapter_title('Próximos Pasos o Siguiente Reunión')
    pdf.chapter_body(meeting_data.get('proximos_pasos_o_siguiente_reunion', 'No especificado.'))
    pdf.ln(5)
    
    # Notas Adicionales
    pdf.chapter_title('Notas Adicionales')
    pdf.chapter_body(meeting_data.get('notas_adicionales', 'Ninguna.'))
    pdf.ln(5)

    # Documentos Referenciados
    pdf.chapter_title('Documentos Referenciados')
    documentos_list = meeting_data.get('documentos_referenciados', [])
    if documentos_list:
        for doc in documentos_list:
            pdf.add_list_item(doc)
    else:
        pdf.chapter_body('Ninguno.')
    pdf.ln(5)

    pdf.output(output_filepath)

if __name__ == '__main__':
    # Ejemplo de uso (esto no se ejecutará en la app principal)
    # ESTE EJEMPLO DEBE COINCIDIR CON LA ÚLTIMA SALIDA REAL DE TU LLM PARA PRUEBAS DEL PDF
    ejemplo_data = {
      "titulo_reunion": "Revisión de Políticas de Seguridad Q3",
      "fecha_reunion": "No especificada",
      "hora_inicio": "No especificada",
      "hora_fin": "No especificada",
      "ubicacion": "No especificada",
      "participantes": [
        {
          "nombre": "Alex",
          "rol": "Administrador"
        },
        {
          "nombre": "Jenny",
          "rol": "No especificado"
        }
      ],
      "ausentes": [],
      "resumen_ejecutivo": "La reunión se centró en la implementación de políticas de seguridad para dispositivos, incluyendo la revisión de requisitos de integridad del código, el uso de TPM y la creación de políticas de cumplimiento. Se acordó posponer la implementación completa para la semana del lunes y continuar revisando las políticas.",
      "objetivos_reunion": [
        "Evaluar la viabilidad de implementar políticas de seguridad para dispositivos móviles y de escritorio.",
        "Determinar los requisitos mínimos de seguridad para garantizar la integridad del código y la protección de datos."
      ],
      "temas_discutidos_y_puntos_clave": [
        {
          "tema": "Integridad del Código y TPM",
          "puntos_clave": [
            "Se discutió la necesidad de garantizar la integridad del código ejecutado.",
            "Se exploró el uso de TPM (Trusted Platform Module) para verificar la integridad del sistema y bloquear el acceso a claves de cifrado en caso de detección de cambios no autorizados.",
            "Se determinó que el uso de TPM requiere hardware compatible (bios/wifi)."
          ],
          "responsable_tema": "Alex"
        },
        {
          "tema": "Políticas de Cumplimiento",
          "puntos_clave": [
            "Se acordó crear una política de cumplimiento basada en un script que identifique los dispositivos que cumplen con los requisitos mínimos de seguridad.",
            "Se discutió la necesidad de una interfaz que muestre claramente los dispositivos que cumplen y los que no, para facilitar la acción correctiva.",
            "Se identificó la importancia de definir un nivel de cumplimiento mínimo."
          ],
          "responsable_tema": "Jenny"
        },
        {
          "tema": "Microsoft Defender y Bitlocker",
          "puntos_clave": [
            "Se discutió la implementación de Microsoft Defender.",
            "Se mencionó la necesidad de verificar la versión mínima de Defender (ej: 8.5).",
            "Se identificó la necesidad de documentar las versiones y configuraciones."
          ],
          "responsable_tema": "Alex"
        }
      ],
      "decisiones_clave_tomadas": [
        {
          "decision": "Se pospondrá la implementación completa de las políticas de seguridad para la semana del lunes.",
          "acordada_por": "Alex y Jenny"
        },
        {
          "decision": "Se creará una política de cumplimiento basada en un script.",
          "acordada_por": "Alex y Jenny"
        }
      ],
      "tareas_pendientes": [
        {
          "tarea": "Crear un script para la política de cumplimiento.",
          "responsable": "Alex",
          "fecha_limite": "No especificada"
        },
        {
          "tarea": "Documentar las versiones y configuraciones de Microsoft Defender",
          "responsable": "Alex",
          "fecha_limite": "No especificada"
        }
      ],
      "proximos_pasos_o_siguiente_reunion": "La próxima reunión está programada para la semana del lunes para revisar el script de cumplimiento y discutir los resultados.",
      "notas_adicionales": "Se identificó la necesidad de una interfaz de usuario clara para la política de cumplimiento. Se enfatizó la importancia de la documentación y el seguimiento de las configuraciones de seguridad.",
      "documentos_referenciados": []
    }

    # print("Generando PDF de ejemplo...")
    # try:
    #     create_meeting_minutes_pdf(ejemplo_data, "acta_ejemplo.pdf")
    #     print("PDF de ejemplo generado: acta_ejemplo.pdf")
    # except Exception as e:
    #     print(f"Error al generar PDF: {e}")
    pass