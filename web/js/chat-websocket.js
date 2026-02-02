/**
 * WebSocket Manager
 * Handles WebSocket connection to chat API
 */

class WebSocketManager {
    constructor(apiUrl = 'ws://localhost:8000/api/v1/chat/ws') {
        this.apiUrl = apiUrl;
        this.ws = null;
        this.sessionId = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.messageHandlers = [];
    }

    async connect(sessionId) {
        this.sessionId = sessionId;
        const wsUrl = `${this.apiUrl}/${sessionId}`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('✅ WebSocket connected');
                this.connected = true;
                this.reconnectAttempts = 0;
                this.onStatusChange('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.onStatusChange('error');
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.connected = false;
                this.onStatusChange('disconnected');
                this.attemptReconnect();
            };

        } catch (error) {
            console.error('Failed to connect:', error);
            this.onStatusChange('error');
        }
    }

    sendMessage(message) {
        if (!this.connected || !this.ws) {
            console.error('WebSocket not connected');
            return false;
        }

        try {
            this.ws.send(JSON.stringify({ message }));
            return true;
        } catch (error) {
            console.error('Error sending message:', error);
            return false;
        }
    }

    handleMessage(data) {
        // Notify all registered handlers
        this.messageHandlers.forEach(handler => handler(data));
    }

    onMessage(handler) {
        this.messageHandlers.push(handler);
    }

    onStatusChange(status) {
        // Override this method
        console.log('Status:', status);
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnect attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

        setTimeout(() => {
            if (this.sessionId) {
                this.connect(this.sessionId);
            }
        }, delay);
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.connected = false;
        this.sessionId = null;
    }
}

// Export for use
window.WebSocketManager = WebSocketManager;
