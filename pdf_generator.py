from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        """Define el encabezado del PDF."""
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Acta de Reunión', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        """Define el pie de página del PDF."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def create_meeting_minutes_pdf(markdown_text: str, output_filepath: str):
    """
    Crea un PDF a partir de un texto en formato Markdown.
    """
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Es crucial usar una fuente que soporte UTF-8 para manejar caracteres especiales
    # como tildes, eñes, etc., que son comunes en español.
    try:
        # Intenta añadir la fuente DejaVu. Debes tener el archivo .ttf en la misma carpeta
        # o en una ruta conocida por FPDF.
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 11)
    except RuntimeError:
        print("ADVERTENCIA: No se encontró la fuente DejaVuSans.ttf. Usando Arial.")
        print("Los caracteres especiales podrían no mostrarse correctamente.")
        print("Descarga la fuente desde: https://dejavu-fonts.github.io/")
        pdf.set_font('Arial', '', 10)

    # Usar la funcionalidad de Markdown de FPDF2
    try:
        pdf.write_markdown(markdown_text)
    except Exception as e:
        print(f"Error al procesar Markdown para el PDF: {e}")
        # Si falla el Markdown, lo escribimos como texto plano como respaldo.
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, markdown_text)
    
    pdf.output(output_filepath)