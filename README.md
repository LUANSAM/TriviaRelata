# 📋 Relatório Fotográfico - Trivia Trens

Sistema web para geração de relatórios fotográficos em PDF com design moderno e tema escuro.

## 🚀 Características

- ✅ Interface web moderna com tema escuro
- ✅ Design inspirado em dashboard profissional
- ✅ Cores da identidade Trivia (ciano/turquesa)
- ✅ Upload múltiplo de fotos (até 50 por relatório)
- ✅ Drag and drop de imagens
- ✅ Modal popup para adicionar fotos (FAB no canto inferior direito)
- ✅ Grid responsivo de cards para visualização
- ✅ Preview das fotos em tempo real
- ✅ Observações personalizadas para cada foto
- ✅ Geração de PDF profissional com:
  - Cabeçalho customizado "Relatório de estados" com logo
  - Separadores entre imagens
  - Informações do relatório (local, sistema, data)
  - Fotos e observações lado a lado
  - Rodapé com sistema emissor e numeração de páginas
- ✅ Processamento assíncrono para não travar a página
- ✅ Validações de segurança
- ✅ Otimização automática de imagens

## 📋 Requisitos

- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone ou baixe este repositório**

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Adicione o logo da empresa:**
   - Coloque o arquivo de logo em: `assets/logo.png`
   - Formatos aceitos: PNG, JPG
   - Tamanho recomendado: 300x300 pixels

## ▶️ Como Usar

1. **Inicie o servidor:**
```bash
python app.py
```

2. **Acesse no navegador:**
```
http://localhost:5000
```

3. **Preencha os dados do relatório:**
   - Título do relatório
   - Local
   - Sistema de referência
   - Data
   - Sistema emissor

4. **Adicione fotos:**
   - Clique no FAB (botão flutuante ciano) no canto inferior direito
   - Arraste fotos para o modal ou clique para selecionar
   - Escreva observações para cada foto

5. **Gere o PDF:**
   - Clique em "Gerar PDF"
   - O arquivo será baixado automaticamente

6. **Reinicie quando necessário:**
   - Clique em "Reiniciar Relatório" para limpar todos os dados

## 🌐 Deploy em Produção

O app está configurado para deploy em plataformas gratuitas:

### Render (Recomendado)
1. Acesse https://render.com e crie uma conta
2. Clique em "New +" → "Web Service"
3. Conecte o repositório `LUANSAM/TriviaRelata`
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Deploy! URL: `https://trivia-relata.onrender.com`

### Railway
1. Acesse https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Selecione `TriviaRelata`
4. Deploy automático!

### Vercel
1. Acesse https://vercel.com
2. Import `TriviaRelata`
3. Deploy!

## 🔒 Segurança

- Validação de tipo de arquivo (apenas imagens)
- Limite de tamanho por foto (10MB)
- Limite total de fotos (50 por relatório)
- Sanitização de nomes de arquivo
- Proteção CSRF integrada
- Sem armazenamento permanente de dados sensíveis

## 📂 Estrutura do Projeto

```
relatorio-fotografico/
├── app.py                  # Aplicação principal Flask
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
├── assets/                # Recursos (logo)
│   └── logo.png          # [ADICIONE SEU LOGO AQUI]
├── templates/             # Templates HTML
│   └── index.html
├── static/                # Arquivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos da aplicação
│   └── js/
│       └── app.js        # Lógica frontend
└── temp_uploads/          # [Criado automaticamente]
```

## 🎨 Personalização

### Alterar cores da interface
Edite as variáveis CSS em `static/css/style.css`:
```css
:root {
    --primary-color: #00d9b8;  /* Ciano/Turquesa */
    --bg-dark: #0f1117;        /* Fundo escuro */
    /* ... outras cores ... */
}
```

### Ajustar layout do PDF
Modifique a função `generate_pdf()` em `app.py`

### Alterar limites
Em `app.py`:
- `MAX_CONTENT_LENGTH`: tamanho máximo total (padrão: 50MB)
- No frontend (`app.js`): limite de fotos (padrão: 50)

## ❗ Solução de Problemas

### O logo não aparece no PDF
- Verifique se o arquivo está em `assets/logo.png`
- Certifique-se que o formato é PNG ou JPG
- Teste com uma imagem menor (< 1MB)

### Erro ao gerar PDF
- Verifique se todas as dependências estão instaladas
- Confirme que há espaço em disco suficiente
- Tente com menos fotos ou fotos menores

### Página lenta com muitas fotos
- Reduza o tamanho das fotos antes do upload
- Limite-se a 20-30 fotos por relatório para melhor performance

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Geração de PDF:** ReportLab
- **Processamento de Imagens:** Pillow
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Segurança:** Flask-CORS, Werkzeug

## 📝 Licença

Este projeto é de uso interno da Trivia Trens.

## 👨‍💻 Desenvolvimento

Para modo de desenvolvimento com auto-reload:
```bash
python app.py
```

O servidor reinicia automaticamente quando detecta mudanças nos arquivos.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de solução de problemas
2. Consulte os logs no terminal
3. Contate o administrador do sistema
=======
# Trivia
>>>>>>> c9b0820a260c6161e437bf5510ad7cdfb781aa8a
