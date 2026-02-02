/**
 * Enhanced Chat UI with Loading States and Error Handling
 */

// Add loading states to ChatUI class
ChatUI.prototype.showLoading = function (message = 'Processing...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-indicator';
    loadingDiv.id = 'loading';
    loadingDiv.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    this.messagesContainer.appendChild(loadingDiv);
    this.scrollToBottom();
};

ChatUI.prototype.hideLoading = function () {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.remove();
    }
};

ChatUI.prototype.showError = function (message) {
    this.clearWelcome();

    const errorDiv = document.createElement('div');
    errorDiv.className = 'message agent error-message';
    errorDiv.innerHTML = `
        <div class="message-avatar">⚠️</div>
        <div class="message-content error">
            <strong>Error</strong><br>
            ${this.formatMessage(message)}
            <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        </div>
    `;
    this.messagesContainer.appendChild(errorDiv);
    this.scrollToBottom();
};

// Add download button creator
ChatUI.prototype.createDownloadButton = function (path, label) {
    return `
        <a href="${path}" download class="download-btn">
            📥 Download ${label}
        </a>
    `;
};

// Add success message
ChatUI.prototype.showSuccess = function (message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-toast';
    successDiv.textContent = '✅ ' + message;
    document.body.appendChild(successDiv);

    setTimeout(() => {
        successDiv.classList.add('show');
    }, 100);

    setTimeout(() => {
        successDiv.classList.remove('show');
        setTimeout(() => successDiv.remove(), 300);
    }, 3000);
};

// Export
window.ChatUIEnhanced = true;
