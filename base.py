"""
This script contains the widgets which are used by
one or more of the screens shown in the app
"""

from datetime import time

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

import globals


class Dialog(ModalView):
    """Class for showing alerts to the user"""

    fsz = ObjectProperty(None)
    text = ObjectProperty(None)

    def __init__(self, parent, text, **kwargs):
        super().__init__(**kwargs)

        self.height = parent.height * 0.1
        self.width = parent.width * 0.4
        self.text.text = text

    def show(self, timeout=5):
        """Show the alert for a short time and then go away"""

        self.open()
        Clock.schedule_interval(lambda dt: self.dismiss(), timeout)


class NavigationBar(BoxLayout):
    """Class for the Navigation Bar in all the screens"""

    pass


class TimeLabel(Label):
    """Class for Labels showing only time"""

    tm = ObjectProperty(time(0, 0, 0))
    # Checks if the time in the Label is to be updated or not
    update = BooleanProperty(True)

    def __init__(self, **kwargs):
        globals.update_objs.append(self)

        # Updates the clock every 1/60 seconds (the event is cancelled i.e. the label text is not updated if the update property is False)
        self.update = self.update if not "update" in kwargs.keys() else kwargs["update"]

        super().__init__(**kwargs)

    def on_update(self, instance, value):
        """Schedule the update_clock event if its not already scheduled and self.update is changed from false to true"""
        if self.update:
            globals.update_objs.append(self)
        else:
            globals.update_objs.remove(self)
            self.tm = time(0, 0, 0)

    def on_tm(self, instance, value):
        self.text = self.tm.strftime("%H:%M:%S")


class RoundedButton(Button):
    """Class for Buttons with rounded corner (styling in kv file)"""

    def on_state(self, ins, value):
        """Changes the color of the RoundedButton when pressed(due to custom layout, there is no appearance change of button when it is pressed by the user)"""

        if value == "down":
            with self.canvas:
                self._color = Color(200 / 255, 228 / 255, 244 / 255, 0.5)
                self._rect = RoundedRectangle(pos=self.pos, size=self.size)
        if value == "normal":
            self.canvas.remove(self._color)
            self.canvas.remove(self._rect)

    pass
