<template>
    <footer class="footer">
      <div class="footer-toggle" @click="toggleFooter">
        <i class="fas fa-chevron-up" v-if="footerExpanded"></i>
        <i class="fas fa-chevron-down" v-else></i>
        <span>Event Log</span>
      </div>
      <div class="footer-content" v-show="footerExpanded">
        <div class="event-log">
          <ul>
            <li v-for="event in eventLog" :key="event.id">{{ event.timestamp }} - {{ event.message }}</li>
          </ul>
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
                { id: 1, timestamp: '2023-04-15 09:30:00', message: 'User logged in.' },
                { id: 2, timestamp: '2023-04-15 10:15:00', message: 'User created a new post.' },
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


</style>