<!-- Tabs.vue -->
<template>
    <ul class="nav nav-tabs">
      <li
        class="nav-item"
        v-for="(tab, index) in tabs"
        :key="index"
        :class="{ disabled: tab.disabled }"
      >
        <a
          class="nav-link"
          :class="{ active: index === activeIndex, disabled: tab.disabled }"
          @click="!tab.disabled && selectTab(index)"
          href="#"
        >
          <i :class="tab.icon"></i> {{ tab.title }}
        </a>
      </li>
    </ul>
</template>
  
<script>
  export default {
    props: {
      tabs: {
        type: Array,
        required: true,
      },
      activeIndex: {
        type: Number,
        default: 0,
      },
    },
    methods: {
      selectTab(index) {
        this.$emit('tab-selected', index);
      },
    },
  };
</script>
  
<style scoped>
  .disabled {
    pointer-events: none;
    opacity: 0.6;
  }
</style>
  