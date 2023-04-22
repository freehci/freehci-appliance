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

<style>
    .full-width {
        width: 100%;
    }

    .icon-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        max-height: 500px; /* Set the maximum height for the card */
        overflow-y: auto; /* Add a scrollbar when the content exceeds the maximum height */
        padding: 1rem;
    }

    .icon-item :hover {
        background-color: #596280;
        border-radius: 10px;
        cursor: pointer;
    }

    .icon-item {
        flex-basis: calc(16.666% - 10px); /* 6 items per row with some space for margins */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 5px;
        background-color: #1A233A;
        border: solid 1px #bcd0f7;
        border-radius: 10px;
        padding: 10px;
        box-sizing: border-box;
        text-align: center;
        font-size: 14px;
        position: relative;
    }

    .icon-item::before {
        content: "";
        display: block;
        padding-top: 100%; /* 1:1 aspect ratio */
    }

    .icon-item-content {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
    }

    .icon-item i {
        font-size: 30px;
        margin-bottom: 5px;
        margin-top: 20px;
    }

    .icon-item p {
        margin-top: 10px;
    }


</style>