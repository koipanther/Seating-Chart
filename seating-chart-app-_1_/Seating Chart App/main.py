from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, DictProperty
import random
import json
import os

Builder.load_file("seating.kv")


class MainMenu(Screen):
    seating_chart = ListProperty([])

    def randomize_seating(self):
        from kivy.app import App
        # List of students
        students = [
            "Batman", "Captain America", "Danny Devito", "Elon Musk", "Homelander",
            "John Cena", "Jack Harlow", "Logan Paul", "Mickey Mouse", "MJ",
            "Spiderman", "Mother Teresa", "Mbappe", "Roddy Ricch", "KSI",
            "Superman", "The Joker", "The Winter Soldier", "Toussaint Louverture", "Mr. Beast"
        ]
        random.shuffle(students)
        self.seating_chart = students[:20]  # Limit to 20 students for seating

        # Save the randomized student data to the app instance
        app = App.get_running_app()
        app.randomized_students = {name: {"preferences": {}} for name in self.seating_chart}
        print(f"Randomized students: {app.randomized_students}")


class NamePreferencesScreen(Screen):
    student_data = {}

    def on_enter(self):
        # Load students when entering the screen
        self.load_students()
        self.populate_name_list()

    def load_students(self):
        try:
            # Check if the file exists and is not empty
            if os.path.exists("students.json") and os.path.getsize("students.json") > 0:
                with open("students.json", "r") as f:
                    self.student_data = json.load(f)
            else:
                # Initialize with an empty dictionary if the file doesn't exist or is empty
                self.student_data = {}
                with open("students.json", "w") as f:
                    json.dump(self.student_data, f)
        except json.JSONDecodeError:
            # Handle invalid JSON
            self.student_data = {}
            with open("students.json", "w") as f:
                json.dump(self.student_data, f)

    def populate_name_list(self):
        """Populate the name list dynamically in the UI."""
        self.ids.name_list_box.clear_widgets()  # Clear existing widgets
        for name in self.student_data.keys():
            # Create a horizontal layout for each name
            name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)

            # Add a Label for the student name
            name_label = Label(
                text=name,
                color=(0, 0, 0, 1),  # Black text color
                size_hint_x=0.8
            )
            name_layout.add_widget(name_label)

            # Add a delete button next to each name
            delete_button = Button(
                text="Delete",
                size_hint_x=0.2,
                background_color=(1, 0, 0, 1)  # Red background
            )
            delete_button.bind(on_release=lambda btn, n=name: self.delete_student(n))
            name_layout.add_widget(delete_button)

            self.ids.name_list_box.add_widget(name_layout)

    def add_student(self, name):
        """Add a new student to the list."""
        if name and name not in self.student_data:
            self.student_data[name] = {"preferences": {}}
            self.save_students()
            self.populate_name_list()  # Update the UI

    def delete_student(self, name):
        """Delete a student from the list."""
        if name in self.student_data:
            del self.student_data[name]
            self.save_students()
            self.populate_name_list()  # Update the UI

    def save_students(self):
        """Save the current student data to the JSON file."""
        with open("students.json", "w") as f:
            json.dump(self.student_data, f)

    def save_and_return(self):
        """Save changes and navigate back to the main menu."""
        self.save_students()
        print("Saving preferences and returning...")
        self.manager.current = "main_menu"

    def open_customize_preferences(self):
        """Navigate to the Customize Preferences screen."""
        self.manager.current = "customize_preferences"


class RoomConfigScreen(Screen):
    room_objects = []  # Store all objects (desks, teacher desks, etc.)
    selected_object = None  # Track the currently selected object

    def on_enter(self):
        self.refresh_room_layout()

    def refresh_room_layout(self):
        """Refresh the layout to display all objects in the room."""
        self.ids.room_layout.clear_widgets()
        for scatter in self.room_objects:
            self.ids.room_layout.add_widget(scatter)

    def add_student_desk(self):
        """Add a new student desk to the center of the room."""
        desk = Button(
            text="Seats: 4",
            size_hint=(None, None),
            size=(100, 50),
            background_color=(0.8, 0.9, 0.9, 1),  # Light cyan
        )
        scatter = Scatter(
            size=(120, 70),
            size_hint=(None, None),
            do_rotation=False,  # Disable rotation
            do_scale=True,  # Allow resizing
            do_translation=True,  # Allow moving
            pos=self.center_of_room(),  # Position in the center
        )
        scatter.add_widget(desk)
        self.room_objects.append(scatter)
        self.refresh_room_layout()

    def add_teacher_desk(self):
        """Add a new teacher desk to the center of the room."""
        desk = Button(
            text="Teacher Desk",
            size_hint=(None, None),
            size=(120, 60),
            background_color=(0.7, 0.7, 0.7, 1),  # Grey
        )
        scatter = Scatter(
            size=(140, 80),
            size_hint=(None, None),
            do_rotation=False,  # Disable rotation
            do_scale=True,  # Allow resizing
            do_translation=True,  # Allow moving
            pos=self.center_of_room(),  # Position in the center
        )
        scatter.add_widget(desk)
        self.room_objects.append(scatter)
        self.refresh_room_layout()

    def center_of_room(self):
        """Calculate the center position of the room layout."""
        room_layout = self.ids.room_layout
        return (room_layout.width / 2 - 50, room_layout.height / 2 - 25)

    def configure_desk(self):
        """Configure the selected desk (change seats or label)."""
        if self.selected_object:
            button = self.selected_object.children[0]  # Get the Button inside the Scatter
            button.text = "Seats: 6"  # Example configuration
            self.refresh_room_layout()

    def select_object(self, scatter):
        """Select a desk object."""
        self.selected_object = scatter
        print(f"Selected object: {self.selected_object}")

    def delete_object(self):
        """Delete the currently selected object."""
        if self.selected_object in self.room_objects:
            self.room_objects.remove(self.selected_object)
            self.selected_object = None
            self.refresh_room_layout()

    def save_configuration(self):
        """Save the current room configuration."""
        print("Configuration saved!")
        self.manager.current = "main_menu"

    def cancel_configuration(self):
        """Cancel and return to the main menu."""
        print("Configuration canceled.")
        self.manager.current = "main_menu"

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
import json
import os

class CustomizePreferencesScreen(Screen):
    selected_student = StringProperty("")
    student_data = {}
    seat_preferences = []  # To store selected seat preferences
    sit_with_preference = None  # To store "sit with"/"not sit with" preference

    def on_enter(self):
        app = App.get_running_app()  # Get the app instance
        if hasattr(app, 'randomized_students'):
            self.student_data = app.randomized_students
        else:
            self.student_data = {}
        self.populate_spinner()

    def populate_spinner(self):
        spinner = self.ids.student_spinner
        spinner.values = list(self.student_data.keys())

        preference_spinner = self.ids.preference_spinner
        preference_spinner.values = list(self.student_data.keys())

    def set_selected_student(self, student_name):
        self.selected_student = student_name
        print(f"Selected student: {self.selected_student}")

    def add_seat_preference(self, seat_id):
        if seat_id not in self.seat_preferences:
            self.seat_preferences.append(seat_id)
            print(f"Added seat preference: {seat_id}")
        else:
            self.seat_preferences.remove(seat_id)
            print(f"Removed seat preference: {seat_id}")

    def set_sit_with_preference(self, preference):
        self.sit_with_preference = preference
        print(f"Set sit-with preference: {self.sit_with_preference}")

    def save_preferences(self):
        if self.selected_student and self.selected_student in self.student_data:
            self.student_data[self.selected_student]["preferences"] = {
                "seats": self.seat_preferences,
                "sit_with": self.sit_with_preference
            }
            with open("students.json", "w") as f:
                json.dump(self.student_data, f)
            print(f"Saved preferences for {self.selected_student}: {self.student_data[self.selected_student]['preferences']}")

    def save_and_return(self):
        self.save_preferences()
        self.manager.current = "main_menu"

    def cancel(self):
        self.manager.current = "main_menu"




class SeatingApp(App):
    randomized_students = DictProperty({})  # Shared data structure for randomized students

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(NamePreferencesScreen(name='name_preferences'))
        sm.add_widget(RoomConfigScreen(name='room_config'))
        sm.add_widget(CustomizePreferencesScreen(name='customize_preferences'))
        return sm


if __name__ == '__main__':
    SeatingApp().run()
