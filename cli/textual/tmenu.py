from textual.app import App
from textual import events
from textual.reactive import Reactive
from textual.widgets import Button, Checkbox, Placeholder, ListView
from textual.containers import VerticalScroll, Container
from textual.scroll_view import ScrollView




class MyApp(App):
    async def on_load(self, event: events.Load) -> None:
        self.bind("q", "quit")

    async def on_mount(self, event: events.Mount) -> None:
        appliance_button = Button("Appliance", name="appliance_button")
        users_button = Button("Users", name="users_button")
        groups_button = Button("Groups", name="groups_button")
        equipment_button = Button("Equipment", name="equipment_button")
        logs_button = Button("Logs", name="logs_button")
        quit_button = Button("Quit", name="quit_button")
        # Here we're adding services as checkboxes
        dhcp_service = Checkbox("DHCP", name="dhcp_service", value=True)
        # ... add more services here

        buttons = ScrollView()  # ScrollView can be used to hold buttons
        buttons._add_children(appliance_button, users_button, groups_button, equipment_button, logs_button, quit_button, dhcp_service)
        buttons.border_title = "Services"
        #buttons._add_child(appliance_button, users_button, groups_button, equipment_button, logs_button, quit_button, dhcp_service)
        #await self.view.dock(buttons)
        
        
    async def action_appliance_button(self, button: Button) -> None:
        # Here we would handle what happens when the Appliance button is pressed
        pass

    async def action_users_button(self, button: Button) -> None:
        # Here we would handle what happens when the Users button is pressed
        pass

    async def action_quit_button(self, button: Button) -> None:
        await self.quit()

# ... and so on for other buttons

#MyApp.run(title="FreeHCI!")


if __name__ == "__main__":
    app = MyApp()
    app.run()
