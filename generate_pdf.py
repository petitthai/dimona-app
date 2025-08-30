# generate_pdf.py
import pdfkit

# Optioneel: geef het pad naar wkhtmltopdf expliciet op
# Op Windows kun je bijvoorbeeld iets als dit gebruiken:
# config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
# Als wkhtmltopdf in PATH staat, kun je het config-argument weglaten.
WKHTMLTOPDF_PATH = r"C:\Users\jeroe\OneDrive\Documents\DimApp\dimona-app\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)


def generate_pdf_for_worker(html_content: str, output_filename: str):
    """
    Genereert een PDF van de gegeven HTML-content en slaat deze op.
    
    :param html_content: De HTML die je wilt omzetten naar PDF
    :param output_filename: Bestandsnaam van de PDF die wordt aangemaakt
    """
    try:
        pdfkit.from_string(html_content, output_filename)  # , configuration=config)
        print(f"PDF succesvol aangemaakt: {output_filename}")
    except Exception as e:
        print(f"Fout bij genereren PDF: {e}")
        raise

