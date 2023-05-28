<template>
    <div class="tab-pane" id="groups" role="tabpanel" :class="{ active: selectedTab === 'groups' }">
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
                        <div class="row">
                            <div class="col-xl-12 col-lg-12 col-md-12 col-sm-12 col-12">
                                <h6 class="mb-3 text-primary">Groups Details</h6>
                            </div>
                            <!-- Search box -->
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="searchGroup">Search Group</label>
                                    <input type="text" class="form-control" id="searchGroup" placeholder="Search for a group">
                                </div>
                            </div>
                        </div>

                        <div class="row">
                            <!-- List box 1 -->
                            <div class="col-md-5">
                                <label for="listBox1">Available Groups</label>
                                <select ref="listBox1" multiple class="form-control custom-listbox" id="listBox1" size="10">
                                    <!-- Add your available groups here -->
                                    <option v-for="group in groups" :key="group.id" :value="group.id">
                                        {{ group.name }} - {{ group.description }}
                                    </option>
                                </select>
                            </div>

                            <!-- Buttons -->
                            <div class="col-md-2 d-flex flex-column justify-content-center">
                                <button @click="addToSelected" type="button" ref="addButton" class="btn btn-custom mb-3">Add <i class="fa-solid fa-caret-right"></i></button>
                                <button @click="addToSelected" type="button" ref="addButton" class="btn btn-custom mb-3"><i class="fa-solid fa-calendar"> </i> Add <i class="fa-solid fa-caret-right"></i></button>
                                <button @click="removeFromSelected" type="button" ref="removeButton" class="btn btn-custom"><i class="fa-solid fa-caret-left"></i> Remove</button>
                            </div>

                            <!-- List box 2 -->
                            <div class="col-md-5">
                                <label for="listBox2">Selected Groups</label>
                                <select ref="listBox2" multiple class="form-control" id="listBox2" size="10">
                                    <!-- Add your selected groups here -->
                                    <option v-for="group in selectedGroups" :key="group.id" :value="group.id">
                                        {{ group.name }} - {{ group.description }}
                                    </option>
                                </select>
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
        },
        data() {
            return {
                groups: [
                    { id: 1, name: 'Domain Admins', description: 'Description 1' },
                    { id: 2, name: 'Domain Users', description: 'Description 2' },
                    { id: 3, name: 'FreeHCI Users', description: 'Description 3' },
                    { id: 4, name: 'FreeHCI Admins', description: 'Description 4' },
                    { id: 5, name: 'FreeHCI Developers', description: 'Description 5' },
                    { id: 6, name: 'FreeHCI Testers', description: 'Description 6' },
                    { id: 7, name: 'FreeHCI Beta Testers', description: 'Description 7' },
                    { id: 8, name: 'FreeHCI Alpha Testers', description: 'Description 8' },
                    { id: 9, name: 'FreeHCI Beta Testers', description: 'Description 9' },
                    { id: 10, name: 'FreeHCI Alpha Testers', description: 'Description 10' },
                    { id: 11, name: 'FreeHCI Beta Testers', description: 'Description 11' },
                    { id: 12, name: 'FreeHCI Alpha Testers', description: 'Description 12' },
                    { id: 13, name: 'FreeHCI Beta Testers', description: 'Description 13' },
                    { id: 14, name: 'FreeHCI Alpha Testers', description: 'Description 14' },
                    { id: 15, name: 'FreeHCI Beta Testers', description: 'Description 15' },
                    { id: 16, name: 'FreeHCI Alpha Testers', description: 'Description 16' },
                    { id: 17, name: 'FreeHCI Beta Testers', description: 'Description 17' },
                    { id: 18, name: 'FreeHCI Alpha Testers', description: 'Description 18' },
                    { id: 19, name: 'FreeHCI Beta Testers', description: 'Description 19' },
                    { id: 20, name: 'FreeHCI Alpha Testers', description: 'Description 20' },
                    { id: 21, name: 'FreeHCI Beta Testers', description: 'Description 21' },
                    { id: 22, name: 'FreeHCI Alpha Testers', description: 'Description 22' },
                    { id: 23, name: 'FreeHCI Beta Testers', description: 'Description 23' },
                    { id: 24, name: 'FreeHCI Alpha Testers', description: 'Description 24'}
                ],
                
                selectedGroups: [],
            // ...
            };
        },
        methods: {
            
            addToSelected() {
                const selectedOptions = Array.from(this.$refs.listBox1.selectedOptions);
                selectedOptions.forEach((option) => {
                const groupId = parseInt(option.value);
                const group = this.groups.find((g) => g.id === groupId);
                if (group) {
                    this.selectedGroups.push(group);
                    this.groups = this.groups.filter((g) => g.id !== groupId);
                }
                });
            },
            removeFromSelected() {
                const selectedOptions = Array.from(this.$refs.listBox2.selectedOptions);
                selectedOptions.forEach((option) => {
                const groupId = parseInt(option.value);
                const group = this.selectedGroups.find((g) => g.id === groupId);
                if (group) {
                    this.groups.push(group);
                    this.selectedGroups = this.selectedGroups.filter((g) => g.id !== groupId);
                }
                });
            },
            
        },
        mounted() {
            
        }
    };
</script>
  