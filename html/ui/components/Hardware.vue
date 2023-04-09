<template>
    <div class="table-responsive">
      <table class="table table-dark table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Manufacturer</th>
            <th>Model</th>
            <th>Serial</th>
            <th>Operating System</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="node in nodes" :key="node.id">
            <td>{{ node.id }}</td>
            <td>{{ node.name }}</td>
            <td>{{ node.manufacturer }}</td>
            <td>{{ node.model }}</td>
            <td>{{ node.serial }}</td>
            <td>{{ node.operating_system }}</td>
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
      };
    },
    methods: {
      fetchNodes() {
        axios
          .get("http://localhost:8000/hardware/nodes")
          .then((response) => {
            this.nodes = response.data;
          })
          .catch((error) => {
            console.error("Error fetching nodes:", error);
          });
      },
    },
    mounted() {
      this.fetchNodes();
      setInterval(this.fetchNodes, 5000); // Update every 5 seconds
    },
  };
  </script>
  