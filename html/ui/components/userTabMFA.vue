<template>
    <div class="tab-pane" id="mfa" role="tabpanel" :class="{ active: selectedTab === 'mfa' }">
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
                    <div class="card-body" >
                        <div class="row" >
                            <div class="col-xl-12 col-lg-12 col-md-12 col-sm-12 col-12" >
                                <h6 class="mb-3 text-primary" >Multi-Factor Authentication</h6>
                            </div>
                        </div>

                        <!-- Add MFA Button and Dropdown -->
                        <div class="row">
                            <div class="col-md-12">
                                <div class="dropdown">
                                    <button class="btn btn-custom dropdown-toggle" type="button" id="addMfaDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                        Add MFA
                                    </button>
                                    <ul class="dropdown-menu" aria-labelledby="addMfaDropdown">
                                        <li><a class="dropdown-item" href="#">Enable SMS</a></li>
                                        <li><a class="dropdown-item" href="#">Enable OTP</a></li>
                                        <li><a class="dropdown-item" href="#">Enable Email</a></li>
                                        <li><a class="dropdown-item" href="#">Enable Google Authenticator</a></li>
                                        <li><a class="dropdown-item" href="#">Enable Mobile Push</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <!-- MFA Container -->
                        <div class="mfa-container">
                            <!-- Active MFA Methods List -->
                            <div class="row mt-3 mfa-row">
                                <div class="col-md-6">
                                    <div class="list-group">
                                    <a href="#" class="list-group-item list-group-item-action">
                                        SMS
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action">
                                        OTP
                                    </a>
                                    <!-- Add more active MFA methods here -->
                                    </div>
                                </div>
                            

                                <!-- MFA Method Content (Half width) -->
                                <div class="col-md-6">
                                    <div class="mfa-content">
                                    <!-- Display content related to the selected MFA method here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- Buttons -->
                        <div class="row gutters mt-3">
                            <div class="col-xl-12 col-lg-12 col-md-12 col-sm-12 col-12">
                                <div class="text-right">
                                    <button type="button" id="submit" name="submit" class="btn btn-custom">Cancel</button>
                                    <button type="button" id="submit" name="submit" class="btn btn-custom">Update</button>
                                </div>
                            </div>
                        </div>
                        <!-- End Buttons -->
                        
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
    .mfa-container {
        
        display: flex;
        flex-direction: row;
        align-items: stretch;
        height: calc(100% - 120px); /* Adjust this value based on the height of the "Add MFA" button and title */
    }

    .mfa-row {
        width: 100%;
    }

    .mfa-content {
        position: relative;
        /* top: -150; */
        border: 1px solid #596280;
        border-radius: 5px;
        /* padding: 10px; */
        height: 370px;
        /* width: 390px; */
    }


</style>