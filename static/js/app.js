// Estado da aplicação
let fotos = [];
let fotoIdCounter = 0;

// Elementos DOM
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fotosContainer = document.getElementById('fotosContainer');
const btnGerar = document.getElementById('btnGerar');
const btnReiniciar = document.getElementById('btnReiniciar');
const loadingOverlay = document.getElementById('loadingOverlay');
const fabAddPhoto = document.getElementById('fabAddPhoto');
const uploadModal = document.getElementById('uploadModal');
const modalClose = document.getElementById('modalClose');
const dataInput = document.getElementById('data');

// Configurar data padrão para hoje (ajustando fuso horário)
setDateInputToToday();

// Event Listeners
fabAddPhoto.addEventListener('click', () => uploadModal.classList.add('active'));
modalClose.addEventListener('click', () => uploadModal.classList.remove('active'));
uploadModal.addEventListener('click', (e) => {
    if (e.target === uploadModal) {
        uploadModal.classList.remove('active');
    }
});
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
btnGerar.addEventListener('click', gerarPDF);
btnReiniciar.addEventListener('click', reiniciarRelatorio);

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
        file.type.startsWith('image/')
    );
    
    if (files.length > 0) {
        processarArquivos(files);
    }
});

function setDateInputToToday() {
    const today = new Date();
    today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
    dataInput.value = today.toISOString().split('T')[0];
}

// Função para processar arquivos selecionados
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    processarArquivos(files);
    fileInput.value = ''; // Limpar input
}

// Processar múltiplos arquivos
async function processarArquivos(files) {
    if (fotos.length + files.length > 50) {
        showToast('Máximo de 50 fotos por relatório', 'error');
        return;
    }

    showToast(`Processando ${files.length} foto(s)...`, 'info');

    for (const file of files) {
        if (!file.type.startsWith('image/')) {
            continue;
        }

        // Validar tamanho (máx 10MB por foto)
        if (file.size > 10 * 1024 * 1024) {
            showToast(`Foto ${file.name} é muito grande (máx. 10MB)`, 'error');
            continue;
        }

        try {
            const imageData = await readFileAsDataURL(file);
            const foto = {
                id: ++fotoIdCounter,
                nome: file.name,
                imagem: imageData,
                observacao: ''
            };

            fotos.push(foto);
            renderizarFoto(foto);
        } catch (error) {
            console.error('Erro ao processar arquivo:', error);
            showToast(`Erro ao processar ${file.name}`, 'error');
        }
    }

    showToast(`${files.length} foto(s) adicionada(s) com sucesso!`, 'success');
    
    // Fechar modal após adicionar fotos
    uploadModal.classList.remove('active');
}

// Ler arquivo como Data URL
function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Renderizar foto na interface
function renderizarFoto(foto) {
    const fotoItem = document.createElement('div');
    fotoItem.className = 'foto-item';
    fotoItem.dataset.id = foto.id;
    fotoItem.style.animation = 'slideIn 0.3s ease';

    fotoItem.innerHTML = `
        <div class="foto-preview">
            <img src="${foto.imagem}" alt="${foto.nome}">
        </div>
        <div class="foto-info">
            <textarea 
                placeholder="Adicione observações sobre esta foto..." 
                data-id="${foto.id}"
                rows="3"
            >${foto.observacao}</textarea>
            <div class="foto-actions">
                <button class="btn-remove" data-id="${foto.id}">
                    Remover
                </button>
            </div>
        </div>
    `;

    fotosContainer.appendChild(fotoItem);

    // Event listener para textarea
    const textarea = fotoItem.querySelector('textarea');
    textarea.addEventListener('input', (e) => {
        const foto = fotos.find(f => f.id == e.target.dataset.id);
        if (foto) {
            foto.observacao = e.target.value;
        }
    });

    // Event listener para botão remover
    const btnRemove = fotoItem.querySelector('.btn-remove');
    btnRemove.addEventListener('click', () => removerFoto(foto.id));
}

// Remover foto
function removerFoto(id) {
    fotos = fotos.filter(f => f.id !== id);
    const fotoItem = fotosContainer.querySelector(`[data-id="${id}"]`);
    if (fotoItem) {
        fotoItem.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => fotoItem.remove(), 300);
    }
    showToast('Foto removida', 'info');
}

// Gerar PDF
async function gerarPDF() {
    // Validações
    if (!validarFormulario()) {
        return;
    }

    if (fotos.length === 0) {
        showToast('Adicione pelo menos uma foto ao relatório', 'error');
        return;
    }

    // Mostrar loading
    loadingOverlay.classList.add('active');
    btnGerar.disabled = true;

    try {
        const dados = {
            titulo: document.getElementById('titulo').value.trim(),
            local: document.getElementById('local').value.trim(),
            sistema_ref: document.getElementById('sistemaRef').value.trim(),
            data: formatarData(dataInput.value),
            sistema: document.getElementById('sistema').value.trim(),
            fotos: fotos.map(f => ({
                imagem: f.imagem,
                observacao: f.observacao || 'Sem observações'
            }))
        };

        const response = await fetch('/api/gerar-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dados)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao gerar PDF');
        }

        // Download do PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('PDF gerado com sucesso! 🎉', 'success');

    } catch (error) {
        console.error('Erro ao gerar PDF:', error);
        showToast('Erro ao gerar PDF: ' + error.message, 'error');
    } finally {
        loadingOverlay.classList.remove('active');
        btnGerar.disabled = false;
    }
}

// Validar formulário
function validarFormulario() {
    const campos = [
        { id: 'titulo', nome: 'Título' },
        { id: 'local', nome: 'Local' },
        { id: 'sistemaRef', nome: 'Sistema' },
        { id: 'data', nome: 'Data' },
        { id: 'sistema', nome: 'Emitido por' }
    ];

    for (const campo of campos) {
        const elemento = document.getElementById(campo.id);
        if (!elemento.value.trim()) {
            showToast(`Campo "${campo.nome}" é obrigatório`, 'error');
            elemento.focus();
            return false;
        }
    }

    return true;
}

// Formatar data
function formatarData(dataISO) {
    const data = new Date(dataISO + 'T00:00:00');
    return data.toLocaleDateString('pt-BR');
}

// Reiniciar relatório
function reiniciarRelatorio() {
    if (fotos.length > 0 || document.getElementById('titulo').value) {
        if (!confirm('Tem certeza que deseja reiniciar o relatório? Todos os dados serão perdidos.')) {
            return;
        }
    }

    // Limpar fotos
    fotos = [];
    fotoIdCounter = 0;
    fotosContainer.innerHTML = '';

    // Limpar campos
    document.getElementById('titulo').value = '';
    document.getElementById('local').value = '';
    document.getElementById('sistemaRef').value = '';
    setDateInputToToday();
    document.getElementById('sistema').value = '';

    showToast('Relatório reiniciado', 'info');
}

// Sistema de notificações toast
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
    `;

    toastContainer.appendChild(toast);

    // Remover após 4 segundos
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Adicionar animação de slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Verificar saúde da API ao carregar
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (!data.logo_exists) {
            showToast('⚠️ Logo não encontrado. Adicione em assets/logo.png', 'info');
        }
    } catch (error) {
        console.error('Erro ao verificar saúde da API:', error);
    }
});
