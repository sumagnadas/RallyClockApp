from kivy.base import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu
from kivy.properties import StringProperty
from kivy.clock import Clock

from datetime import datetime

Builder.load_file("pages.kv")

class TimeLabel(Label):
    time = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_clock, 1/60)
    def update_clock(self, dt):
      self.text = str(datetime.now().time())
    def on_time(self, instance, value):
        self.text = self.time
        print(self.time)
class RoundedButton(Button):
    pass
class SetPage(SettingsWithNoMenu):
    pass

class Page3(Screen):
    pass