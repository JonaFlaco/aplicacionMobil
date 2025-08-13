// Variables globales
let currentVideoId = null;
let allVideos = [];
let filteredVideos = [];

// Configuración de la API
// Detectar automáticamente el entorno
function getApiBaseUrl() {
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // Si estamos en localhost sin puerto específico (Docker), usar el puerto 80
    if (hostname === 'localhost' && !port) {
        return ''; // URL relativa para Docker
    }
    
    // Si estamos en Live Server (puerto 5500), usar puerto 5000
    if (port === '5500') {
        return 'http://localhost:5000';
    }
    
    // Para otros casos, usar URL relativa
    return '';
}

const API_BASE_URL = getApiBaseUrl();

// DOM Elements
const searchInput = document.getElementById('searchInput');
const sortSelect = document.getElementById('sortSelect');
const tagFilter = document.getElementById('tagFilter');
const videosContainer = document.getElementById('videosContainer');
const uploadForm = document.getElementById('uploadForm');
const fileUploadArea = document.getElementById('fileUploadArea');
const videoFile = document.getElementById('videoFile');
const videoModal = document.getElementById('videoModal');
const toast = document.getElementById('toast');

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    // Cargar videos
    loadVideos();
    
    // Cargar estadísticas
    loadStats();
    
    // Cargar tags populares
    loadPopularTags();
    
    // Mostrar sección inicial
    showSection('videos');
}

function setupEventListeners() {
    // Navegación
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const section = e.target.closest('.nav-btn').dataset.section;
            showSection(section);
        });
    });

    // Búsqueda y filtros
    searchInput.addEventListener('input', debounce(filterVideos, 300));
    sortSelect.addEventListener('change', filterVideos);
    tagFilter.addEventListener('change', filterVideos);

    // Formulario de subida
    uploadForm.addEventListener('submit', handleUpload);
    
    // Drag and drop
    fileUploadArea.addEventListener('dragover', handleDragOver);
    fileUploadArea.addEventListener('dragleave', handleDragLeave);
    fileUploadArea.addEventListener('drop', handleDrop);
    
    // Cambio de archivo
    videoFile.addEventListener('change', handleFileSelect);

    // Cerrar modal con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && videoModal.classList.contains('active')) {
            closeModal();
        }
    });

    // Cerrar modal clickeando fuera
    videoModal.addEventListener('click', (e) => {
        if (e.target === videoModal) {
            closeModal();
        }
    });
}

// Navegación entre secciones
function showSection(sectionName) {
    // Actualizar botones de navegación
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.section === sectionName) {
            btn.classList.add('active');
        }
    });

    // Mostrar sección correspondiente
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Cargar datos específicos de la sección
    if (sectionName === 'analytics') {
        loadStats();
        loadPopularTags();
    }
}

// Gestión de videos
async function loadVideos() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/videos`);
        
        if (!response.ok) {
            throw new Error('Error al cargar videos');
        }
        
        const data = await response.json();
        allVideos = data.data || [];
        filteredVideos = [...allVideos];
        
        updateTagFilter();
        renderVideos();
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al cargar videos', 'error');
        hideLoading();
    }
}

function renderVideos() {
    hideLoading();
    
    if (filteredVideos.length === 0) {
        showEmptyState();
        return;
    }
    
    hideEmptyState();
    
    const videosHTML = filteredVideos.map(video => `
        <div class="video-card" onclick="openVideoModal(${video.id})">
            <div class="video-thumbnail">
                <video preload="metadata" muted>
                    <source src="/uploads/${video.filename}" type="video/mp4">
                </video>
                <div class="video-overlay">
                    <div class="play-button">
                        <i class="fas fa-play"></i>
                    </div>
                </div>
            </div>
            <div class="video-info">
                <div class="video-title">${escapeHtml(video.title)}</div>
                <div class="video-meta">
                    <span>${formatDate(video.upload_date)}</span>
                    <span>${formatFileSize(video.file_size)}</span>
                </div>
                <div class="video-tags">
                    ${video.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
    
    videosContainer.innerHTML = videosHTML;
}

function filterVideos() {
    const searchTerm = searchInput.value.toLowerCase();
    const selectedTag = tagFilter.value;
    const sortBy = sortSelect.value;
    
    // Filtrar
    filteredVideos = allVideos.filter(video => {
        const matchesSearch = !searchTerm || 
            video.title.toLowerCase().includes(searchTerm) ||
            video.description.toLowerCase().includes(searchTerm) ||
            video.tags.some(tag => tag.toLowerCase().includes(searchTerm));
        
        const matchesTag = !selectedTag || video.tags.includes(selectedTag);
        
        return matchesSearch && matchesTag;
    });
    
    // Ordenar
    const [sortField, sortOrder] = sortBy.split('-');
    filteredVideos.sort((a, b) => {
        let aValue, bValue;
        
        if (sortField === 'date') {
            aValue = new Date(a.upload_date);
            bValue = new Date(b.upload_date);
        } else if (sortField === 'title') {
            aValue = a.title.toLowerCase();
            bValue = b.title.toLowerCase();
        }
        
        if (sortOrder === 'asc') {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });
    
    renderVideos();
}

function updateTagFilter() {
    const allTags = new Set();
    allVideos.forEach(video => {
        video.tags.forEach(tag => allTags.add(tag));
    });
    
    const currentValue = tagFilter.value;
    tagFilter.innerHTML = '<option value="">Todos los tags</option>';
    
    Array.from(allTags).sort().forEach(tag => {
        const option = document.createElement('option');
        option.value = tag;
        option.textContent = tag;
        if (tag === currentValue) {
            option.selected = true;
        }
        tagFilter.appendChild(option);
    });
}

// Modal de video
async function openVideoModal(videoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}`);
        
        if (!response.ok) {
            throw new Error('Error al cargar video');
        }
        
        const data = await response.json();
        const video = data.data;
        
        currentVideoId = videoId;
        
        // Llenar información del modal
        document.getElementById('modalVideoTitle').textContent = video.title;
        document.getElementById('modalVideoDescription').textContent = video.description || 'Sin descripción';
        document.getElementById('modalVideoTags').textContent = video.tags.join(', ') || 'Sin tags';
        document.getElementById('modalVideoDate').textContent = formatDate(video.upload_date);
        
        // Configurar video
        const modalVideo = document.getElementById('modalVideo');
        modalVideo.src = `/uploads/${video.filename}`;
        modalVideo.load();
        
        // Limpiar estado de publicación
        document.getElementById('publicationStatus').style.display = 'none';
        document.querySelectorAll('input[name="platform"]').forEach(cb => {
            cb.checked = false;
        });
        
        // Mostrar modal
        videoModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al cargar video', 'error');
    }
}

function closeModal() {
    videoModal.classList.remove('active');
    document.body.style.overflow = '';
    
    // Pausar video
    const modalVideo = document.getElementById('modalVideo');
    modalVideo.pause();
    modalVideo.currentTime = 0;
    
    currentVideoId = null;
}

// Subida de archivos
function handleDragOver(e) {
    e.preventDefault();
    fileUploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        videoFile.files = files;
        handleFileSelect();
    }
}

function handleFileSelect() {
    const file = videoFile.files[0];
    if (file) {
        const fileName = file.name;
        const fileSize = formatFileSize(file.size);
        
        fileUploadArea.innerHTML = `
            <i class="fas fa-video"></i>
            <h3>Archivo seleccionado</h3>
            <p><strong>${fileName}</strong></p>
            <p>Tamaño: ${fileSize}</p>
            <span class="supported-formats">Haz clic para seleccionar otro archivo</span>
        `;
    }
}

async function handleUpload(e) {
    e.preventDefault();
    
    console.log('🚀 Iniciando subida de video...');
    
    const formData = new FormData();
    const videoFile = document.getElementById('videoFile').files[0];
    const title = document.getElementById('videoTitle').value;
    const description = document.getElementById('videoDescription').value;
    const tags = document.getElementById('videoTags').value;
    
    console.log('📋 Datos del formulario:');
    console.log('   - Archivo:', videoFile ? videoFile.name : 'No seleccionado');
    console.log('   - Título:', title);
    console.log('   - Descripción:', description);
    console.log('   - Tags:', tags);
    console.log('   - API_BASE_URL:', API_BASE_URL);
    
    formData.append('video', videoFile);
    formData.append('title', title);
    formData.append('description', description);
    formData.append('tags', tags);
    
    // Verificar contenido del FormData
    console.log('📦 Contenido del FormData:');
    for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
            console.log(`   - ${key}:`, value.name, `(${value.size} bytes, ${value.type})`);
        } else {
            console.log(`   - ${key}:`, value);
        }
    }
    
    try {
        showUploadProgress();
        
        const url = `${API_BASE_URL}/api/videos`;
        console.log('🌐 URL de la solicitud:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        console.log('📥 Respuesta del servidor:');
        console.log('   - Status:', response.status);
        console.log('   - Status Text:', response.statusText);
        console.log('   - Headers:', Object.fromEntries(response.headers.entries()));
        
        const data = await response.json();
        console.log('   - Response Data:', data);
        
        if (response.ok) {
            showToast('Video subido exitosamente', 'success');
            resetForm();
            loadVideos();
            showSection('videos');
        } else {
            throw new Error(data.message || data.error || 'Error al subir video');
        }
        
    } catch (error) {
        console.error('❌ Error en handleUpload:', error);
        showToast(error.message, 'error');
    } finally {
        hideUploadProgress();
    }
}

function resetForm() {
    uploadForm.reset();
    fileUploadArea.innerHTML = `
        <i class="fas fa-cloud-upload-alt"></i>
        <h3>Selecciona un video</h3>
        <p>Arrastra y suelta tu video aquí o haz clic para seleccionar</p>
        <span class="supported-formats">Formatos soportados: MP4, AVI, MOV, WMV, FLV, WEBM</span>
    `;
}

function showUploadProgress() {
    const progressElement = document.getElementById('uploadProgress');
    const uploadBtn = document.getElementById('uploadBtn');
    
    progressElement.style.display = 'block';
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subiendo...';
    
    // Simular progreso
    let progress = 0;
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `Subiendo... ${Math.round(progress)}%`;
        
        if (progress >= 90) {
            clearInterval(interval);
        }
    }, 200);
}

function hideUploadProgress() {
    const progressElement = document.getElementById('uploadProgress');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    
    progressFill.style.width = '100%';
    progressText.textContent = 'Completado!';
    
    setTimeout(() => {
        progressElement.style.display = 'none';
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Subir Video';
        progressFill.style.width = '0%';
    }, 1000);
}

// Publicación en redes sociales
async function publishVideo() {
    const selectedPlatforms = Array.from(document.querySelectorAll('input[name="platform"]:checked'))
        .map(cb => cb.value);
    
    if (selectedPlatforms.length === 0) {
        showToast('Selecciona al menos una plataforma', 'warning');
        return;
    }
    
    try {
        const publishBtn = document.getElementById('publishBtn');
        const originalText = publishBtn.innerHTML;
        
        publishBtn.disabled = true;
        publishBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publicando...';
        
        const response = await fetch(`${API_BASE_URL}/api/videos/${currentVideoId}/publish`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                platforms: selectedPlatforms
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showPublicationResults(data.data);
            showToast('Publicación iniciada', 'success');
        } else {
            throw new Error(data.message || 'Error al publicar');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
    } finally {
        const publishBtn = document.getElementById('publishBtn');
        publishBtn.disabled = false;
        publishBtn.innerHTML = '<i class="fas fa-share-alt"></i> Publicar en Plataformas Seleccionadas';
    }
}

function showPublicationResults(results) {
    const statusDiv = document.getElementById('publicationStatus');
    
    const resultsHTML = results.map(result => `
        <div class="publication-result ${result.success ? 'success' : 'error'}">
            <strong>${result.platform.charAt(0).toUpperCase() + result.platform.slice(1)}:</strong>
            ${result.success ? 
                `<span class="success">✓ ${result.message}</span>` :
                `<span class="error">✗ ${result.error || 'Error desconocido'}</span>`
            }
        </div>
    `).join('');
    
    statusDiv.innerHTML = `
        <h5>Resultados de Publicación:</h5>
        ${resultsHTML}
    `;
    statusDiv.style.display = 'block';
}

// Eliminar video
async function deleteVideo() {
    if (!confirm('¿Estás seguro de que quieres eliminar este video? Esta acción no se puede deshacer.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/videos/${currentVideoId}/delete`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Video eliminado exitosamente', 'success');
            closeModal();
            loadVideos();
        } else {
            throw new Error(data.message || 'Error al eliminar video');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
    }
}

// Estadísticas
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/videos`);
        
        if (!response.ok) {
            throw new Error('Error al cargar estadísticas');
        }
        
        const data = await response.json();
        const videos = data.data || [];
        
        // Calcular estadísticas
        const totalVideos = videos.length;
        const totalSize = videos.reduce((sum, video) => sum + (video.file_size || 0), 0);
        const totalDuration = videos.reduce((sum, video) => sum + (video.duration || 0), 0);
        const totalPublications = videos.reduce((sum, video) => sum + (video.publications || []).length, 0);
        
        // Actualizar DOM
        document.getElementById('totalVideos').textContent = totalVideos;
        document.getElementById('totalSize').textContent = formatFileSize(totalSize);
        document.getElementById('totalDuration').textContent = formatDuration(totalDuration);
        document.getElementById('totalPublications').textContent = totalPublications;
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al cargar estadísticas', 'error');
    }
}

async function loadPopularTags() {
    try {
        // Calcular tags populares desde los videos cargados
        const tagCounts = {};
        allVideos.forEach(video => {
            video.tags.forEach(tag => {
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
        });
        
        const popularTags = Object.entries(tagCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        const tagsContainer = document.getElementById('tagsContainer');
        
        if (popularTags.length === 0) {
            tagsContainer.innerHTML = '<p>No hay tags disponibles</p>';
            return;
        }
        
        const tagsHTML = popularTags.map(([tag, count]) => `
            <div class="popular-tag">
                ${escapeHtml(tag)}
                <span class="tag-count">${count}</span>
            </div>
        `).join('');
        
        tagsContainer.innerHTML = tagsHTML;
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al cargar tags populares', 'error');
    }
}

// Utilidades
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    if (!seconds) return '0 min';
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes % 60}min`;
    }
    return `${minutes} min`;
}

function showLoading() {
    videosContainer.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Cargando videos...
        </div>
    `;
}

function hideLoading() {
    const loading = videosContainer.querySelector('.loading');
    if (loading) {
        loading.remove();
    }
}

function showEmptyState() {
    document.getElementById('emptyState').style.display = 'block';
    videosContainer.innerHTML = '';
}

function hideEmptyState() {
    document.getElementById('emptyState').style.display = 'none';
}

function showToast(message, type = 'info') {
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideToast();
    }, 5000);
}

function hideToast() {
    toast.classList.remove('show');
}