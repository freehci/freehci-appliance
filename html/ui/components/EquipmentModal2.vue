<!-- 
    File:EquipmentModal2.vue 
    Whis Modal is used to display information about a specific equipment.
    It is called from the Rack.vue component.
    Data is passed to this component from the Rack.vue component.

    This is a copy of the EquipmentModal.vue file.  It is a backup in case I mess up the original.
-->

<template>
    <div>
      <tabs :tabs="myTabs" @tab-selected="onTabSelected" :active-index="activeTabIndex">
        <component :is="selectedTabComponent" />
      </tabs>
    </div>
</template>
  
<script>

    import Tabs from "./components/Tabs.vue";
    import Overview from "./components/Overview.vue";
    import Environment from "./components/Environment.vue";
    import Hardware from "./components/Hardware.vue";
    
    export default {
        components: {
        Tabs,
        Overview,
        Environment,
        Hardware,
        },
        data() {
            return {
                myTabs: [], // Get tabs from API
                activeTabIndex: 0,
                selectedTabComponent: "overview", // Set this to name of the component received from API
            };
        },
        methods: {
            onTabSelected(tab, index) {
                this.activeTabIndex = index;
                this.selectedTabComponent = tab.component;
            },
            async fetchTabs() {
                // Get tabs from API and update myTabs here
                // Example:
                // this.myTabs = await this.$http.get("/api/tabs");
            },
        },
        created() {
            this.fetchTabs();
        },
    };
</script>
  