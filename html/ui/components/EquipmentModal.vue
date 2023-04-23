<!-- 
    File:EquipmentModal.vue 
    Whis Modal is used to display information about a specific equipment.
    It is called from the Rack.vue component.
    Data is passed to this component from the Rack.vue component.
-->
<template>
    <div>
      <button @click="showModal = true">Open Modal</button>
      <div class="custom-modal" v-show="showModal" @click.self="showModal = false">
        <div class="custom-modal-dialog">
          <div class="custom-modal-content">
            <div class="custom-modal-header">
                <h5>{{ selectedEquipment ? selectedEquipment.name : '' }} - ({{ selectedEquipment ? selectedEquipment.equipmentid : '' }})</h5>
                <button class="btn btn-primary" @click="showModal = false">
                    Close
                </button>
            </div>
            <div class="custom-modal-body">
                <!-- Modal body content goes here -->
                <ul class="nav nav-tabs">
                        <li class="nav-item">
                            <a class="nav-link active" href="#"><i class="fa-solid fa-house"></i> Overview</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="fa-solid fa-temperature-low"></i> Environment</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="fa-solid fa-microchip"></i> Hardware</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="fa-brands fa-windows"></i> OS Info</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="fa-solid fa-list-check"></i> Log</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="fa-solid fa-sliders"></i> Settings</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="fa-solid fa-location-dot"></i> Location</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#"><i class="fa-solid fa-file-pdf"></i> Documentation</a>
                        </li>
                    </ul>
                <div class="row">
                    
                <div class="col-4">
                    <h6 class="mb-3 text-primary">Server Console</h6>
                    <div class="mt-3 position-relative">
                        
                        <div v-if="isLoading" class="spinner-overlay">
                            <i class="fa-solid fa-spinner fa-spin-pulse fa-2xl loading-spinner" ></i>
                        </div>
                        <img :src="selectedEquipment ? selectedEquipment.screenshot : ''" alt="Equipment screenshot" class="img-thumbnail" style="max-height: 50%;" id="remote-console" >

                    </div>

                    
                    <div class="mt-3">
                        <button class="btn btn-primary"><i class="fa-solid fa-compact-disc fa-spin-pulse"></i> Virtual Media</button>
                        <button class="btn btn-primary"><i class="fa-solid fa-power-off" style="color: #11d01e;"></i> Power</button>
                        <button class="btn btn-primary"><i class="fa-solid fa-desktop"></i> Connect</button>
                    </div>
                    <div class="mt-3">
                        <!-- Add the text you want to display under the buttons -->
                        <p>Server Image</p>
                        <img :src="selectedEquipment ? selectedEquipment.picture : ''" alt="Equipment screenshot" class="img-thumbnail" style="max-height: 50%;">
                    </div>
                    <div class="mt-3">
                        <!-- Add the text you want to display under the buttons -->
                        <p>Operating System</p>
                        <img :src="selectedEquipment ? selectedEquipment.osBrandImage : ''" alt="Equipment screenshot" class="img-thumbnail" style="max-height: 50%;">
                    </div>
                </div>
                <div class="col-8">
                    <h6 class="mb-3 text-primary">Information</h6>
                    
                    <p>DNS Name: {{ selectedEquipment ? selectedEquipment.dnsName : '' }}</p>

                    <p>Model: {{ selectedEquipment ? selectedEquipment.model : ''}}</p>
                    <p>Identifier: {{ selectedEquipment ? selectedEquipment.identifier : '' }}</p>
                    <p>Asset Tag: {{ selectedEquipment ? selectedEquipment.assetTag : ''}}</p>
                    <p>Express Service Code: {{ selectedEquipment ? selectedEquipment.expressServiceCode : ''}}</p>
                    <p>Management IP: {{ selectedEquipment ? selectedEquipment.managementIp : ''}}</p>
                    <p>System Up Time: {{ selectedEquipment ? selectedEquipment.systemUpTime : ''}}</p>
                    <p>Power State: {{ selectedEquipment ? selectedEquipment.powerstatus : ''}}</p>
                    <p>Connection State: {{ selectedEquipment ? selectedEquipment.connectionState : ''}}</p>
                    <p>Total System Memory: {{ selectedEquipment ? selectedEquipment.totalSystemMemory : '' }}</p>
                    <p>Populated DIMM Slots: {{ selectedEquipment ? selectedEquipment.populatedDimmSlots : ''}}</p>
                    <p>Total DIMM Slots: {{ selectedEquipment ? selectedEquipment.totalDimmSlots : '' }}</p>
                    <p>Processor Summary: {{ selectedEquipment ? selectedEquipment.processorSummary : ''}}</p>

                    <h6 class="mb-3 text-primary">Operating System Information (from iDRAC/ISM)</h6>
                    <p>OS Name: {{ selectedEquipment ? selectedEquipment.osName : ''}}</p>
                    <p>OS Version: {{ selectedEquipment ? selectedEquipment.osVersion : ''}}</p>
                    <p>OS Hostname: {{ selectedEquipment ? selectedEquipment.osHostname : ''}}</p>
                </div>
            </div>
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
                selectedEquipment: this.initialSelectedEquipment,
                showModal: false,
                isLoading: false,
            // ...
            };
        },
        props: {
            initialSelectedEquipment: Object,
        },
        computed: {
            selectedEquipment() { // TODO: Rename this to computedSelectedEquipment and change all references to it as this throws an warning in the console
            return this.initialSelectedEquipment;
            },
        },
        methods: {
            // Any methods goes here...
            openModal() {
                console.log("openModal called");
                console.log("Selected equipment in openModal: ", this.selectedEquipment);
                this.showModal = true;
                this.showLoadingSpinner();
            },
            closeModal() {
                this.showModal = false;
                this.$emit("close");
            },
            showLoadingSpinner() {
                this.isLoading = true;
                setTimeout(() => {
                    this.isLoading = false;
                }, 3000);
            },
            
        },

        mounted() {
            console.log("Selected equipment in EquipmentModal: ", this.selectedEquipment);
            this.showSpinner = true;
        },

        
    };

</script>

<style scoped>
    .custom-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .custom-modal-dialog {
        width: 1300px;
        max-width: 90%;
        background-color: #1A233A;
        border-radius: 8px;
        overflow: hidden;
    }

    .custom-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid #596280;
    }

    .custom-modal-body {
        padding: 1rem;
    }

    .img-thumbnail {
        padding: 0.1rem;
        background-color: #596280;
        border: 1px solid #596280;
        border-radius: 0.25rem;
        max-width: 100%;
        height: auto;
    }

    #remote-console :hover{ /* This don't work. Consider using custom css instead */
        cursor: pointer;
    }

    .position-relative {
        position: relative;
    }

    .spinner-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: rgba(51, 47, 47, 0.5);
    }

    .loading-spinner {
        color:#d4d8e6;
    }

</style>
