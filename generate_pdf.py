from weasyprint import HTML

def generate_pdf_for_worker(worker_id, output_path, result_text=None):
    """
    Genereert een PDF voor een DIMONA resultaat.
    Als result_text is meegegeven, wordt die gebruikt.
    """
    # Simpele HTML template
    html_content = f"""
    <html>
    <head><meta charset="UTF-8"><title>DIMONA Resultaat</title></head>
    <body>
        <h1>DIMONA Resultaat</h1>
        <p>Werknemer ID: {worker_id}</p>
        <div>
            {result_text or 'Resultaat niet beschikbaar'}
        </div>
    </body>
    </html>
    """

    HTML(string=html_content).write_pdf(output_path)
