<template>
    <div class="table-responsive">
      <table class="table table-dark table-striped">
        <thead>
          <tr>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
            <tr><td>Nodes</td> <td>{{ Metrics.nodes }}</td></tr>
            <tr><td>CPU</td> <td>{{ Metrics.cpu }}</td></tr>
            <tr><td>Memory</td> <td>{{ Metrics.memory }}</td></tr>
            <tr><td>Storage</td> <td>{{ Metrics.disk }}</td></tr>
            <tr><td>Network</td> <td>N/A</td></tr>
            <tr><td>Power</td> <td>N/A</td></tr>
            <tr><td>Temperature</td> <td>N/A</td></tr>
            <tr><td>Uptime</td> <td>{{ Metrics.uptime }}</td></tr>
            <tr><td>Version</td> <td>{{ Metrics.version }}</td></tr>
        </tbody>
      </table>
    </div>
</template>

<script>
  export default {
    data() {
      return {
        Metrics: [],
      };
    },
    
    methods: {
      fetchMetrics() {
        axios
          .get(window.apiBaseUrl + "appliance/metrics")
          .then((response) => {
            this.Metrics = response.data;
          })
          .catch((error) => {
            console.error("Error fetching nodes:", error);
          });
      },
    },
    mounted() {
      this.fetchMetrics();
      setInterval(this.fetchMetrics, 5000); // Update every 5 seconds
    },
  };
</script>