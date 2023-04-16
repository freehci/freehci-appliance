<template>
    <footer class="footer">
      <div class="footer-toggle" @click="toggleFooter">
        <i class="fas fa-chevron-down" v-if="footerExpanded"></i>
        <i class="fas fa-chevron-up" v-else></i>
        <span>Event Log</span>
      </div>
      <div class="footer-content" v-show="footerExpanded">
        <div class="event-log mt-2">
            <div class="event-log-header">
            <div class="row">
                <div class="col-md-2">Time</div>
                <div class="col-md-3">Task / Event</div>
                <div class="col-md-2">Status</div>
                <div class="col-md-2">Progress</div>
                <div class="col-md-3">User</div>
            </div>
            </div>
            <div class="event-log-content">
            <ul class="list-group">
                <li class="list-group-item" v-for="event in eventLog" :key="event.id">
                    <div class="row">
                        <div class="col-md-2">{{ event.time }}</div>
                        <div class="col-md-3">{{ event.task }}</div>
                        <div class="col-md-2">{{ event.status }}</div>
                        <div class="col-md-2">{{ event.progress }}</div>
                        <div class="col-md-3">{{ event.user }}</div>
                    </div>
                </li>
            </ul>
            </div>
        </div>
      </div>
    </footer>
</template>
  
  
<script>
    export default {
        data() {
            return {
                footerExpanded: false,
                eventLog: [
                    {
                        id: 1,
                        time: '09:30:00',
                        task: 'Login',
                        status: 'Success',
                        progress: '100%',
                        user: 'John Doe',
                    },
                    {
                        id: 2,
                        time: '10:15:00',
                        task: 'Create post',
                        status: 'Success',
                        progress: '100%',
                        user: 'John Doe',
                    },
                    
                    {
                        id: 3,
                        time: '12:27:00',
                        task: 'Migrate SRV-01 to vcenter-40',
                        status: 'Active',
                        progress: '39%',
                        user: 'Jane Doe',
                    },
                    
                    {
                        id: 4,
                        time: '12:30:00',
                        task: 'Remove snapshot from WEB-19',
                        status: 'Success',
                        progress: '100%',
                        user: 'John Doe',
                    },
                    // Add more events as needed
                ],
            };
        },
        methods: {
            toggleFooter() {
                this.footerExpanded = !this.footerExpanded;
            },
        },
    };
</script>

<style>
    
    .event-log {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
    }

    .event-log-header {
        background-color: #343a40;
        color: #fff;
        padding: 0.5rem;
    }

    .event-log-content {
        max-height: 300px;
        overflow-y: auto;
    }

    .list-group-item {
       background-color: #f1f1f1;
        color: #333;
        border-bottom: 1px solid #ccc;
    }

</style>