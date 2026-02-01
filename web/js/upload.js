/**
 * File Upload Module
 * Handles drag & drop and file selection
 */

class FileUploadManager {
    constructor() {
        this.files = [];
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.browseBtn = document.getElementById('browseBtn');
        this.fileList = document.getElementById('fileList');

        this.init();
    }

    init() {
        // Browse button click
        this.browseBtn.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.addFiles(e.target.files);
        });

        // Drag & drop events
        this.dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropZone.classList.add('drag-over');
        });

        this.dropZone.addEventListener('dragleave', () => {
            this.dropZone.classList.remove('drag-over');
        });

        this.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('drag-over');
            this.addFiles(e.dataTransfer.files);
        });
    }

    addFiles(fileList) {
        const validFiles = Array.from(fileList).filter(file => this.validateFile(file));

        if (validFiles.length === 0) {
            this.showError('No valid files selected. Please upload Excel, CSV, Word, or PDF files.');
            return;
        }

        this.files.push(...validFiles);
        this.renderFileList();
        this.updateMergeButton();
    }

    validateFile(file) {
        const validExtensions = ['.xlsx', '.xls', '.csv', '.docx', '.doc', '.pdf'];
        const extension = '.' + file.name.split('.').pop().toLowerCase();

        if (!validExtensions.includes(extension)) {
            return false;
        }

        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            this.showError(`${file.name} is too large (max 50MB)`);
            return false;
        }

        return true;
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.renderFileList();
        this.updateMergeButton();
    }

    renderFileList() {
        if (this.files.length === 0) {
            this.fileList.innerHTML = '';
            return;
        }

        this.fileList.innerHTML = this.files.map((file, index) => `
            <div class="file-item">
                <div class="file-item-info">
                    <span class="file-icon">${this.getFileIcon(file.name)}</span>
                    <div class="file-details">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button class="file-remove" onclick="uploadManager.removeFile(${index})" title="Remove file">
                    ✕
                </button>
            </div>
        `).join('');
    }

    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const icons = {
            'xlsx': '📊',
            'xls': '📊',
            'csv': '📋',
            'docx': '📝',
            'doc': '📝',
            'pdf': '📄'
        };
        return icons[extension] || '📄';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    updateMergeButton() {
        const mergeBtn = document.getElementById('mergeBtn');
        mergeBtn.disabled = this.files.length === 0;
    }

    showError(message) {
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.textContent = message;
        statusMessage.className = 'status-message error';

        setTimeout(() => {
            statusMessage.className = 'status-message';
        }, 5000);
    }

    getFiles() {
        return this.files;
    }

    clear() {
        this.files = [];
        this.fileInput.value = '';
        this.renderFileList();
        this.updateMergeButton();
    }
}

// Initialize upload manager
const uploadManager = new FileUploadManager();
window.uploadManager = uploadManager;
