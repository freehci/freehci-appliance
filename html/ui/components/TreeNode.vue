<template>
    <li>
      <div>
        <i class="fas fa-server"></i> <!-- You can use Font Awesome icons or any other icon library -->
        {{ node.label }}
      </div>
      <ul v-if="node.children && node.children.length">
        <tree-node v-for="(child, index) in node.children" :key="index" :node="child" />
      </ul>
    </li>
  </template>
  
<script>
  export default {
    props: {
      node: {
        type: Object,
        required: true,
      },
    },
  };
</script>
  
<style scoped>
  li {
    list-style-type: none;
  }
</style>
  