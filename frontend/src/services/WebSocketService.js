class WebSocketService {
  constructor() {
    this.ws = null;
    this.url = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:3000';
    this.reconnectInterval = 5000;
    this.reconnectTimer = null;
    this.eventHandlers = {};
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.emit('connect');
        this.clearReconnectTimer();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('emotionUpdate', data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnect');
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.scheduleReconnect();
    }
  }

  disconnect() {
    this.clearReconnectTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  scheduleReconnect() {
    this.clearReconnectTimer();
    this.reconnectTimer = setTimeout(() => {
      console.log('Attempting to reconnect...');
      this.connect();
    }, this.reconnectInterval);
  }

  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  emit(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => handler(data));
    }
  }

  onConnect(handler) {
    this.addEventListener('connect', handler);
  }

  onDisconnect(handler) {
    this.addEventListener('disconnect', handler);
  }

  onEmotionUpdate(handler) {
    this.addEventListener('emotionUpdate', handler);
  }

  onError(handler) {
    this.addEventListener('error', handler);
  }

  addEventListener(event, handler) {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = [];
    }
    this.eventHandlers[event].push(handler);
  }

  removeEventListener(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
    }
  }

  isConnected() {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

const webSocketService = new WebSocketService();
export default webSocketService; 