<!-- 
    File:EquipmentModal.vue 
    Whis Modal is used to display information about a specific equipment.
    It is called from the Rack.vue component.
    Data is passed to this component from the Rack.vue component.

    This is a copy of the EquipmentModal.vue file.  It is a backup in case I mess up the original.
-->
<template>
    <div class="modal" :class="{show: showModal}" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedEquipment ? selectedEquipment.name : '' }} - ({{ selectedEquipment ? selectedEquipment.equipmentid : '' }})</h5>
            <button type="button" class="close" @click="closeModal">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <!-- Modal body content goes here -->
            <div class="row">
                <div class="col-6">
                    <ul class="nav nav-tabs">
                        <li class="nav-item">
                            <a class="nav-link active" href="#">Tab 1</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">Tab 2</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">Tab 3</a>
                        </li>
                    </ul>
                    <div class="mt-3">
                        <img :src="selectedEquipment ? selectedEquipment.picture : ''" alt="Equipment Image" class="img-thumbnail" style="max-height: 50%;">

                    </div>
                    <div class="mt-3">
                        <button class="btn btn-primary">Virtual Media</button>
                        <button class="btn btn-primary">Power</button>
                        <button class="btn btn-primary">Connect</button>
                    </div>
                    <div class="mt-3">
                        <!-- Add the text you want to display under the buttons -->
                        <p>Some text here...</p>
                    </div>
                </div>
                <div class="col-6">
                    <h2>Information</h2>
                    
                    <p>DNS Name: {{ selectedEquipment ? selectedEquipment.dnsName : '' }}</p>

                    <p>Model: {{ selectedEquipment ? selectedEquipment.model : ''}}</p>
                    <p>Identifier: {{ selectedEquipment ? selectedEquipment.identifier : '' }}</p>
                    <p>Asset Tag: {{ selectedEquipment ? selectedEquipment.assetTag : ''}}</p>
                    <p>Express Service Code: {{ selectedEquipment ? selectedEquipment.expressServiceCode : ''}}</p>
                    <p>Management IP: {{ selectedEquipment ? selectedEquipment.managementIp : ''}}</p>
                    <p>System Up Time: {{ selectedEquipment ? selectedEquipment.systemUpTime : ''}}</p>
                    <p>Power State: {{ selectedEquipment ? selectedEquipment.powerState : ''}}</p>
                    <p>Connection State: {{ selectedEquipment ? selectedEquipment.connectionState : ''}}</p>
                    <p>Total System Memory: {{ selectedEquipment ? selectedEquipment.totalSystemMemory : '' }}</p>
                    <p>Populated DIMM Slots: {{ selectedEquipment ? selectedEquipment.populatedDimmSlots : ''}}</p>
                    <p>Total DIMM Slots: {{ selectedEquipment ? selectedEquipment.totalDimmSlots : '' }}</p>
                    <p>Processor Summary: {{ selectedEquipment ? selectedEquipment.processorSummary : ''}}</p>

                    <h2>Operating System Information (from iDRAC/ISM)</h2>
                    <p>OS Name: {{ selectedEquipment ? selectedEquipment.osName : ''}}</p>
                    <p>OS Version: {{ selectedEquipment ? selectedEquipment.osVersion : ''}}</p>
                    <p>OS Hostname: {{ selectedEquipment ? selectedEquipment.osHostname : ''}}</p>
                </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>
</template>
  

<script>
    export default {
        data() {
            return {
            showModal: false,
            // ...
            };
        },
        props: {
            initialSelectedEquipment: Object,
        },
        computed: {
            selectedEquipment() {
            return this.initialSelectedEquipment;
            },
        },
        methods: {
            // Any methods goes here...
            openModal() {
            console.log("openModal called");
            console.log("Selected equipment in openModal: ", this.selectedEquipment);
            this.showModal = true;
            },
            closeModal() {
            this.showModal = false;
            this.$emit("close");
            },
        },

        mounted() {
            console.log("Selected equipment in EquipmentModal: ", this.selectedEquipment);
        },

        watch: {
            selectedEquipment: {
            immediate: true,
            handler(newValue, oldValue) {
                console.log("Selected equipment in EquipmentModal: ", newValue);
            },
            },
        },
    };

</script>

<style scoped>
    .modal {
        display: none;
        position: fixed;
        z-index: 4050;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        outline: 0;
        overflow-x: hidden;
        overflow-y: auto;
        background-color: rgba(0, 0, 0, 0.5);
    }
    .modal.show {
        display: block;
    }

    .modal-dialog {
        max-width: 600px; /* Du kan endre dette tallet til ønsket bredde */
        margin: 30px auto;
        width: 560px !important;
    }

    .modal-content {
        position: relative;
        margin: 10% auto;
        padding: 20px;
        width: 80%;
        max-width: 700px;
        background-color: #302727;
        border-radius: 4px;
    }
</style>