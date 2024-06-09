from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from pages import Page3
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

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
class MainApp(App):
    _color=dict()
    _rect = dict()
    sm = ScreenManager(transition=NoTransition())

    def build(self):
        #self.settings_cls = SetingsWI
        self.sm.add_widget(Home(name="Home"))
        self.sm.add_widget(Page3(name="Page3"))
        self.rv = self.sm.get_screen('Page3').rv
        return self.sm
    def on_release(self, obj, i):
        obj.canvas.remove(self._color[i])
        obj.canvas.remove(self._rect[i])


if __name__=="__main__":
    MainApp().run()