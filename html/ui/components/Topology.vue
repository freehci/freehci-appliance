<template>
    <div>
      <tree :treeData="jsonData" />
    </div>
  </template>
  
  <script>
  import Tree from "./Tree.vue";
  
  export default {
    components: {
      Tree,
    },
    data() {
      return {
        jsonData: [
          {
            label: "FreeHCI Orchestrator (This Server)",
            type: "orchestrator",
            children: [
              {
                label: "FreeHCI Appliance",
                type: "appliance",
                children: [{ 
                    label: "Server-1",
                    type: "Linux",
                }, { 
                    label: "Server-2",
                    type: "Linux",
                }],
              },
              {
                label: "WIN-SRV-01",
                type: "Windows",
              },
            ],
          },
          {
            label: "WIN-SRV-02",
            type: "Windows",
          },
          {
            label: "FreeHCI Appliance",
            type: "appliance",
            children: [
                {
                    label: "ESXi-1",
                    type: "esxi",
                }],
          },
        ],
      };
    },
  };
  </script>
  