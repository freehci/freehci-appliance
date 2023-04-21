<template>
    <div class="tab-pane" id="log" role="tabpanel" :class="{ active: selectedTab === 'log' }">
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