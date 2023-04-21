<template>
  <div class="tab-pane" id="user" role="tabpanel" :class="{ active: selectedTab === 'user' }">
      <!-- User Card -->
      <div class="row gutters">
        <div class="col-xl-3 col-lg-3 col-md-12 col-sm-12 col-12">
            <div class="card h-100">
                <div class="card-body">
                    <div class="account-settings">
                        <div class="user-profile">
                            <div class="user-avatar">
                                <img src="static/images/Sofagris avatar.png" alt="Sofagris">
                            </div>
                            <h5 class="user-name">Roy Michelsen</h5>
                            <h6 class="user-email">roy.michelsen@freehci.com</h6>
                            <p class="user-website">https://www.freehci.com</p>
                            <p class="user-handle">@Sofagris</p>
                        </div>
                        <div class="about">
                            <h5 class="mb-2 text-primary">About</h5>
                            <p>I'm the lead developer for FreeHCI. Live in Norway, and work IRL with HCI solutions like VxRail and other technologies</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- Properties Card -->
        <div class="col-xl-9 col-lg-9 col-md-12 col-sm-12 col-12">
            <div class="card h-100">
                <div class="card-body">
                  
                    <div class="row gutters">
                        <div class="col-xl-12 col-lg-12 col-md-12 col-sm-12 col-12">
                            <h6 class="mb-3 text-primary">Personal Details</h6>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="fullName">Full Name</label>
                                <input type="text" class="form-control" id="fullName" placeholder="Enter full name">
                            </div>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="eMail">Email</label>
                                <input type="email" class="form-control" id="eMail" placeholder="Enter email ID">
                            </div>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="phone">Phone</label>
                                <input type="text" class="form-control" id="phone" placeholder="Enter phone number">
                            </div>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="website">Website URL</label>
                                <input type="url" class="form-control" id="website" placeholder="Website url">
                            </div>
                        </div>
                    </div>
                    <div class="row gutters">
                        <div class="col-xl-12 col-lg-12 col-md-12 col-sm-12 col-12">
                            <h6 class="mb-3 text-primary">Address</h6>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="Street">Street</label>
                                <input type="name" class="form-control" id="Street" placeholder="Enter Street">
                            </div>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="ciTy">City</label>
                                <input type="name" class="form-control" id="ciTy" placeholder="Enter City">
                            </div>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="sTate">State</label>
                                <input type="text" class="form-control" id="sTate" placeholder="Enter State">
                            </div>
                        </div>
                        <div class="col-xl-6 col-lg-6 col-md-6 col-sm-6 col-12">
                            <div class="form-group">
                                <label for="zIp">Zip Code</label>
                                <input type="text" class="form-control" id="zIp" placeholder="Zip Code">
                            </div>
                        </div>
                    </div>
                    <div class="row gutters">
                        <div class="col-xl-12 col-lg-12 col-md-12 col-sm-12 col-12">
                            <div class="text-right">
                                <button type="button" id="submit" name="submit" class="btn btn-custom">Cancel</button>
                                <button type="button" id="submit" name="submit" class="btn btn-custom">Update</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>  
  </div>
</template>
  
<script>  
  export default {
    props: {
        selectedTab: String
    },
    data() {
      return {
        items: [],
      };
    },
    methods: {
      // Fetch items
      fetchItems() {
        axios
          .get(window.apiBaseUrl + "appliance/metrics")
          .then((response) => {
            this.items = response.data;
          })
          .catch((error) => {
            console.error("Error fetching items:", error);
          });
      },
  
      // Create a new item
      createItem(item) {
        axios
          .post(window.apiBaseUrl + "appliance/metrics", item)
          .then((response) => {
            this.items.push(response.data);
          })
          .catch((error) => {
            console.error("Error creating item:", error);
          });
      },
  
      // Update an existing item
      updateItem(item) {
        axios
          .put(window.apiBaseUrl + `appliance/metrics/${item.id}`, item)
          .then((response) => {
            const index = this.items.findIndex((i) => i.id === item.id);
            this.items.splice(index, 1, response.data);
          })
          .catch((error) => {
            console.error("Error updating item:", error);
          });
      },
  
      // Delete an item
      deleteItem(item) {
        axios
          .delete(window.apiBaseUrl + `appliance/metrics/${item.id}`)
          .then(() => {
            const index = this.items.findIndex((i) => i.id === item.id);
            this.items.splice(index, 1);
          })
          .catch((error) => {
            console.error("Error deleting item:", error);
          });
      },
    },
    mounted() {
        // Fetch items on mount
        this.fetchItems();
        setInterval(this.fetchItems, 5000); // Update every 5 seconds
    },
  };
</script>
  
<style>
  /* Your component styles go here */

</style>
  