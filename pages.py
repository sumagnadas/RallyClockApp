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
from kivy.graphics import Color, RoundedRectangle
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
class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def _btnchg(self, obj,i):
        with obj.canvas:
            App.get_running_app()._color[i] = Color(200/255, 200/255, 200/255,0.9)
            App.get_running_app()._rect[i] = RoundedRectangle(pos=obj.pos, size=obj.size)
    def on_b1(self, obj):
        print("button1")
        self.manager.current = "Page3"
        self._btnchg(obj, 0)
        print(obj)
    def on_b2(self, obj):
        print("button2")
        self._btnchg(obj, 1)
        print(obj)
    def on_b3(self, obj):
        print("button3")
        self._btnchg(obj, 2)
        print(obj)
    def on_b4(self, obj):
        print("button4a")
        self._btnchg(obj, 3)
        print(obj)
    def on_b5(self, obj):
        print("button4b")
        self.manager.current = "StageSel"
        self._btnchg(obj, 4)
        print(obj)
    def on_b6(self, obj):
        print("button4c")
        self._btnchg(obj, 5)
        print(obj)
    def on_set(self, obj):
        print("settings")
        self._btnchg(obj, 6)
        print(obj)
class SetPage(SettingsWithNoMenu):
    pass
class StageSel(Screen):
    day = ObjectProperty([])
    day_no = ObjectProperty(None)
    stage = ObjectProperty(None)
    def on_day_no(self,instance,value):
        print(self.day)
        app = App.get_running_app()
        if app.sm.current == 'StageSel':
            print(self.day.index(self.day_no))
class Page3(Screen):
    rv = ObjectProperty(None)
    def on_capture(self, time):
        print(time)
        self.rv.data.append({'time': str(time),'carno': 0})