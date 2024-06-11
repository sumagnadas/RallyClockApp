from kivy.app import App
from pages import Home, Page3, StageSel
from kivy.uix.screenmanager import ScreenManager,NoTransition

class MainApp(App):
    _color=dict()
    _rect = dict()
    sm = ScreenManager(transition=NoTransition())

    def build(self):
        #self.settings_cls = SetingsWI
        self.sm.add_widget(Home(name="Home"))
        self.sm.add_widget(Page3(name="Page3"))
        self.sm.add_widget(StageSel(name="StageSel"))
        self.rv = self.sm.get_screen('Page3').rv
        return self.sm
    def on_release(self, obj, i):
        obj.canvas.remove(self._color[i])
        obj.canvas.remove(self._rect[i])


if __name__=="__main__":
    MainApp().run()