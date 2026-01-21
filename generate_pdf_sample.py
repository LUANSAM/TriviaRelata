from app import generate_pdf

sample_data = {
    "titulo": "Relatorio de Auditoria - Estacao Jose Bonifacio",
    "local": "Estacao Jose Bonifacio",
    "sistema_ref": "SA",
    "data": "12/01/2026",
    "sistema": "Trivia Trens",
    "fotos": []
}

buffer = generate_pdf(sample_data)
output_path = "test_header.pdf"
with open(output_path, "wb") as pdf_file:
    pdf_file.write(buffer.getbuffer())

print(f"PDF gerado em: {output_path}")
