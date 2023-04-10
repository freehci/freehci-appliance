<template>
    <!-- Add buttons -->
    <div class="mb-3">
        <button @click="openModal()" class="btn btn-primary">Add User</button>
        <button @click="openModal(selectedNodes.length === 1 ? getNodeById(selectedNodes[0]) : null)" class="btn btn-secondary" :disabled="selectedNodes.length !== 1">Modify</button>
        <button class="btn btn-danger" @click="deleteUser">Delete</button>
    </div>
    <div class="table-responsive">
      <table class="table table-dark table-striped">
        <thead>
          <tr>
            <th></th>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <!-- Add more attributes here -->
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
      <!-- Add the modal -->
      <div class="modal" tabindex="-1" :class="{ show: showModal }" style="display: block;" v-show="showModal">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{ currentNode.id ? 'Modify User' : 'Add User' }}</h5>
                    <button type="button" class="close" @click="showModal = false">
                    <span>&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form>
                        <!-- Add form fields here -->
                        <div class="form-group">
                            <label for="userId">User ID</label>
                            <input type="text" class="form-control" id="userId" v-model="currentNode.id" readonly>
                        </div>
                        <div class="form-group">
                            <label for="userName">Username</label>
                            <input type="text" class="form-control" id="userName" v-model="currentNode.username" readonly>
                            
                            <label for="email">Email</label>
                            <input type="text" class="form-control" id="email" v-model="currentNode.email" readonly>
                            <!-- First name, Last name, ... -->
                            <label for="fname">First Name</label>
                            <input type="text" class="form-control" id="firstname" readonly>
                            <label for="lname">Last Name</label>
                            <input type="text" class="form-control" id="lastname" readonly>
                        </div>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" class="form-control" id="password" v-model="currentNode.password" readonly>
                        </div>
                        
                        <!-- Add other form fields similarly -->
                    </form>
                </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary">Save</button>
                        <button type="button" class="btn btn-secondary" @click="showModal = false">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </template>
  
  <script>
    export default {
        data() {
        return {
            nodes: [],
            selectedNodes: [],
            showModal: false,
            currentNode: {},
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
        openModal(node) {
            this.currentNode = node || {};
            this.showModal = true;
        },
        getNodeById(id) {
            // Return the node with the given ID
            // TODO: Change this to use the API
            return this.nodes.find((node) => node.id === id);
        },
    },
    mounted() {
      this.fetchNodes();
      setInterval(this.fetchNodes, 5000); // Update every 5 seconds
    },
  };
  </script>
  