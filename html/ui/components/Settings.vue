<template>
    <div>
        <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item" @click="selectTab('networking')">
                <a class="nav-link" data-toggle="tab" href="#networking" role="tab" :class="{ active: selectedTab === 'networking' }"><i class="fas fa-network-wired"></i> Networking</a>
            </li>
            <li class="nav-item" @click="selectTab('componentsAndServices')">
                <a class="nav-link" data-toggle="tab" href="#componentsAndServices" role="tab" :class="{ active: selectedTab === 'componentsAndServices' }"><i class="fas fa-cogs"></i> Components and services</a>
            </li>
            <li class="nav-item" @click="selectTab('Appliance')">
                <a class="nav-link" data-toggle="tab" href="#Appliance" role="tab" :class="{ active: selectedTab === 'Appliance' }"><i class="fas fa-server"></i> Appliance</a>
            </li>
        </ul>

        <div class="tab-content">

            <!-- Networking -->
            <div id="networking" class="tab-pane fade" :class="{ active: selectedTab === 'networking', show: selectedTab === 'networking' }">
                <h3>Networking</h3>
                <p>Some content.</p>
            </div>

            <!-- Components and services -->
            <div id="componentsAndServices" class="tab-pane fade" :class="{ active: selectedTab === 'componentsAndServices', show: selectedTab === 'componentsAndServices' }">
                <h3><i class="fas fa-cogs"></i> Components And Services</h3>
                <table class="table table-dark table-striped">
                <thead>
                    <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Help Text</th>
                    <th>Help URL</th>
                    <th>Enabled</th>
                    <th>Status</th>
                    <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(service, index) in services" :key="index">
                    <td>{{ service.name }}</td>
                    <td>{{ service.description }}</td>
                    <td>{{ service.helptext }}</td>
                    <td>
                        <template v-if="service.helpurl">
                        <a :href="service.helpurl" target="_blank" rel="noopener noreferrer">{{ service.helpurl }}</a>
                        </template>
                        <template v-else>
                        -
                        </template>
                    </td>
                    
                    <td>
                        <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" :id="'enabled-' + index" v-model="service.enabled" @change="updateService(index)">
                        <!--
                        <label class="form-check-label" :for="'enabled-' + index">Enabled</label>
                        -->
                        </div>
                    </td>
                    <td>
                        <i class="fas" :class="getStatusIcon(service.status)" :title="service.status"></i>
                    </td>
                    <td>
                        <div class="dropdown">
                            <button class="btn btn-secondary dropdown-toggle" type="button" id="actionDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                <i class="fas fa-bars"></i>
                            </button>
                            <div class="dropdown-menu" aria-labelledby="actionDropdown">
                                <a class="dropdown-item" href="#" @click="startService(service)"><i class="fa-solid fa-play"></i> Start</a>
                                <a class="dropdown-item" href="#" @click="stopService(service)"><i class="fa-solid fa-stop"></i> Stop</a>
                                <a class="dropdown-item" href="#" @click="restartService(service)"><i class="fa-solid fa-rotate"></i> Restart</a>
                            </div>
                        </div>
                        <!--
                        <div class="action-buttons">
                            <button class="btn btn-sm btn-success" @click="startService(service)">Start</button>
                            <button class="btn btn-sm btn-danger" @click="stopService(service)">Stop</button>
                            <button class="btn btn-sm btn-warning" @click="restartService(service)">Restart</button>
                        </div>
                        -->
                    </td>
                    </tr>
                </tbody>
                </table>
                <div class="mb-3">
                    <button type="button" class="btn btn-primary">New Service</button>
                    <button type="button" class="btn btn-primary">Remove Service</button>
                </div>
            </div>

            <!-- Appliance -->
            <div id="Appliance" class="tab-pane fade" :class="{ active: selectedTab === 'Appliance', show: selectedTab === 'Appliance' }">
                <h3>Menu 2</h3>
                <p>Some content in menu 2.</p>
            </div>
        </div>

        <!-- Save button -->
        <div class="row">
            <div class="col-md-12">
                <button type="button" class="btn btn-primary"><i class="fa-solid fa-floppy-disk"></i> Save</button>
            </div>
        </div>
    </div>
</template>
  
<script>
    export default {
        data() {
            return {
                selectedTab: 'networking',
                services: [
                    { name: 'Metrics collector', description: 'This is service 1' ,helptext: 'Help text for service 1', helpurl:'https://some.url.com', enabled: true, status: 'running' },
                    { name: 'Scheduler', description: 'This is service 2' ,helptext: 'Help text for service 2', helpurl:'',enabled: false, status: 'stopped' },
                    { name: 'Device discovery', description: 'This is service 3' ,helptext: 'Help text for service 3', helpurl:'',enabled: true, status: 'running' },
                    { name: 'Update Service', description: 'This is service 4' ,helptext: 'Help text for service 4', helpurl:'',enabled: true, status: 'running' },
                    { name: 'SNMP Server', description: 'This is service 5' ,helptext: 'Help text for service 5', helpurl:'',enabled: true, status: 'starting' },
                    { name: 'Redfish Service', description: 'This is service 6' ,helptext: 'Help text for service 6', helpurl:'',enabled: true, status: 'error' },
                ],
            };
        },
        methods: {
            selectTab(tab) {
            this.selectedTab = tab;
            },  
            updateService(index) {
            // Update service in back-end, e.g. using api.
                console.log('Service updated:', this.services[index]);
            },
            getStatusIcon(status) {
                switch (status) {
                    case 'running':
                        return 'fa-play-circle text-success';
                    case 'stopped':
                        return 'fa-stop-circle text-danger';
                    case 'error':
                        return 'fa-exclamation-circle text-warning';
                    case 'starting':
                        return 'fa-circle-notch fa-spin text-primary';
                    case 'pending':
                        return 'fa-hourglass-start text-primary';

                    default:
                        return 'fa-question-circle text-muted';
                }
            },
            startService(service) {
                // Implement your logic for starting the service
                console.log(`Starting ${service.name}, - ${service.description}`);

            },
            stopService(service) {
                // Implement your logic for stopping the service
                console.log(`Stopping ${service.name}`);
            },
            restartService(service) {
                // Implement your logic for restarting the service
                console.log(`Restarting ${service.name}`);
            },
        },
    };
</script>

<style>
    
    .action-buttons {
        display: flex;
    }

    .action-buttons button:not(:last-child) {
        margin-right: 10px; /* Change this to adjust space between buttons */
    }

    

</style>