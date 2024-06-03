from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime

class Home(Widget):
    _color=dict()
    _rect = dict()
    time = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_clock, 1/60)
    def _btnchg(self, obj,i):
        with obj.canvas:
            self._color[i] = Color(200/255, 200/255, 200/255,0.9)
            self._rect[i] = RoundedRectangle(pos=obj.pos, size=obj.size)

    def on_release(self, obj, i):
        obj.canvas.remove(self._color[i])
        obj.canvas.remove(self._rect[i])

    def on_b1(self, obj):
        print("button1")
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
    def update_clock(self, dt):
      self.time.text = str(datetime.now().time())

class MainApp(App):
    def build(self):
        return Home()

if __name__=="__main__":
    MainApp().run()