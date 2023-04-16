<template>
    <div>
      <ul>
        <tree-node v-for="(item, index) in treeData" :key="index" :node="item" />
      </ul>
    </div>
</template>
  
<script>
  import TreeNode from "./TreeNode.vue";
  
  export default {
    components: {
      TreeNode,
    },
    props: {
      treeData: {
        type: Array,
        required: true,
      },
    },
  };
</script>
<style>

</style>