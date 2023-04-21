const options = {
    moduleCache: {
      vue: Vue
    },
    async getFile(url) {
      const res = await fetch(url);
      if (!res.ok)
        throw Object.assign(new Error(res.statusText + ' ' + url), { res });
      return {
        getContentData: asBinary => asBinary ? res.arrayBuffer() : res.text(),
      }
    },
    addStyle(textContent) {
      const style = Object.assign(document.createElement('style'), { textContent });
      const ref = document.head.getElementsByTagName('style')[0] || null;
      document.head.insertBefore(style, ref);
    },
    
}


const { loadModule } = window['vue3-sfc-loader'];

const app = Vue.createApp({
    
    data() {
      return {
        currentComponent: null,
        footerComponent: null,
      };
    },
    provide() {
      return {
        apiBaseUrl, // Provide the apiBaseUrl here
      };
    },
    methods: {
      async loadComponent(name) {
        const url = `/ui/components/${name}.vue`;
        try {
          const component = await loadModule(url, options);
          this.currentComponent = Vue.markRaw(Vue.defineAsyncComponent(() => Promise.resolve(component)));
        } catch (error) {
          console.error('Failed to load component:', error);
        }
      },
      logOff() {
        // Log off the user
        window.location.href = '/ui/logoff';
      },
      async loadFooterComponent() {
        const name = 'Footer';
        const url = `/ui/components/${name}.vue`;
        try {
          const component = await loadModule(url, options);
          this.footerComponent = Vue.markRaw(Vue.defineAsyncComponent(() => Promise.resolve(component)));
        } catch (error) {
          console.error('Failed to load Footer component:', error);
        }
      },      
    },
    mounted() {
      // Load standard component at startup, eg. 'Users'
      this.loadComponent('Dashboard');
      this.loadFooterComponent();
    },
    
});


app.mount('#app');