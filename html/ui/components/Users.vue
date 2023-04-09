<template>
    <!-- Add buttons -->
    <div class="mb-3">
      <button class="btn btn-primary mr-2" @click="addUser">Add User</button>
      <button class="btn btn-secondary mr-2" @click="modifyUser">Modify</button>
      <button class="btn btn-danger" @click="deleteUser">Delete</button>
    </div>
    <div class="table-responsive">
      <table class="table table-dark table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="node in nodes" :key="node.id">
            <td>
                <input type="checkbox" v-model="selectedNodes" :value="node.id" />
            </td>
            <td>{{ node.id }}</td>
            <td>{{ node.username }}</td>
            <td>{{ node.email }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
    export default {
        data() {
        return {
            nodes: [],
            selectedNodes: [],
        };
    },

    methods: {
        fetchNodes() {
            axios
                .get("http://localhost:8000/users/")
                .then((response) => {
                this.nodes = response.data;
                })
                .catch((error) => {
                console.error("Error fetching nodes:", error);
                });
        },
        // Add new functions for the buttons
        addUser() {
        // Call the API to add a user
        console.log("Add user");
        },
        modifyUser() {
        // Call the API to modify a user
        console.log("Selected nodes for modification:", this.selectedNodes);
        },
        deleteUser() {
        // Call the API to delete a user
        console.log("Selected nodes for deletion:", this.selectedNodes);
        },
    },
    mounted() {
      this.fetchNodes();
      setInterval(this.fetchNodes, 5000); // Update every 5 seconds
    },
  };
  </script>
  