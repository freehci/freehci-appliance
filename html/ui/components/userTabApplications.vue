<template>
    <div class="tab-pane" id="applications" role="tabpanel" :class="{ active: selectedTab === 'applications' }">
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
                    <div class="icon-container">
                    <!-- Icon elements will be added here -->
                        
                            <div class="icon-item">
                                <div class="icon-item-content">
                                    <i class="fa-brands fa-windows" style="color: #007bff;"></i>
                                    <p>Windows Server 2022</p>
                                </div>
                            </div>

                            <div class="icon-item">
                                <div class="icon-item-content">
                                    <i class="fa-brands fa-ubuntu" style="color: #007bff;"></i>
                                    <p>Ubuntu</p>
                                </div>
                            </div>

                            <div class="icon-item">
                                <div class="icon-item-content">
                                    <i class="fa-brands fa-redhat" style="color: red;"></i>
                                    <p>Red Hat Enterprise Server</p>
                                </div>
                            </div>

                            <div class="icon-item">
                                <div class="icon-item-content">
                                    <i class="fa-brands fa-centos" style="color: #007bff;"></i>
                                    <p>CentOS</p>
                                </div>
                            </div>

                            <div class="icon-item">
                                <div class="icon-item-content">
                                    <i class="fa-brands fa-suse" style="color: #269c28;"></i>
                                    <p>Suse 1</p>
                                </div>
                            </div>

                            <div class="icon-item">
                                <div class="icon-item-content">
                                    <i class="fa-brands fa-suse" style="color: #269c28;"></i>
                                    <p>Suse 2</p>
                                </div>
                            </div>

                            <div class="icon-item">
                                <div class="icon-item-content">
                                    <i class="fa-brands fa-suse" style="color: #269c28;"></i>
                                    <p>Suse 3</p>
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
        }
    };
</script>

<style scoped>
    

</style>