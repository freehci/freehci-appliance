<template>
    
    <!-- Rack -->
    <div class="rack-container">
      <div class="rack" v-for="rack in racks" :key="rack.id">
        
        <div class="rack-unit" v-for="unit in rack.Units" :key="unit">
          <div class="unit-number">{{ unit }}</div>
          <div class="unit-content">
            <img src="static/images/rack_rail.png" alt="Rack hole" class="rack-hole rack-hole-l" />
            <div
              class="equipment"
              v-for="equipment in getEquipment(unit, rack.id)"
              :class="['u-' + equipment.size]"
              @click="logClick(equipment)"
              :style="`background-image: url('${equipment.picture}');`"
            >
                <div class="equipment-name" >
                {{ equipment.name }} - ({{ equipment.equipmentid }})
                </div>

                <!-- Hardware Error Status -->
                <div class="equipment-errorstatus dropdown" v-if="equipment.hasError" id="logDropdown" aria-haspopup="true" aria-expanded="false">
                    <i class="fa-solid fa-triangle-exclamation fa-beat-fade" style="color: #f40122;"></i>
                    <!-- The following code is just a POC -->
                    <ul class="dropdown-menu dropdown-menu-custom" aria-labelledby="logDropdown">
                        <li><a class="dropdown-item" href="#"><i class="fa-solid fa-triangle-exclamation" style="color: #f50505;"></i>Jan 24, 2022 02:00:24 - Unable to perform the operation on the device because connection with the device is lost. </a></li>
                        <li><a class="dropdown-item" href="#"><i class="fa-regular fa-flag" style="color: #f7f1b0;"></i>Jan 04, 2022 13:20:38 - Device health has improved. </a></li>
                        <li><a class="dropdown-item" href="#"><i class="fa-regular fa-circle-check" style="color: #78e60a;"></i>Jan 04, 2022 13:19:57 - Device is online. </a></li>
                        <li><a class="dropdown-item" href="#"><i class="fa-solid fa-triangle-exclamation" style="color: #f50505;"></i>Jan 01, 2022 10:05:50 - Device health has deteriorated. </a></li>
                        <li><a class="dropdown-item" href="#"><i class="fa-regular fa-circle-check" style="color: #78e60a;"></i>Jan 01, 2022 08:12:08 - Device is online. </a></li>

                        <!-- Add more lines of log as needed -->
                    </ul>
                </div>
                
                <!-- Hardware Power Status -->
                <!-- <PowerDropdown :equipment="equipment" /> -->

                <div class="equipment-powerstatus dropdown" id="powerDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    <i class="fa-solid fa-power-off" :style="{ color: powerStatusColor(equipment.powerstatus) }"></i>
                    <ul class="dropdown-menu dropdown-menu-custom" aria-labelledby="powerDropdown">
                        <li><a class="dropdown-item" @click="powerOn(equipment)" href="#"><i class="fa-solid fa-power-off" style="color: #00ff00;"></i> Power On</a></li>
                        <li><a class="dropdown-item" @click="powerOff(equipment)" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Power Off</a></li>
                        <li><a class="dropdown-item" @click="powerReset(equipment)" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Reset</a></li>
                        <li><a class="dropdown-item" @click="powerRestart(equipment)" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Restart</a></li>
                        <li><a class="dropdown-item" @click="powerShutdown(equipment)" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Shutdown</a></li>
                    </ul>
                </div>
                
            </div>
            <img src="static/images/rack_rail.png" alt="Rack hole" class="rack-hole rack-hole-r" />
          </div>
        </div>
        <div class="rack-header">
          <div class="rack-name" contenteditable="true"><h2>{{ rack.name }}</h2></div>
          <div class="rack-id" contenteditable="true"><h3>{{ rack.equipmentid }}</h3></div>
        </div>
      </div>

      
    </div>
    
    <EquipmentModal ref="equipmentModal" :initial-selected-equipment="selectedEquipment" @close="closeModal" />


</template>
  
<script>
  import EquipmentModal from "./EquipmentModal.vue";

  export default {
    components: {
        EquipmentModal,
    },
    data() {
      return {
        racks: [
            { id: 1, equipmentid: "RAC-10023", name: "Rack 5", Units: 42 },
            { id: 2, equipmentid: "RAC-10029", name: "Rack 6", Units: 42 },
            { id: 3, equipmentid: "RAC-10003", name: "Rack 7", Units: 42 },
            { id: 4, equipmentid: "RAC-10036", name: "Rack 8", Units: 42 }
        ],
        equipmentList: [
            { id: 1, equipmentid: "SRV-34223", name: "Server 1", dnsName: "iDRAC-F59R2T2", rackId: 1, position: 4, size: 1, picture: "static/images/Dell-1U-Server.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on"},
            { id: 2, equipmentid: "SRV-34629", name: "Server 67", dnsName: "", rackId: 1, position: 42, size: 1, picture: "static/images/Dell-1U-Server.svg", screenshot: "static/images/freehci-rc-esxi.png", hasError: false, powerstatus: "on" },
            { id: 2, equipmentid: "SRV-35330", name: "Server 42", dnsName: "", rackId: 1, position: 41, size: 1, picture: "static/images/Dell-1U-Server.svg", screenshot: "static/images/freehci-rc-esxi.png", hasError: false, powerstatus: "on" },
            { id: 2, equipmentid: "SRV-31993", name: "Server 83", dnsName: "", rackId: 1, position: 40, size: 1, picture: "static/images/Dell-1U-Server.svg", screenshot: "static/images/freehci-rc-esxi.png", hasError: false, powerstatus: "on" },
            { id: 3, equipmentid: "SRV-21844", name: "Router 1", dnsName: "", rackId: 2, position: 2, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 4, equipmentid: "SRV-74001", name: "Server 14", dnsName: "", rackId: 2, position: 4, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: true, powerstatus: "off" },
            { id: 5, equipmentid: "SRV-30541", name: "Server 15", dnsName: "", rackId: 2, position: 6, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 6, equipmentid: "SRV-33932", name: "Server 16", dnsName: "", rackId: 2, position: 8, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 7, equipmentid: "SRV-54789", name: "Server 17", dnsName: "", rackId: 3, position: 10, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 8, equipmentid: "SRV-20922", name: "Server 18", dnsName: "", rackId: 3, position: 12, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 9, equipmentid: "SRV-49562", name: "Server 19", dnsName: "", rackId: 3, position: 14, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 10, equipmentid: "SRV-49391", name: "Server 20", dnsName: "", rackId: 2, position: 16, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-esxi.png", hasError: false, powerstatus: "on" },
            { id: 11, equipmentid: "SRV-32384", name: "Server 21", dnsName: "", rackId: 2, position: 18, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-esxi.png", hasError: false, powerstatus: "on" },
            { id: 12, equipmentid: "SRV-41124", name: "Server 22", dnsName: "", rackId: 2, position: 20, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-esxi.png", hasError: false, powerstatus: "on" },
            { id: 13, equipmentid: "SRV-23340", name: "Server 23", dnsName: "", rackId: 4, position: 22, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 14, equipmentid: "SRV-12109", name: "Server 24", dnsName: "", rackId: 4, position: 24, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "unknown" },
            { id: 15, equipmentid: "SRV-80210", name: "Server 25", dnsName: "", rackId: 2, position: 26, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "unknown" },
            { id: 16, equipmentid: "SRV-21886", name: "Server 26", dnsName: "", rackId: 2, position: 28, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "unknown" },
            { id: 17, equipmentid: "SRV-34223", name: "Server 27", dnsName: "", rackId: 2, position: 30, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 18, equipmentid: "SRV-34223", name: "Server 28", dnsName: "", rackId: 4, position: 32, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 19, equipmentid: "SRV-34223", name: "Server 29", dnsName: "", rackId: 2, position: 34, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { 
                id: 20,
                equipmentid: "SRV-34223", 
                equipmentType: "Server", // Server, Storage, Network, etc. Consider using a lookup table and a foreign key.
                equipmentSubType: "Rackmount", // Rackmount, Blade, etc. Consider using a lookup table and a foreign key.
                equipmentManufacturer: "Dell", // Dell, HP, Cisco, etc. Consider using a lookup table and a foreign key.
                equipmentModel: "PowerEdge R740", // PowerEdge R740, PowerEdge R740XD, etc. Consider using a lookup table and a foreign key.
                equipmentSerialNumber: "F49Q2E7", // F49Q2E7, 9ZQ2E7, etc. Consider using a lookup table and a foreign key.
                equipmentAssetTag: "F49Q2E7", // F49Q2E7, 9ZQ2E7, etc. Consider using a lookup table and a foreign key.
                equipmentExpressServiceCode: "92533481036", // 92533481036, 92533481037, etc. Consider using a lookup table and a foreign key.
                equipmentWarrentyExpiration: "2020-05-20T15:00:00.000Z", // 2020-05-20T15:00:00.000Z, 2020-05-20T15:00:00.000Z, etc. Consider using a lookup table and a foreign key.
                equipmentSupportExpiration: "2020-05-20T15:00:00.000Z", // 2020-05-20T15:00:00.000Z, 2020-05-20T15:00:00.000Z, etc. Consider using a lookup table and a foreign key.
                equipmentWarrantyStatus: "Active", // Active, Expired, etc. Consider using a lookup table and a foreign key.
                equipmentSupportStatus: "Active", // Active, Expired, etc. Consider using a lookup table and a foreign key.
                equipmentSupportLevel: "ProSupport", // ProSupport, ProSupport Plus, etc. Consider using a lookup table and a foreign key.
                equipmentSupportType: "24x7", // 24x7, 9x5, etc. Consider using a lookup table and a foreign key.

                equipmentManagementIp: "10.28.5.217",
                equipmentManagementMac: "00:0A:F7:49:B2:E7",
                equipmentManagementType: "iDRAC",
                equipmentManagementProtocols: "HTTPS , SSH , Telnet , IPMI 2.0 , SNMP , Web , RACADM",
                equipmentManagementHWVersion: "7",
                equipmentManagementFWVersion: "9.00.00",
                equipmentManagementLicense: "iDRAC9 Enterprise",
                equipmentManagementLicenseExpiration: "N/A",
                equipmentManagementLicenseStatus: "Licensed",
                equipmentManagementLicenseType: "Enterprise",
                equipmentManagementLicenseVersion: "9",
                equipmentManagementLicenseFeatures: "Dedicated NIC , iDRAC Direct , Quick Sync 2 , Redfish API , REST API , Serial over LAN , vFlash",
                equipmentManagementLicenseNotes: "",
                equipmentManagementLicenseMaxSessions: "Unlimited",
                equipmentManagementNotes: "",
                equipmentManagementStatus: "Up",
                equipmentManagementStatusMessage: "",
                equipmentManagementLastUpdate: "2020-05-20T15:00:00.000Z",
                equipmentManagementLastUpdateBy: "admin",

                name: "Server 30",
                dnsName: "iDRAC-F49Q2E7", 
                model: "PowerEdge R740",
                identifier: "F49Q2E7",
                assetTag: "F49Q2E7",
                expressServiceCode: "92533481036",
                managementIp: "10.28.5.217 (iDRAC)",

                systemUpTime: "1 day, 1 hour, 2 minutes, 3 seconds",
                connectionState: "Connected",
                totalSystemMemory: "128 GB",
                populatedDimmSlots: "8",
                totalDimmSlots: "24",
                processorSummary: "Intel(R) Xeon(R) Gold 6248 CPU @ 2.50GHz",
                processorCount: "2",
                processorCores: "24",
                processorThreads: "48",
                processorSpeed: "2.5 GHz",
                processorType: "Intel(R) Xeon(R) Gold 6248 CPU @ 2.50GHz",
                processorStatus: "Enabled",
                processorCache: "24 MB",
                processorCacheType: "L3",
                processorCacheSpeed: "2.5 GHz",
                processorCacheStatus: "Enabled",
                processorCacheSize: "24 MB",
                processorCacheAssociativity: "Fully Associative",
                processorCacheLineSize: "64",
                processorCacheMaxSize: "24 MB",
                processorCacheMaxSpeed: "2.5 GHz",
                osName: "Microsoft Windows Server 2016 Standard",
                osVersion: "Version 10.0 (Build 14393) (x64)",
                osArchitecture: "64-bit",
                osLanguage: "English (United States)",
                osBootTime: "2020-04-08T09:00:00Z",
                osLastBootTime: "2020-04-08T09:00:00Z",
                osLastShutdownTime: "2020-04-08T09:00:00Z",
                osLastRebootTime: "2020-04-08T09:00:00Z",
                osLastLogonTime: "2020-04-08T09:00:00Z",
                osLastLogoffTime: "2020-04-08T09:00:00Z",
                osLastLogonUser: "Administrator",
                osLastLogonUserId: "S-1-5-21-1234567890-1234567890-1234567890-500",
                osLastLogonDomain: "WORKGROUP",
                osLastLogonDomainId: "S-1-5-21-1234567890-1234567890-1234567890-1000",
                osHostname: "WIN-1234567890",
                osDomain: "WORKGROUP",
                osBrandImage: "static/images/Brands/Windows_Server_2016_logo.svg",
                rackId: 2, 
                position: 36, 
                size: 2, 
                picture: "static/images/R740XD-24-Front.svg", 
                screenshot: "static/images/freehci-rc-windows.png", 
                hasError: false, 
                powerstatus: "on" 
            },
            { id: 21, equipmentid: "SRV-34223", name: "Server 31", dnsName: "", rackId: 4, position: 38, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" },
            { id: 22, equipmentid: "SRV-34223", name: "Server 32", dnsName: "", rackId: 2, position: 40, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: true, powerstatus: "on" },
            { id: 23, equipmentid: "SRV-34223", name: "Server 33", dnsName: "", rackId: 1, position: 39, size: 2, picture: "static/images/R740XD-24-Front.svg", screenshot: "static/images/freehci-rc-windows.png", hasError: false, powerstatus: "on" }
        ],
        selectedEquipment: null,
      };
    },
    methods: {
        getEquipment(unit, rackId) {
            return this.equipmentList.filter(
                (equipment) => equipment.position === unit && equipment.rackId === rackId
            );
        },
        logClick(equipment) { // TODO: Change the name of this function to something more appropriate, e.g., equipmentClick
            console.log(`Clicked on equipment: ${equipment.name}`);
            // Implement additional logic to handle the click event, e.g., write to a log

            this.selectedEquipment = equipment;
            this.$nextTick(() => {
                this.$refs.equipmentModal.openModal();
            });
            
        },
        closeModal() {
          this.selectedEquipment = null;
        },
        powerStatusColor(status) {
            switch (status) {
                case 'off':
                    return '#f40122';
                case 'on':
                    return '#00ff00';
                case 'unknown':
                default:
                    return '#f4f401';
            }
        },
        powerOn(equipment) {
            console.log(`Powering on equipment: ${equipment.name}`);
            // Implement additional logic to handle the power on event, e.g., write to a log
        },
        powerOff(equipment) {
            console.log(`Powering off equipment: ${equipment.name}`);
            // Implement additional logic to handle the power off event, e.g., write to a log
        },
        powerCycle(equipment) {
            console.log(`Power cycling equipment: ${equipment.name}`);
            // Implement additional logic to handle the power cycle event, e.g., write to a log
        },
        powerReset(equipment) {
            console.log(`Resetting equipment: ${equipment.name}`);
            // Implement additional logic to handle the power status event, e.g., write to a log
        },
        powerRestart(equipment) {
            console.log(`Restarting equipment: ${equipment.name}`);
            // Implement additional logic to handle the power status event, e.g., write to a log
        },
        powerShutdown(equipment) {
            console.log(`Shutting down equipment: ${equipment.name}`);
            // Implement additional logic to handle the power status event, e.g., write to a log
        }
    },
  };
</script>
  
<style>
    .rack-container {
        display: flex;
        flex-direction: row;
        gap: 2rem;
        padding-bottom: 10rem;
    }
    
    .rack {
        /* border: 1px solid #ccc; */ 
        
        border-bottom: 1px solid #ccc;

        display: flex;
        flex-direction: column-reverse;
    }

    .rack-header {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 44px;
        width: 465px;
        
        border: solid 1px #ccc;
        background-color: #343a40!important;
    }

    .rack-name {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 44px;
        width: 465px;
        border: hidden;
        border-bottom: solid 1px #ccc;
        
    }

    .rack-name h2 {
        font-size: 1.5rem;
    }

    .rack-id {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 44px;
        width: 465px;
        border: hidden;
        border-bottom: solid 1px #ccc;
    }

    .rack-id h2 {
        font-size: 1.5rem;
    }

    .rack-id h3 {
        font-size: 1.0rem;
    }
    
    .rack-unit {
        display: flex;
        align-items: center;
        position: relative;
        border-top: 1px solid #ccc;
        border: hidden;
    }
  
    .unit-number {
        position: absolute;
        left: -20px;
    }
    
    .unit-content {
        flex-grow: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        height: 44px;
        width: 465px;
        border: hidden;
        border-left: 1px solid #ccc;
        border-right: 1px solid #ccc;
    }
  
    .equipment {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #aaa;
        border-radius: 4px;
        border: hidden;
        padding: 4px;
        width: 465px;
        position: relative;
    }

    .equipment:hover {
        border: 1px solid red;
        box-sizing: border-box;
        cursor: pointer;
    }

    .equipment-errorstatus {
        position: absolute;
        top: 4px;
        left: 4px;
        width: 25px;
        height: 25px;
        background-color: rgba(0, 0, 0, 0.5); /* Add semi-transparent background */
        /* background-color: red; */ 
        border-radius: 50%;
        display: flex; /* Add this to enable flexbox */
        align-items: center; /* Center vertically */
        justify-content: center; /* Center horizontally */
    }
    
    .equipment-errorstatus:hover .dropdown-menu {
        display: block;
    }

    .powerstatus-container {
        position: absolute;
        bottom: 4px;
        right: 4px;
        width: 25px;
        height: 25px;
        
        display: flex; /* Add this to enable flexbox */
        align-items: center; /* Center vertically */
        justify-content: center; /* Center horizontally */
    }
    .equipment-powerstatus {
        position: absolute;
        bottom: 4px;
        right: 4px;
        width: 25px;
        height: 25px;
        background-color: rgba(0, 0, 0, 0.5); /* Add semi-transparent background */
        border-radius: 50%;
        display: flex; /* Add this to enable flexbox */
        align-items: center; /* Center vertically */
        justify-content: center; /* Center horizontally */
    }

    .equipment-name {
        display: flex;
        justify-content: center;
        align-items: center;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;

        /* some adjustments to improve readability */
        background-color: rgba(0, 0, 0, 0.5); /* Add semi-transparent background */
        padding: 2px 4px; /* Add some padding around the text */
        color: #fff; /* White text */
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Add some shadow around the text */
    }


    .equipment-name img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .rack-hole {
        position: absolute;
        z-index: -3;
    }
    
    .rack-hole-l {
        width: 20px;
        height: 44px;
        left: 0;
        
    }
  
    .rack-hole-r {
        width: 20px;
        height: 48px;
        transform: rotate(180deg);
        right: 0;
    }

    .u-1 {
        height: 44px;
    }
    
    .u-2 {
        height: 88px;
        bottom: -22px;
        /*
        top: -50%;
        transform: translateY(50%);
        */
    }
</style>