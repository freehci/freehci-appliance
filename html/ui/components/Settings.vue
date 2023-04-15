<template>
    <div class="container-fluid">
      <h1 class="mt-3 mb-3">Settings</h1>
      <div>
        <button v-for="(tab, index) in tabs" :key="index" class="btn btn-dark mr-1" @click="activeTab = index">{{ tab }}</button>
      </div>
      <component :is="currentTabComponent"></component>
    </div>
  </template>
  
<script>
  const Networking = {
    template: `
      <div class="group-container">
        <div class="card bg-dark text-white mb-3">
          <div class="card-header">Group 1</div>
          <div class="card-body">
            <!-- Legg til skjema for gruppe 1 her -->
          </div>
        </div>
        <div class="card bg-dark text-white mb-3">
          <div class="card-header">Group 2</div>
          <div class="card-body">
            <!-- Legg til skjema for gruppe 2 her -->
          </div>
        </div>
      </div>
    `,
  };
  
  const ComponentsAndServices = {
    template: `
      <div>
        <!-- Innhold for Components and services fane -->
      </div>
    `,
  };
  
  const Appliance = {
    template: `
      <div>
        <!-- Innhold for Appliance fane -->
      </div>
    `,
  };
  
  const Misc = {
    template: `
      <div>
        <!-- Innhold for Misc fane -->
      </div>
    `,
  };
  
  export default {
    name: 'Settings',
    data() {
      return {
        activeTab: 0,
        tabs: ['Networking', 'Components and services', 'Appliance', 'Misc'],
      };
    },
    computed: {
      currentTabComponent() {
        switch (this.activeTab) {
          case 0:
            return Networking;
          case 1:
            return ComponentsAndServices;
          case 2:
            return Appliance;
          case 3:
            return Misc;
          default:
            return null;
        }
      },
    },
  };
</script>
  
<style scoped>
    button.btn-dark {
        background-color: #343a40;
        color: white;
        margin-bottom: 1rem;
    }
        
    .group-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        background-color: #343a40;
        padding: 1rem;
        border-radius: 5px;
        position: relative;
    }

    .card {
        flex: 1;
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        padding-top: 1.5rem;
    }

    .card-header {
        position: absolute;
        top: 0;
        left: 0;
        background-color: transparent;
        padding: 0;
        margin-left: 0.5rem;
        margin-top: -0.5rem;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
  