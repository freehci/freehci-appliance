<template>
    <div>
        <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item" @click="selectTab('networking')">
                <a class="nav-link" data-toggle="tab" href="#networking" role="tab" :class="{ active: selectedTab === 'networking' }">Networking</a>
            </li>
            <li class="nav-item" @click="selectTab('componentsAndServices')">
                <a class="nav-link" data-toggle="tab" href="#componentsAndServices" role="tab" :class="{ active: selectedTab === 'componentsAndServices' }">Components and services</a>
            </li>
            <li class="nav-item" @click="selectTab('Appliance')">
                <a class="nav-link" data-toggle="tab" href="#Appliance" role="tab" :class="{ active: selectedTab === 'Appliance' }">Appliance</a>
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
                <h3>Components And Services</h3>
                <table class="table table-dark table-striped">
                <thead>
                    <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Help Text</th>
                    <th>Help URL</th>
                    <th>Enabled</th>
                    <th>Status</th>
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
                    </tr>
                </tbody>
                </table>
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
                <button type="button" class="btn btn-primary">Save</button>
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
                { name: 'Service 1', description: 'This is service 1' ,helptext: 'Help text for service 1', helpurl:'https://some.url.com', enabled: true, status: 'running' },
                { name: 'Service 2', description: 'This is service 2' ,helptext: 'Help text for service 2', helpurl:'',enabled: false, status: 'stopped' },
                { name: 'Service 3', description: 'This is service 3' ,helptext: 'Help text for service 3', helpurl:'',enabled: true, status: 'running' },
                { name: 'Service 4', description: 'This is service 4' ,helptext: 'Help text for service 4', helpurl:'',enabled: true, status: 'running' },
                { name: 'Service 5', description: 'This is service 5' ,helptext: 'Help text for service 5', helpurl:'',enabled: true, status: 'starting' },
                { name: 'Service 6', description: 'This is service 6' ,helptext: 'Help text for service 6', helpurl:'',enabled: true, status: 'error' },
            ],
            };
        },
        methods: {
            selectTab(tab) {
            this.selectedTab = tab;
            },  
            updateService(index) {
            // Oppdater tjenesten i back-end, f.eks. med en API-kall
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
                    default:
                        return 'fa-question-circle text-muted';
                }
            },
        },
    };
</script>

<style>
    /* Bootstrap tab styles */
    .nav-tabs .nav-link {
        border: 1px solid transparent;
        border-top-left-radius: 0.25rem;
        border-top-right-radius: 0.25rem;
    }

    .nav-tabs .nav-link:hover {
        border-color: #e9ecef #e9ecef #dee2e6;
    }

    .nav-tabs .nav-link.active {
        color: #495057;
        background-color: #fff;
        border-color: #dee2e6 #dee2e6 #fff;
    }
</style>