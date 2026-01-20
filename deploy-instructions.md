# Instruções de Deploy - TriviaRelata

## Passo 1: Criar repositório no GitHub
1. Acesse: https://github.com/new
2. Nome do repositório: `TriviaRelata`
3. **NÃO** marque "Initialize this repository with a README"
4. Clique em "Create repository"

## Passo 2: Conectar ao GitHub
Execute no terminal:
```powershell
git remote add origin https://github.com/SEU-USUARIO/TriviaRelata.git
git branch -M main
git push -u origin main
```

## Passo 3: Deploy no Render (Recomendado - Grátis)

### Opção A - Via Dashboard Render
1. Acesse: https://render.com (crie conta gratuita)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub "TriviaRelata"
4. Configure:
   - **Name**: trivia-relata
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free
5. Clique em "Create Web Service"
6. Aguarde o deploy (3-5 minutos)
7. Acesse a URL fornecida (ex: https://trivia-relata.onrender.com)

### Opção B - Via Railway (Alternativa)
1. Acesse: https://railway.app (crie conta gratuita)
2. Clique em "New Project" → "Deploy from GitHub repo"
3. Selecione "TriviaRelata"
4. Railway detectará automaticamente que é Python
5. A aplicação estará disponível em poucos minutos

### Opção C - Via Vercel (Alternativa)
1. Acesse: https://vercel.com (crie conta gratuita)
2. Clique em "Add New" → "Project"
3. Importe o repositório "TriviaRelata"
4. Configure:
   - **Framework Preset**: Other
   - **Build Command**: deixe vazio
   - **Output Directory**: deixe vazio
5. Clique em "Deploy"

## Notas Importantes
- O app estará disponível 24/7 na URL fornecida
- Plano gratuito do Render pode ter cold start (primeiros 30s lentos)
- Se precisar de domínio customizado, configure nas settings da plataforma

## Solução de Problemas
- Se der erro no deploy, verifique os logs na plataforma
- Certifique-se que todos os arquivos foram commitados
- Verifique se requirements.txt está correto
