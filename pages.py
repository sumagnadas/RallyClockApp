from kivy.base import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from re import sub

from datetime import datetime

Builder.load_file("pages.kv")

class NumericInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline=False
        self.input_type='number'
    def insert_text(self, substring: str, from_undo=False):
        s = sub('[^0-9]','',substring)
        return super(NumericInput, self).insert_text(s,from_undo=from_undo)
class RallyRow(RecycleDataViewBehavior, BoxLayout):
    car = ObjectProperty(None)
    time = StringProperty("00:00:00")
    carno = ObjectProperty(None)
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index# As an alternate method of assignment
        return super(RallyRow, self).refresh_view_attrs(
            rv, index, data)
    def on_enter(self):
        rv = App.get_running_app().rv
        rv.data[self.index]['carno'] = self.carno



class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = list()
class TimeLabel(Label):
    time = StringProperty()
    update = BooleanProperty(True)
    def __init__(self, **kwargs):
        self.update = self.update if not 'update' in kwargs.keys() else kwargs['update']
        self.event = Clock.schedule_interval(self.update_clock, 1/60)
        super().__init__(**kwargs)
    def on_update(self, instance, value):
        if self.update:
            Clock.schedule_interval(self.update_clock, 1/60)
        else:
            self.event.cancel()
            self.time = '00:00:00'

    def update_clock(self, dt):
      self.text = str(datetime.now().time())
      self.time = self.text

    def on_time(self, instance, value):
        self.text = self.time
class RoundedButton(Button):
    pass
class SetPage(SettingsWithNoMenu):
    pass

class Page3(Screen):
    rv = ObjectProperty(None)
    def on_capture(self, time):
        self.rv.data.append({'time': str(time),'carno': 0})