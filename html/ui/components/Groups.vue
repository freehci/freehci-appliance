<template>
    <div>
      <h1>Groups</h1>
    </div>
  </template>
  
<script> 
  export default {
    data() {
      return {
        items: [],
      };
    },
    methods: {
      // Fetch items
      fetchItems() {
        axios
          .get(window.apiBaseUrl + "groups")
          .then((response) => {
            this.items = response.data;
          })
          .catch((error) => {
            console.error("Error fetching items:", error);
          });
      },
  
      // Create a new item
      createItem(item) {
        axios
          .post(window.apiBaseUrl + "groups", item)
          .then((response) => {
            this.items.push(response.data);
          })
          .catch((error) => {
            console.error("Error creating item:", error);
          });
      },
  
      // Update an existing item
      updateItem(item) {
        axios
          .put(window.apiBaseUrl + `groups/${item.id}`, item)
          .then((response) => {
            const index = this.items.findIndex((i) => i.id === item.id);
            this.items.splice(index, 1, response.data);
          })
          .catch((error) => {
            console.error("Error updating item:", error);
          });
      },
  
      // Delete an item
      deleteItem(item) {
        axios
          .delete(window.apiBaseUrl + `groups/${item.id}`)
          .then(() => {
            const index = this.items.findIndex((i) => i.id === item.id);
            this.items.splice(index, 1);
          })
          .catch((error) => {
            console.error("Error deleting item:", error);
          });
      },
    },
    mounted() {
      this.fetchItems();
      setInterval(this.fetchItems, 5000); // Update every 5 seconds
    },
  };
  </script>
  
  <style scoped>
  /* Your component styles go here */
  </style>
  