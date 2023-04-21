<template>
    <div class="powerstatus-container dropdown" @click="toggleDropdown" :class="{ 'open': isOpen }">
        <div class="equipment-powerstatus">
            <i class="fa-solid fa-power-off" :style="{ color: powerStatusColor(equipment.powerstatus) }"></i>
        </div>
        
            <ul class="dropdown-menu" v-show="isOpen">
                <li><a class="dropdown-item" href="#"><i class="fa-solid fa-power-off" style="color: #00ff00;"></i> Power On</a></li>
                <li><a class="dropdown-item" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Power Off</a></li>
                <li><a class="dropdown-item" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Reset</a></li>
                <li><a class="dropdown-item" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Restart</a></li>
                <li><a class="dropdown-item" href="#"><i class="fa-solid fa-power-off" style="color: #f4f401;"></i> Shutdown</a></li>
            </ul>
        
    </div>
</template>

<script>
  export default {
    props: {
      equipment: {
        type: Object,
        required: true,
      },
    },
    data() {
      return {
        isOpen: false,
      };
    },
    mounted() {
      document.addEventListener("click", this.handleDocumentClick);
    },
    beforeDestroy() {
      document.removeEventListener("click", this.handleDocumentClick);
    },
    methods: {
      toggleDropdown(event) {
        event.stopPropagation();
        this.isOpen = !this.isOpen;
        console.log("toggleDropdown()" + this.isOpen);
      },
      handleDocumentClick() {
        if (this.isOpen) {
          this.isOpen = false;
        }
      },
      powerStatusColor(status) {
        switch (status) {
          case "off":
            return "#f40122";
          case "on":
            return "#00ff00";
          case "unknown":
          default:
            return "#f4f401";
        }
      },
    },
  };
</script>


