<template>
    <!-- This design is based on design by 
        Bootdey Admin Template
        https://www.bootdey.com/license
    -->
    <div class="container">
        <!-- Tabs -->
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
            <li class="nav-item" @click="selectTab('applications')">
                <a class="nav-link" data-toggle="tab" href="#applications" role="tab" :class="{ active: selectedTab === 'applications' }"><i class="fa-solid fa-box-open"></i> Applications</a>
            </li>
            <li class="nav-item" @click="selectTab('log')">
                <a class="nav-link" data-toggle="tab" href="#log" role="tab" :class="{ active: selectedTab === 'log' }"><i class="fa-solid fa-clock-rotate-left"></i> Log</a>
            </li>
            <li class="nav-item" @click="selectTab('company')">
                <a class="nav-link" data-toggle="tab" href="#company" role="tab" :class="{ active: selectedTab === 'company' }"><i class="fa-regular fa-building"></i> Company</a>
            </li>            
        </ul>
        
        <!-- Tab panes -->
        <div class="tab-content">
            <UserTab :selected-tab="selectedTab" />
            <MFATab :selected-tab="selectedTab" />
            <GroupsTab :selected-tab="selectedTab" />
            <PermissionsTab :selected-tab="selectedTab" />
            <RolesTab :selected-tab="selectedTab" />
            <LogTab :selected-tab="selectedTab" />
            <ApplicationsTab :selected-tab="selectedTab" />
        </div>
    </div>
</template>

<script>
    import UserTab from './userTabUser.vue';
    import MFATab from './userTabMFA.vue';
    import GroupsTab from './userTabGroups.vue';
    import PermissionsTab from './userTabPermissions.vue';
    import RolesTab from './userTabRoles.vue';
    import LogTab from './userTabLog.vue';
    import ApplicationsTab from './userTabApplications.vue';
    // import CompanyTab from './userTabCompany.vue';

    export default {
        components: {
            UserTab,
            MFATab,
            GroupsTab,
            PermissionsTab,
            RolesTab,
            LogTab,
            ApplicationsTab,
            //CompanyTab
        },
        data() {
            return {
                selectedTab: 'user'
            };
        },
        methods: {
            selectTab(tabName) {
                this.selectedTab = tabName;
            }
        }
    };
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
        background-color: #1A233A;
        
        color: #bcd0f7;
    }

    .form-control:focus {
        background-color: #1A233A;
        color: #bcd0f7;
    }

    select option {
        background: #1A233A;
        background-color: #1A233A;
        color: #bcd0f7;
        padding: #1A233A;
    }


    div select {
        background: #1A233A;
        background-color: #1A233A;
        color: #bcd0f7;
    }

    /* Prevent odd behavior on auto-filled forms */
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus,
    textarea:-webkit-autofill,
    textarea:-webkit-autofill:hover,
    textarea:-webkit-autofill:focus {
        background-color: #1A233A !important;
        -webkit-box-shadow: 0 0 0 30px #1A233A inset !important;
        -webkit-text-fill-color: #bcd0f7 !important;
        box-shadow: 0 0 0 30px #1A233A inset !important;
        font-size: .825rem !important;
        color: #bcd0f7 !important;
    }

    /* For Chrome, Edge, and Safari */
    
    .custom-listbox::-webkit-scrollbar {
        width: 12px; /* Bredden på rullefeltet */
        height: 12px; /* Høyden på rullefeltet */
    }

    .custom-listbox::-webkit-scrollbar-thumb {
        background-color: #47526e; /* Fargen på rullefeltets "tommel" */
        /* border-radius: 6px; /* Avrundede hjørner på "tommelen" */
    }

    .custom-listbox::-webkit-scrollbar-track {
        background-color: #bcd0f7; /* Fargen på rullefeltets bakgrunn */
        /* border-radius: 6px; /* Avrundede hjørner på rullefeltets bakgrunn */
    }

    /* For Firefox */
    .custom-listbox {
        scrollbar-width: thin; /* Bredden på rullefeltet */
        scrollbar-color: #1A233A #bcd0f7; /* Fargene på "tommelen" og bakgrunnen */
    }


    /* add some space between the tabs and the content */
    .tab-content {
        margin-top: 20px;
    }

</style>
