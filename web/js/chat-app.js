/**
 * Chat Application
 * Main application logic
 */

class ChatApp {
    constructor() {
        this.ui = new ChatUI();
        this.ws = new WebSocketManager();
        this.sessionId = null;
        this.uploadedFile = null;

        this.init();
    }

    async init() {
        // Create session
        await this.createSession();

        // Setup file upload
        this.setupFileUpload();

        // Setup message input
        this.setupMessageInput();

        // Setup WebSocket handlers
        this.setupWebSocket();

        // Update status indicator
        this.updateStatus('connecting');
    }

    async createSession() {
        try {
            const response = await fetch('http://localhost:8000/api/v1/chat/sessions', {
                method: 'POST'
            });

            const data = await response.json();
            this.sessionId = data.session_id;

            console.log('✅ Session created:', this.sessionId);

            // Connect WebSocket
            await this.ws.connect(this.sessionId);

        } catch (error) {
            console.error('Failed to create session:', error);
            this.ui.addMessage('⚠️ Failed to connect to server. Please make sure the API is running.', 'agent');
            this.updateStatus('error');
        }
    }

    setupFileUpload() {
        const uploadZone = document.getElementById('uploadZone');
        const browseBtn = document.getElementById('browseBtn');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');

        browseBtn.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadFile(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = '#3B82F6';
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.style.borderColor = '#D1D5DB';
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = '#D1D5DB';

            if (e.dataTransfer.files.length > 0) {
                this.uploadFile(e.dataTransfer.files[0]);
            }
        });
    }

    async uploadFile(file) {
        this.uploadedFile = file;
        const fileInfo = document.getElementById('fileInfo');

        // Show file info
        fileInfo.innerHTML = `📄 ${file.name} (${this.formatFileSize(file.size)})`;
        fileInfo.classList.remove('hidden');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(
                `http://localhost:8000/api/v1/chat/sessions/${this.sessionId}/upload`,
                {
                    method: 'POST',
                    body: formData
                }
            );

            const data = await response.json();

            if (response.ok) {
                // Update UI with data summary
                this.ui.updateDataSummary(data.data_summary);

                // Add system message
                this.ui.addMessage(
                    `✅ File uploaded: **${file.name}**\n\n` +
                    `I can see ${data.data_summary.total_rows} rows and ${data.data_summary.total_columns} columns.\n\n` +
                    `What would you like to analyze?`,
                    'agent',
                    {
                        actions: ['Filter data', 'Create pivot', 'Show summary', 'Generate chart']
                    }
                );

                this.ui.enableInput();
            } else {
                throw new Error(data.detail || 'Upload failed');
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.ui.addMessage(`❌ Upload failed: ${error.message}`, 'agent');
        }
    }

    setupMessageInput() {
        const messageInput = this.ui.messageInput;
        const sendBtn = this.ui.sendBtn;

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            this.ui.autoResize();
        });

        // Send on Enter (Shift+Enter for new line)
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Send button click
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
    }

    setupWebSocket() {
        // Handle incoming messages
        this.ws.onMessage((data) => {
            this.handleAgentResponse(data);
        });

        // Handle status changes
        this.ws.onStatusChange = (status) => {
            this.updateStatus(status);
        };
    }

    sendMessage() {
        const message = this.ui.messageInput.value.trim();

        if (!message) return;

        // Add user message to UI
        this.ui.addMessage(message, 'user');

        // Clear input
        this.ui.clearInput();

        // Show typing indicator
        this.ui.showTyping();

        // Send via WebSocket
        this.ws.sendMessage(message);
    }

    handleAgentResponse(data) {
        // Hide typing indicator
        this.ui.hideTyping();

        if (data.error) {
            this.ui.addMessage(`❌ Error: ${data.error}`, 'agent');
            return;
        }

        // Add agent message
        const options = {};

        if (data.result && data.result.preview) {
            options.preview = data.result.preview;
        }

        if (data.quick_actions) {
            options.actions = data.quick_actions;
        }

        this.ui.addMessage(data.message, 'agent', options);

        // Update quick actions in sidebar
        if (data.quick_actions) {
            this.ui.setQuickActions(data.quick_actions);
        }
    }

    handleQuickAction(action) {
        // Simulate user message
        this.ui.messageInput.value = action;
        this.sendMessage();
    }

    updateStatus(status) {
        const indicator = document.getElementById('statusIndicator');
        const statusText = indicator.querySelector('.status-text');

        indicator.className = 'status-indicator';

        switch (status) {
            case 'connected':
                indicator.classList.add('connected');
                statusText.textContent = 'Connected';
                break;
            case 'disconnected':
                indicator.classList.add('disconnected');
                statusText.textContent = 'Disconnected';
                break;
            case 'connecting':
                statusText.textContent = 'Connecting...';
                break;
            case 'error':
                indicator.classList.add('disconnected');
                statusText.textContent = 'Error';
                break;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ChatApp();
    console.log('✅ Chat app initialized');
});
