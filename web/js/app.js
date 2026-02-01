/**
 * Main Application
 * Coordinates file upload, merge, and download
 */

class MergeApp {
    constructor() {
        this.taskId = null;
        this.mergeBtn = document.getElementById('mergeBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.newMergeBtn = document.getElementById('newMergeBtn');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.statusMessage = document.getElementById('statusMessage');
        this.resultSection = document.getElementById('resultSection');
        this.resultInfo = document.getElementById('resultInfo');

        this.init();
    }

    init() {
        // Check API health on load
        this.checkAPIHealth();

        // Merge button click
        this.mergeBtn.addEventListener('click', () => {
            this.startMerge();
        });

        // Download button click
        this.downloadBtn.addEventListener('click', () => {
            this.downloadResult();
        });

        // New merge button click
        this.newMergeBtn.addEventListener('click', () => {
            this.reset();
        });
    }

    async checkAPIHealth() {
        const isHealthy = await API.checkHealth();

        if (!isHealthy) {
            this.showError('⚠️ Backend API is not running. Please start the server first:\ncd src/api && python main.py');
        }
    }

    async startMerge() {
        try {
            const files = uploadManager.getFiles();

            if (files.length === 0) {
                this.showError('Please select files to merge');
                return;
            }

            // Disable button and show progress
            this.mergeBtn.disabled = true;
            this.showProgress(true);
            this.setProgress(10, 'Uploading files...');

            // Upload files
            const uploadResponse = await API.uploadFiles(files);
            this.taskId = uploadResponse.task_id;

            this.setProgress(50, 'Processing files...');

            // Get options
            const outputFilename = document.getElementById('outputName').value || 'merged_result.xlsx';

            // Start merge
            const mergeResponse = await API.startMerge(this.taskId, outputFilename);

            this.setProgress(100, 'Merge complete!');

            // Show success
            setTimeout(() => {
                this.showSuccess(files.length, outputFilename);
            }, 500);

        } catch (error) {
            console.error('Merge error:', error);
            this.showError(`Error: ${error.message}`);
            this.showProgress(false);
            this.mergeBtn.disabled = false;
        }
    }

    downloadResult() {
        if (!this.taskId) {
            this.showError('No result available to download');
            return;
        }

        const downloadUrl = API.getDownloadUrl(this.taskId);

        // Create temporary link and trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = document.getElementById('outputName').value || 'merged_result.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showSuccess(null, null, 'File downloaded successfully!');
    }

    showProgress(show) {
        this.progressContainer.style.display = show ? 'block' : 'none';
    }

    setProgress(percent, message) {
        this.progressFill.style.width = `${percent}%`;
        this.progressText.textContent = message;
    }

    showSuccess(fileCount, filename, customMessage) {
        this.showProgress(false);
        this.resultSection.style.display = 'block';

        if (customMessage) {
            this.statusMessage.textContent = customMessage;
            this.statusMessage.className = 'status-message success';
            setTimeout(() => {
                this.statusMessage.className = 'status-message';
            }, 3000);
        } else {
            this.resultInfo.textContent = `Successfully merged ${fileCount} file(s) into ${filename}`;
        }

        // Scroll to result
        this.resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    showError(message) {
        this.statusMessage.textContent = message;
        this.statusMessage.className = 'status-message error';

        setTimeout(() => {
            this.statusMessage.className = 'status-message';
        }, 5000);
    }

    reset() {
        // Reset state
        this.taskId = null;

        // Clear files
        uploadManager.clear();

        // Hide result section
        this.resultSection.style.display = 'none';

        // Reset progress
        this.showProgress(false);
        this.setProgress(0, '');

        // Clear messages
        this.statusMessage.className = 'status-message';

        // Enable merge button
        this.mergeBtn.disabled = true;

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new MergeApp();
    window.app = app;

    console.log('✅ Smart Document Factory initialized');
    console.log('📡 API endpoint:', 'http://localhost:8000/api/v1');
});
