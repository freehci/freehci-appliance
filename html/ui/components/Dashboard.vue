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
            <tr><td><i class="fa-solid fa-circle-nodes"></i> Nodes</td> <td>{{ Metrics.nodes }}</td></tr>
            <tr><td><i class="fa-solid fa-microchip"></i> CPU</td> <td>
              <div class="progress-bar-container">
                <div 
                  class="progress-bar" 
                  :style="{
                    width: Metrics.cpu + '%', 
                    backgroundImage: 'linear-gradient(to right, #28a745, ' + getProgressBarColor(Metrics.cpu / 100 * 100) + ')',
                  }" 
                >
                  <span class="progress-bar-text">{{ Metrics.cpu }}%</span>
                
                </div>
            </div>
              
            </td></tr>
            <tr><td><i class="fa-solid fa-memory"></i> Memory</td>
              <td>
                <div class="progress-bar-container"> <!-- backgroundImage: 'linear-gradient(to right, #28a745, ' + getProgressBarColor((Metrics.free_memory / Metrics.total_memory) * 100) + ')',-->
                  <div
                    class="progress-bar"
                    :style="{
                      width: ((Metrics.total_memory - Metrics.free_memory) / Metrics.total_memory) * 100 + '%',
                      backgroundImage: 'linear-gradient(to right, #28a745, ' + getProgressBarColor(((Metrics.total_memory - Metrics.free_memory) / Metrics.total_memory) * 100) + ')',
                    }"
                  >
                    <span class="progress-bar-text">{{ ((Metrics.total_memory - Metrics.free_memory) /1024 / 1024 / 1024).toFixed(1)}}GB / {{ Math.round(Metrics.total_memory /1024 / 1024 /1024).toFixed(0)}}GB</span>
                  </div>
                </div>
            
              </td>
            </tr>
            <tr v-for="(disk, index) in Metrics.disks" :key="index">
                <td><i class="fa-regular fa-hard-drive"></i> Disk {{ index + 1 }}</td>
                <td>
                    <div class="progress-bar-container"> <!-- background: linear-gradient(0.25turn, green, red);-->
                      <div 
                        class="progress-bar" 
                        :style="{
                          width: disk.usage_percent, 
                          backgroundImage: 'linear-gradient(to right, #28a745, ' + getProgressBarColor(parseFloat(disk.usage_percent)) + ')',
                          
                        }"
                      >
                          <span class="progress-bar-text">{{ disk.used_space }} / {{ disk.total_space }}</span>
                        </div>
                    </div>
                </td>
            </tr>
            
            <tr v-for="(networkIF, index) in Metrics.network" :key="index">
                <td><i class="fa-solid fa-network-wired"></i> Interface {{ index + 1 }} ( {{ networkIF.name }} - {{ networkIF.macaddr }}) </td>
                <td>
                  Sent: {{ networkIF.bytes_sent }} - Received: {{ networkIF.bytes_received }}
                </td>
            </tr>
            
            
            <tr><td><i class="fa-solid fa-plug-circle-bolt"></i> Power</td> <td>PSU1: <i class="fa-regular fa-circle-check" style="color: #3de010;"></i> PSU2: <i class="fa-regular fa-circle-check" style="color: #3de010;"></i></td></tr>
            <tr><td><i class="fa-solid fa-temperature-high"></i> Temperature</td> <td>N/A</td></tr>
            <tr><td><i class="fa-solid fa-stopwatch"></i> Uptime</td> <td>{{ Metrics.uptime }}</td></tr>
            <tr><td><i class="fa-solid fa-code-branch"></i> Version</td> <td>{{ Metrics.version }}</td></tr>
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
      },getProgressBarColor(percent) {
        const r = Math.floor(255 * (percent / 100));
        const g = Math.floor(255 * (1 - percent / 100));
        return `rgb(${r},${g},0)`;
      },
    },
    mounted() {
      this.fetchMetrics();
      setInterval(this.fetchMetrics, 5000); // Update every 5 seconds
    },
  };
</script>