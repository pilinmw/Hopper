/**
 * Chat UI Manager
 * Handles chat interface updates and interactions
 */

class ChatUI {
    constructor() {
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.dataSummary = document.getElementById('dataSummary');
        this.dataCard = document.getElementById('dataCard');
        this.quickActions = document.getElementById('quickActions');
        this.actionButtons = document.getElementById('actionButtons');
    }

    clearWelcome() {
        const welcome = this.messagesContainer.querySelector('.welcome-message');
        if (welcome) {
            welcome.remove();
        }
    }

    addMessage(content, sender = 'agent', options = {}) {
        this.clearWelcome();

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = sender === 'agent' ? '🤖' : '👤';
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        let messageHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                ${this.formatMessage(content)}
                ${options.preview ? this.createPreview(options.preview) : ''}
                ${options.actions ? this.createActions(options.actions) : ''}
                <div class="message-time">${time}</div>
            </div>
        `;

        messageDiv.innerHTML = messageHTML;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Convert markdown-style formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    createPreview(preview) {
        if (!preview || !preview.data) return '';

        const rows = preview.data.slice(0, 5); // Show first 5 rows
        const columns = preview.columns || Object.keys(rows[0] || {});

        let tableHTML = `
            <div class="data-preview">
                <div><strong>Preview (${preview.showing_rows} of ${preview.total_rows} rows)</strong></div>
                <div class="preview-table">
                    <table>
                        <thead>
                            <tr>
                                ${columns.map(col => `<th>${col}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.map(row => `
                                <tr>
                                    ${columns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        return tableHTML;
    }

    createActions(actions) {
        if (!actions || actions.length === 0) return '';

        return `
            <div class="message-actions">
                ${actions.map(action => `
                    <button class="quick-action-btn" onclick="app.handleQuickAction('${action}')">
                        ${action}
                    </button>
                `).join('')}
            </div>
        `;
    }

    updateDataSummary(summary) {
        if (!summary) return;

        const categories = summary.categories || {};
        const categoryList = Object.keys(categories).slice(0, 3);

        this.dataSummary.innerHTML = `
            <div><strong>Rows:</strong> ${summary.total_rows?.toLocaleString() || 0}</div>
            <div><strong>Columns:</strong> ${summary.total_columns || 0}</div>
            ${categoryList.length > 0 ? `
                <div><strong>Categories:</strong></div>
                <ul style="margin-left: 1rem; margin-top: 0.5rem;">
                    ${categoryList.map(cat => `
                        <li>${cat}: ${categories[cat].length} values</li>
                    `).join('')}
                </ul>
            ` : ''}
            ${summary.date_range ? `
                <div><strong>Date Range:</strong> ${summary.date_range[0]} to ${summary.date_range[1]}</div>
            ` : ''}
        `;

        this.dataCard.classList.remove('hidden');
    }

    setQuickActions(actions) {
        if (!actions || actions.length === 0) {
            this.quickActions.classList.add('hidden');
            return;
        }

        this.actionButtons.innerHTML = actions.map(action => `
            <button class="action-btn" onclick="app.handleQuickAction('${action}')">
                ${action}
            </button>
        `).join('');

        this.quickActions.classList.remove('hidden');
    }

    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message agent typing-indicator';
        typingDiv.id = 'typing';
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTyping() {
        const typing = document.getElementById('typing');
        if (typing) {
            typing.remove();
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    enableInput() {
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.messageInput.focus();
    }

    disableInput() {
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
    }

    clearInput() {
        this.messageInput.value = '';
        this.autoResize();
    }

    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }
}

// Export
window.ChatUI = ChatUI;
