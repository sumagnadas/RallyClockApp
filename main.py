'''
This script is the main script which is run when the app is opened
It starts the main thread as well as setup the app for running

'''

from kivy.app import App
from pages import Home, Page3, StageSel, ViewLog
from kivy.uix.screenmanager import ScreenManager,NoTransition

class MainApp(App):
    _color=dict()
    _rect = dict()
    sm = ScreenManager(transition=NoTransition())
    use_kivy_settings = False

    def build(self):
        home = Home(name="Home")
        self.loc_but = home.loc_but
        self.sm.add_widget(home)
        self.sm.add_widget(Page3(name="Page3"))
        self.sm.add_widget(StageSel(name="StageSel"))
        self.sm.add_widget(ViewLog(name="Log"))
        self.rv = self.sm.get_screen('Page3').rv
        return self.sm

    def on_release(self, obj, i):
        obj.canvas.remove(self._color[i])
        obj.canvas.remove(self._rect[i])


if __name__=="__main__":
    MainApp().run()