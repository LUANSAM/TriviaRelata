from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PIL import Image as PILImage
import os
import io
import base64
from datetime import datetime
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
CORS(app)

# Criar pastas necessárias
os.makedirs('temp_uploads', exist_ok=True)
os.makedirs('assets', exist_ok=True)

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self.footer_text = kwargs.pop('footer_text', '')
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont('Helvetica', 8)
        footer_y = 1.5 * cm
        
        # Texto do rodapé à esquerda
        self.drawString(2 * cm, footer_y, self.footer_text)
        
        # Numeração de páginas à direita
        page_num = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(A4[0] - 2 * cm, footer_y, page_num)
        
        self.restoreState()

def process_image_for_pdf(image_data):
    """Processa imagem para otimizar tamanho e qualidade"""
    try:
        # Decodificar base64
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        img = PILImage.open(io.BytesIO(image_bytes))
        
        # Converter para RGB se necessário
        if img.mode in ('RGBA', 'LA', 'P'):
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
        
        # Redimensionar se muito grande
        max_size = (800, 800)
        img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
        
        # Salvar em buffer
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return output
    except Exception as e:
        print(f"Erro ao processar imagem: {str(e)}")
        return None

def generate_pdf(data):
    """Gera o PDF com os dados fornecidos"""
    buffer = io.BytesIO()
    
    footer_text = f"Relatório emitido por: {data.get('sistema', 'Sistema')}"
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=3*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#555555'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_CENTER
    )
    
    observation_style = ParagraphStyle(
        'Observation',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    )
    
    # Cabeçalho personalizado com título e logo
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    logo_path = 'assets/logo.png'
    
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.5*cm, height=2.5*cm, kind='proportional')
        titulo_header = Paragraph("Relatório de estados", header_title_style)
        header_data = [[titulo_header, logo]]
        header_table = Table(header_data, colWidths=[14*cm, 3*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    else:
        titulo_header = Paragraph("Relatório de estados", header_title_style)
        header_data = [[titulo_header]]
        header_table = Table(header_data, colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    
    story.append(header_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Linha separadora
    line_table = Table([['']], colWidths=[17*cm], rowHeights=[0.05*cm])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e5ba8')),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Informações do relatório
    info_lines = []
    if data.get('local'):
        info_lines.append(Paragraph(f"<b>Local:</b> {data['local']}", subtitle_style))
    if data.get('sistema_ref'):
        info_lines.append(Paragraph(f"<b>Sistema:</b> {data['sistema_ref']}", subtitle_style))
    if data.get('data'):
        info_lines.append(Paragraph(f"<b>Data:</b> {data['data']}", subtitle_style))
    
    for line in info_lines:
        story.append(line)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Título do relatório
    if data.get('titulo'):
        story.append(Paragraph(data['titulo'], title_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Adicionar fotos e observações
    fotos = data.get('fotos', [])
    
    for idx, foto in enumerate(fotos):
        try:
            img_buffer = process_image_for_pdf(foto['imagem'])
            if img_buffer:
                img = Image(img_buffer, width=8*cm, height=6*cm, kind='proportional')
                observacao = Paragraph(foto.get('observacao', ''), observation_style)
                
                # Criar tabela com imagem e observação
                foto_table = Table([[img, observacao]], colWidths=[8.5*cm, 8.5*cm])
                foto_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                
                story.append(foto_table)
                
                # Adicionar separador após cada foto (exceto a última)
                if idx < len(fotos) - 1:
                    story.append(Spacer(1, 0.3*cm))
                    separator = Table([['']], colWidths=[17*cm], rowHeights=[0.02*cm])
                    separator.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e2e8f0')),
                    ]))
                    story.append(separator)
                    story.append(Spacer(1, 0.5*cm))
                else:
                    story.append(Spacer(1, 0.8*cm))
                
                # Adicionar quebra de página a cada 2 fotos (exceto na última)
                if (idx + 1) % 2 == 0 and idx < len(fotos) - 1:
                    story.append(PageBreak())
        except Exception as e:
            print(f"Erro ao adicionar foto {idx}: {str(e)}")
            continue
    
    # Gerar PDF
    doc.build(story, canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, footer_text=footer_text, **kwargs))
    
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gerar-pdf', methods=['POST'])
def gerar_pdf():
    try:
        data = request.get_json()
        
        # Validações
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        if not data.get('fotos') or len(data['fotos']) == 0:
            return jsonify({'error': 'Nenhuma foto fornecida'}), 400
        
        # Validar número de fotos
        if len(data['fotos']) > 50:
            return jsonify({'error': 'Máximo de 50 fotos por relatório'}), 400
        
        # Gerar PDF
        pdf_buffer = generate_pdf(data)
        
        # Retornar PDF
        filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        return jsonify({'error': 'Erro ao gerar PDF', 'details': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'logo_exists': os.path.exists('assets/logo.png')})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("RELATÓRIO FOTOGRÁFICO - TRIVIA TRENS")
    print("=" * 60)
    print(f"\n✓ Servidor iniciado")
    print(f"✓ Porta: {port}")
    print(f"✓ Debug: {debug}")
    print(f"\n⚠ IMPORTANTE: Coloque o logo da empresa em: assets/logo.png")
    print(f"   (Formatos aceitos: PNG, JPG)")
    print("=" * 60)
    app.run(debug=debug, host='0.0.0.0', port=port)
