<template>
    <!-- This design is based on design by 
        Bootdey Admin Template
        https://www.bootdey.com/license
    -->
    <div class="container">
        <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item" @click="selectTab('user')">
                <a class="nav-link" data-toggle="tab" href="#user" role="tab" :class="{ active: selectedTab === 'user' }"><i class="fas fa-user"></i> User</a>
            </li>
            <li class="nav-item" @click="selectTab('mfa')">
                <a class="nav-link" data-toggle="tab" href="#mfa" role="tab" :class="{ active: selectedTab === 'mfa' }"><i class="fas fa-calculator"></i> Login devices</a>
            </li>
            <li class="nav-item" @click="selectTab('groups')">
                <a class="nav-link" data-toggle="tab" href="#groups" role="tab" :class="{ active: selectedTab === 'groups' }"><i class="fas fa-user-group"></i> Groups</a>
            </li>
            <li class="nav-item" @click="selectTab('permissions')">
                <a class="nav-link" data-toggle="tab" href="#permissions" role="tab" :class="{ active: selectedTab === 'permissions' }"><i class="fa-solid fa-user-lock"></i> Permissions</a>
            </li>
            <li class="nav-item" @click="selectTab('roles')">
                <a class="nav-link" data-toggle="tab" href="#roles" role="tab" :class="{ active: selectedTab === 'roles' }"><i class="fa-solid fa-user-tag"></i> Roles</a>
            </li>
        </ul>
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
                                <p>@Sofagris</p>
                            </div>
                            <div class="about">
                                <h5 class="mb-2 text-primary">About</h5>
                                <p>I'm the lead developer for FreeHCI. Live in Norway, and work IRL with HCI solutions like VxRail and other technologies</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
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

</script>

<style>

    .account-settings .user-profile {
        margin: 0 0 1rem 0;
        padding-bottom: 1rem;
        text-align: center;
    }
    .account-settings .user-profile .user-avatar {
        margin: 0 0 1rem 0;
    }
    .account-settings .user-profile .user-avatar img {
        width: 90px;
        height: 90px;
        -webkit-border-radius: 100px;
        -moz-border-radius: 100px;
        border-radius: 100px;
    }
    .account-settings .user-profile h5.user-name {
        margin: 0 0 0.5rem 0;
    }
    .account-settings .user-profile h6.user-email .user-website{
        margin: 0;
        font-size: 0.8rem;
        font-weight: 400;
    }
    .account-settings .about {
        margin: 1rem 0 0 0;
        font-size: 0.8rem;
        text-align: center;
    }
    .card {
        background: #272E48;
        -webkit-border-radius: 5px;
        -moz-border-radius: 5px;
        border-radius: 5px;
        border: 0;
        margin-bottom: 1rem;
    }
    .form-control {
        border: 1px solid #596280;
        -webkit-border-radius: 2px;
        -moz-border-radius: 2px;
        border-radius: 2px;
        font-size: .825rem;
        background: #1A233A;
        color: #bcd0f7;
    }

    

    



</style>
