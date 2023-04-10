<!-- Please see Template_WS.md for explanation of this file -->
<template>
    <div>
      <!-- Your component template goes here -->
    </div>
</template>

<script>
  export default {
    data() {
      return {
        items: [],
        socket: null,
        reconnectInterval: null,
      };
    },
    methods: {
      // Initialize WebSocket connection
      initWebSocket() {
        this.socket = new WebSocket(window.webSocketBaseUrl);
  
        this.socket.onopen = () => {
          console.log("WebSocket connection opened.");
          if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
          }
          this.fetchItems();
        };
  
        this.socket.onmessage = (event) => {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        };
  
        this.socket.onclose = (event) => {
          console.log("WebSocket connection closed:", event);
          if (!this.reconnectInterval) {
            this.reconnectInterval = setInterval(() => {
              this.initWebSocket();
            }, 5000); // Attempt to reconnect every 5 seconds
          }
        };
  
        this.socket.onerror = (error) => {
          console.error("WebSocket error:", error);
        };
      },
  
      // Handle incoming WebSocket messages
      handleMessage(message) {
        // Process the message based on its type (fetch, create, update, delete)
        switch (message.type) {
          case "fetch":
            this.items = message.data;
            break;
          case "create":
            this.items.push(message.data);
            break;
          case "update":
            const updateIndex = this.items.findIndex((item) => item.id === message.data.id);
            this.items.splice(updateIndex, 1, message.data);
            break;
          case "delete":
            const deleteIndex = this.items.findIndex((item) => item.id === message.data.id);
            this.items.splice(deleteIndex, 1);
            break;
          default:
            console.error("Unknown message type:", message.type);
        }
      },
  
      // Send a WebSocket message
      sendMessage(type, data) {
        if (this.socket.readyState === WebSocket.OPEN) {
          const message = {
            type: type,
            data: data,
          };
          this.socket.send(JSON.stringify(message));
        } else {
          console.error("WebSocket is not open:", this.socket.readyState);
        }
      },
  
      // Fetch, create, update, and delete methods using WebSockets
      fetchItems() {
        this.sendMessage("fetch");
      },
      createItem(item) {
        this.sendMessage("create", item);
      },
      updateItem(item) {
        this.sendMessage("update", item);
      },
      deleteItem(item) {
        this.sendMessage("delete", item);
      },
    },
    mounted() {
      this.initWebSocket();
    },
    beforeDestroy() {
      if (this.socket) {
        this.socket.close();
      }
      if (this.reconnectInterval) {
        clearInterval(this.reconnectInterval);
      }
    },
  };
</script>
  
<style scoped>
/* Your component styles go here */
</style>
  