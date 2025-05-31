"""
This script contains the widgets which are used by
one or more of the screens shown in the app
"""

from datetime import time

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.textinput import TextInput

import globals
from models import EventLog


class UploadPopup(Popup):
    name = ObjectProperty

    def __init__(self, func, **kwargs):
        self.up_func = func
        super().__init__(**kwargs)
        if "up_name" in globals.settings.options("SETTINGS"):
            self.name.text = globals.settings["SETTINGS"]["up_name"]

    def verify_and_up(self):
        name = self.name.text
        if not name.strip():
            Dialog(self.parent, "Enter Uploader Name").show()
            return 1
        self.up_func(name)
        self.dismiss()
        return 0


class RTimePopup(Popup):
    """Class for the popup which shows up when a restart time is to be added"""

    hour = ObjectProperty(None)
    minute = ObjectProperty(None)
    sec = ObjectProperty(None)
    prev_offset = 0

    def __init__(self, row, **kwargs):
        self.row = row
        self.tm = self.row.tm
        super().__init__(**kwargs)

    def on_rtm(self):
        new_tm = time(int(self.hour.text), int(self.minute.text), int(self.sec.text))

        # if the new time is before old time, then don't take the time
        if self.row.tm > new_tm:
            Dialog(self.parent, text="Invalid RTime").open()
        else:
            self.row.is_rtm = True
            self.row.rtm = time(
                int(self.hour.text), int(self.minute.text), int(self.sec.text)
            )

            # Since there has been a change in data, the upload button is changed
            # as the uploaded data is not same as the local data
            globals.settings["SETTINGS"]["up_count"] = str(0)
            globals.settings.write()

            self.dismiss()

    def on_auto(self, time):
        """Adds the new row to the RecycleView(at the top) and to the logfile database(at the end)"""

        # Show it in the edit section if it wants to be further edited
        tm = globals.synced_time
        self.hour.text = f"{tm.hour:02}"
        self.minute.text = f"{tm.minute:02}"
        self.sec.text = f"{tm.second:02}"


class LLPopup(Popup):
    """Class for the popup which shows up when a Lifeline is to be given"""

    def __init__(self, row, **kwargs):
        self.row = row
        super().__init__(**kwargs)

    def on_ll(self):
        self.row.LL = True
        self.dismiss()

        # Since there has been a change in data, the upload button is changed
        # as the uploaded data is not same as the local data
        globals.settings["SETTINGS"]["up_count"] = str(0)
        globals.settings.write()


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


class LogRow(RecycleDataViewBehavior, BoxLayout):
    """Class which is used as the row for displaying the events in the logfile"""

    carno = ObjectProperty(None)
    tm = ObjectProperty(time(0, 0, 0))  # captured time of car
    # Restart time of the car
    rtime = ObjectProperty(time(0, 0, 0), allownone=True)
    # if there is Restart time given to the car
    is_rtm = BooleanProperty(False)
    LL = BooleanProperty(False)  # if Lifeline is given to the car
    use_ll = BooleanProperty(
        globals.settings.getboolean("SETTINGS", "use_ll")
    )  # Whether to use Lifeline
    use_rt = BooleanProperty(
        globals.settings.getboolean("SETTINGS", "use_rt")
    )  # Whether to use restart time
    ll_row = ObjectProperty(None)  # LL label for the row
    rt_row = ObjectProperty(None)  # restart time label for the row

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload_ll("SETTINGS", "use_ll", None)
        self.reload_rt("SETTINGS", "use_rt", None)
        globals.settings.add_callback(self.reload_ll, "SETTINGS", "use_ll")
        globals.settings.add_callback(self.reload_rt, "SETTINGS", "use_rt")

    def reload_ll(self, section, key, value):
        """Hide the label if it is present when LL is not to be used and vice versa"""

        self.use_ll = globals.settings.getboolean(section, key)
        if not self.use_ll and self.ll_row in self.children:
            self.remove_widget(self.ll_row)
        elif self.use_ll and self.ll_row not in self.children:
            self.add_widget(self.ll_row)

    def reload_rt(self, section, key, value):
        """Hide the label if it is present when LL is not to be used and vice versa"""

        self.use_rt = globals.settings.getboolean(section, key)
        no = len(self.children) - 2
        if not self.use_rt and self.rt_row in self.children:
            self.remove_widget(self.rt_row)
        elif self.use_rt and self.rt_row not in self.children:
            self.add_widget(self.rt_row, index=no)


class NumericInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False  # set mode of input to single line
        # (For android) Show the numeric keyboard for input
        self.input_type = "number"
        self.input_filter = "int"


class RTimeInput(NumericInput):
    """Input for time in the Restart time popup"""

    tm = ObjectProperty(None)  # Original captured time
    pop = ObjectProperty(None)  # Restart time popup

    def insert_text(self, substring: str, from_undo=False):
        text = self.text + substring
        if len(text) > 2:
            substring = ""
        elif self.tm and self.pop and substring.isnumeric():
            if self == self.pop.hour:
                if int(text) >= 24:
                    substring = ""
            elif self == self.pop.minute:
                if int(text) >= 60:
                    substring = ""
            elif self == self.pop.sec:
                if int(text) >= 60:
                    substring = ""
        return super().insert_text(substring, from_undo)

    pass


class RallyRow(RecycleDataViewBehavior, BoxLayout):
    """Class which is used as the row for showing data in the Finish data capture list"""

    carno = StringProperty("")
    tm = ObjectProperty(time(0, 0, 0))  # captured time of car
    # Restart time of the car
    rtm = ObjectProperty(time(0, 0, 0), allownone=True)
    # if there is Restart time given to the car
    is_rtm = BooleanProperty(False)
    LL = BooleanProperty(False)  # if Lifeline is given to the car
    row_id = NumericProperty(0)  # Database row id corresponding to this data
    wrong_car = BooleanProperty(False)  # if the car no. entered is duplicate
    use_ll = BooleanProperty(
        globals.settings.getboolean("SETTINGS", "use_ll")
    )  # Whether to use Lifeline
    use_rt = BooleanProperty(
        globals.settings.getboolean("SETTINGS", "use_rt")
    )  # Whether to use restart time
    ll_but = ObjectProperty(None)  # LL button for the row
    rt_but = ObjectProperty(None)  # restart time button for the row
    rtm_label = ObjectProperty(None)  # restart time label for the row
    tm_box = ObjectProperty(None)  # Box containing restart time label and time

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reload_ll("SETTINGS", "use_ll", None)
        self.reload_rt("SETTINGS", "use_rt", None)
        globals.settings.add_callback(self.reload_rt, "SETTINGS", "use_rt")
        globals.settings.add_callback(self.reload_ll, "SETTINGS", "use_ll")

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""

        data_rv = rv.data

        # the index shound change every time a row is added as the new element is added to the top and index of the elements increases by one
        self.index = data_rv.index(data)

        # row_index is different because view adds to the top but database adds to the end (if the element is 2nd in view, it will be 2nd last in database)
        row_id = len(data_rv) - self.index

        if not self.row_id:
            # store the row for updating data without searching for the row in database every time
            row = EventLog.select().where(EventLog.id == row_id).get()

            # set the prev_carno for getting the NumericInput back if user entered duplicate entry and also for finding the index from the RecycleView
            self.prev_carno = str(row.carno)

        self.row_id = row_id
        return super(RallyRow, self).refresh_view_attrs(rv, index, data)

    def on_enter(self):
        """Process and save the new car no entered"""

        app = App.get_running_app()  # the app being run
        rv = app.rv  # the RecycleView of the Finish screen

        # Find the record with id (auto-incremented integer PK for this table) and corresponding event type and set the carno to new one
        row = EventLog.select().where(EventLog.id == self.row_id).get()

        # See if there are any duplicates in the database
        if not EventLog.select().where(EventLog.carno == self.carno).count():
            self.wrong_car = False
            # Save the new carno in the database and update the prev_carno to the current one
            self.prev_carno = self.carno
        else:
            self.wrong_car = True
            # If there is a duplicate, show a popup which confirms whether the user wants to keep it
            # If user confirms to keep it, then the carno will be set in the process in above if condition
            # If user declines, then the carno input will be returned to the previous carno and asked to enter another one
            self.carno = ""

            dia = Dialog(app.sm.get_screen("Page3"), "Duplicate")
            dia.pos_hint = {"center_x": 0.5, "center_y": 0.9}
            dia.show()
        row.carno = self.carno
        row.save()

        # Set the new carno in the view
        rv.data[self.index]["carno"] = self.carno

        # reset the upload count
        globals.settings["SETTINGS"]["up_count"] = str(0)
        globals.settings.write()

    def on_LL(self, instance, value):
        row = EventLog.select().where(EventLog.id == self.row_id).get()
        row.LL = self.LL
        row.save()

    def on_ll(self):
        LLPopup(row=self).open()

    def reload_ll(self, section, key, value):
        """Hide the label if it is present when LL is not to be used and vice versa"""

        self.use_ll = globals.settings.getboolean(section, key)
        if not self.use_ll and self.ll_but in self.children:
            self.remove_widget(self.ll_but)
        elif self.use_ll and self.ll_but not in self.children:
            self.add_widget(self.ll_but)

    def reload_rt(self, section, key, value):
        """Hide the label if it is present when Restart time is not to be used and vice versa"""

        self.use_rt = globals.settings.getboolean(section, key)
        no = len(self.children) - 2
        if not self.use_rt and self.rt_but in self.children:
            self.remove_widget(self.rt_but)
            self.tm_box.remove_widget(self.rtm_label)
        elif self.use_rt and self.rt_but not in self.children:
            self.add_widget(self.rt_but, index=no)
            self.tm_box.add_widget(self.rtm_label)

    def on_rt(self, but):
        RTimePopup(self).open()

    def on_rtm(self, instance, value):
        if self.is_rtm:
            app = App.get_running_app()  # the app being run
            rv = app.rv  # the RecycleView of the Finish screen
            rv.data[self.index]["rtm"] = self.rtm
            rv.data[self.index]["is_rtm"] = self.is_rtm

            row = EventLog.select().where(EventLog.id == self.row_id).get()
            row.is_rtm = self.is_rtm
            row.rtime = self.rtm
            row.save()


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


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = list()


class FlightPopup(Popup):
    """
    Class for the popup which shows up when asking whether
    the user wants to capture time without turning on airplane mode or not
    """

    def __init__(self, manager, **kwargs):
        self.manager = manager
        super().__init__(**kwargs)

    def on_confirm(self):
        """
        If the user wants to continue to capture, then let
        them capture and go to the capture screen
        """

        self.dismiss()
        self.manager.current = "Page3"


class Re_StartPopup(Popup):
    """
    Class for the popup which shows up when asking whether
    the user wants to capture time without turning on airplane mode or not
    """

    tm = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def change_time(self, value):
        globals.settings["SETTINGS"]["start_time"] = str(value)
        self.dismiss()
