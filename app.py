from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Line
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
    print("\n" + "="*60)
    print("INICIANDO GERAÇÃO DE PDF")
    print("="*60)
    
    buffer = io.BytesIO()
    
    footer_text = f"Relatório emitido por: {data.get('sistema', 'Sistema')}"
    print(f"[LOG] Footer: {footer_text}")
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=2*cm
    )
    print("[LOG] SimpleDocTemplate criado")
    
    story = []
    styles = getSampleStyleSheet()
    print("[LOG] Estilos carregados")
    
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
        fontSize=10,
        textColor=colors.HexColor('#000000'),
        spaceAfter=2,
        alignment=TA_LEFT
    )
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#000000'),
        spaceAfter=12,
        spaceBefore=10,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    observation_style = ParagraphStyle(
        'Observation',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    )
    
    # CABEÇALHO COM LINHAS COLORIDAS E LOGO
    header_lines_height = 0.5*cm
    lines_drawing = Drawing(19*cm, header_lines_height)
    
    def add_colored_line(y_pos, length, hex_color):
        line = Line(0, y_pos, length, y_pos)
        line.strokeColor = colors.HexColor(hex_color)
        line.strokeWidth = 2.5
        line.strokeLineCap = 1  # rounded ends for smoother finish
        lines_drawing.add(line)
    
    add_colored_line(header_lines_height - 0.02*cm, 19*cm, '#F26A21')   # Laranja superior
    add_colored_line(header_lines_height - 0.16*cm, 17*cm, '#2E3192')   # Roxo central (encurtada)
    add_colored_line(header_lines_height - 0.30*cm, 12*cm, '#1FB44F')   # Verde inferior
    
    story.append(lines_drawing)
    story.append(Spacer(1, 0.25*cm))
    
    # Logo e título na mesma linha
    logo_path = 'assets/logo.png'
    
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=3.0*cm, height=3.0*cm, kind='proportional')
        titulo_relatorio = data.get('titulo', '')
        titulo_para = Paragraph(f"<b>{titulo_relatorio}</b>", title_style)
        
        header_data = [[titulo_para, logo]]
        header_table = Table(header_data, colWidths=[15*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
    else:
        titulo_relatorio = data.get('titulo', '')
        titulo_para = Paragraph(f"<b>{titulo_relatorio}</b>", title_style)
        header_data = [[titulo_para]]
        header_table = Table(header_data, colWidths=[19*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
    
    story.append(header_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Informações: Data, Local, Sistema
    info_data = []
    
    if data.get('data'):
        info_data.append([Paragraph(f"<b>Data:</b> {data['data']}", subtitle_style)])
    
    if data.get('local'):
        info_data.append([Paragraph(f"<b>Local:</b> {data['local']}", subtitle_style)])
    
    if data.get('sistema_ref'):
        info_data.append([Paragraph(f"<b>Sistema:</b> {data['sistema_ref']}", subtitle_style)])
    
    if info_data:
        info_table = Table(info_data, colWidths=[19*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(info_table)
    
    story.append(Spacer(1, 0.5*cm))

    
    # Adicionar fotos e observações
    fotos = data.get('fotos', [])
    print(f"\n[LOG] Total de fotos para processar: {len(fotos)}")
    
    for idx, foto in enumerate(fotos):
        print(f"\n[LOG] --- PROCESSANDO FOTO {idx + 1}/{len(fotos)} ---")
        try:
            print(f"[LOG] Chamando process_image_for_pdf...")
            img_buffer = process_image_for_pdf(foto['imagem'])
            print(f"[LOG] Buffer da imagem: {img_buffer}")
            
            if img_buffer:
                print(f"[LOG] Buffer válido, criando Image object...")
                # Garantir que o ponteiro do buffer esteja no início
                img_buffer.seek(0)
                # Imagem com dimensões: 6cm x 5cm
                img = Image(img_buffer, width=6*cm, height=5*cm)
                print(f"[LOG] Image object criado: {img}")
                
                # Observação
                obs_text = foto.get('observacao', 'Sem observações')
                print(f"[LOG] Observação: {obs_text[:50]}...")
                obs_para = Paragraph(obs_text, observation_style)
                print(f"[LOG] Paragraph criado")
                
                # Tabela com imagem e observação lado a lado
                print(f"[LOG] Criando tabela com imagem e observação...")
                foto_data = [[img, obs_para]]
                foto_table = Table(foto_data, colWidths=[6.5*cm, 12.5*cm])
                foto_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('LEFTPADDING', (1, 0), (1, 0), 0.5*cm),
                    ('RIGHTPADDING', (0, 0), (0, 0), 0.2*cm),
                ]))
                print(f"[LOG] Tabela criada, adicionando à story...")
                
                story.append(foto_table)
                print(f"[LOG] ✓ Foto {idx + 1} ADICIONADA COM SUCESSO")
                print(f"[LOG] Story agora tem {len(story)} elementos")
                
                # Espaço entre fotos
                if idx < len(fotos) - 1:
                    story.append(Spacer(1, 0.5*cm))
                    print(f"[LOG] Espaçador adicionado")
            else:
                print(f"[LOG] ✗ ERRO: Buffer de imagem é nulo!")
                
        except Exception as e:
            print(f"\n[LOG] ✗ ERRO na foto {idx + 1}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            continue
    
    print(f"\n[LOG] Total de elementos na story: {len(story)}")
    
    # Gerar PDF
    print(f"\n[LOG] Iniciando build do PDF com {len(story)} elementos...")
    doc.build(story, canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, footer_text=footer_text, **kwargs))
    print("[LOG] ✓ PDF buildado com sucesso")
    
    buffer.seek(0)
    print(f"[LOG] Buffer pronto, tamanho: {buffer.getbuffer().nbytes} bytes")
    print("="*60)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gerar-pdf', methods=['POST'])
def gerar_pdf():
    try:
        print("=== Iniciando geração de PDF ===")
        data = request.get_json()
        print(f"Dados recebidos: {len(data.get('fotos', []))} fotos")
        
        # Validações
        if not data:
            print("ERRO: Dados não fornecidos")
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        if not data.get('fotos') or len(data['fotos']) == 0:
            print("ERRO: Nenhuma foto fornecida")
            return jsonify({'error': 'Nenhuma foto fornecida'}), 400
        
        # Validar número de fotos
        if len(data['fotos']) > 50:
            print("ERRO: Muitas fotos")
            return jsonify({'error': 'Máximo de 50 fotos por relatório'}), 400
        
        # Garantir que o diretório temp existe
        os.makedirs('temp_uploads', exist_ok=True)
        print("Diretório temp_uploads verificado")
        
        # Gerar PDF
        print("Gerando PDF...")
        pdf_buffer = generate_pdf(data)
        print("PDF gerado com sucesso")
        
        # Retornar PDF
        filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        print(f"Enviando arquivo: {filename}")
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERRO CRÍTICO ao gerar PDF:")
        print(error_details)
        return jsonify({
            'error': 'Erro ao gerar PDF', 
            'details': str(e),
            'type': type(e).__name__
        }), 500

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
