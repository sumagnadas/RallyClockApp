'''
This script is the main script which is run when the app is opened
It starts the main thread as well as setup the app for running

'''

from kivy.app import App
from pages import Home, Page3, StageSel, ViewLog, SetPage
from kivy.uix.screenmanager import ScreenManager,NoTransition
from kivy.core.window import Window
from kivy.clock import Clock
from globals import update_clock

class MainApp(App):

    '''Class for the main app'''
    sm = ScreenManager(transition=NoTransition())
    use_kivy_settings = False

    def build(self):
        home = Home(name="Home")
        self.loc_but = home.loc_but
        self.sm.add_widget(home)
        self.sm.add_widget(Page3(name="Page3"))
        self.sm.add_widget(StageSel(name="StageSel"))
        self.sm.add_widget(ViewLog(name="Log"))
        self.sm.add_widget(SetPage(name='Settings'))
        self.rv = self.sm.get_screen('Page3').rv
        Clock.schedule_interval(update_clock, 0.1)

        win = Window
        win.bind(on_keyboard=self.my_key_handler)
        return self.sm

    def my_key_handler(self, window, keycode1, keycode2, text, modifiers):
        if keycode1 in [27, 1001]:
            if self.sm.current == 'Home':
                return False
            else:
                self.sm.current = 'Home'
                return True
        return False

if __name__=="__main__":
    MainApp().run()