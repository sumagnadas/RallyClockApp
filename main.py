"""
This script is the main script which is run when the app is opened
It starts the main thread as well as setup the app for running

"""

__version__ = "2.1"
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import NoTransition, ScreenManager

from globals import update_clock
from pages import Home, SetPage


class MainApp(App):
    """Class for the main app"""

    sm = ScreenManager(transition=NoTransition())
    use_kivy_settings = False

    def build(self):
        Clock.schedule_interval(update_clock, 0.1)
        home = Home(name="Home")
        self.sm.add_widget(home)
        self.sm.add_widget(SetPage(name="Settings", version=__version__))

        win = Window
        win.bind(on_keyboard=self.my_key_handler)
        return self.sm

    def my_key_handler(self, window, keycode1, keycode2, text, modifiers):
        if keycode1 in [27, 1001]:
            if self.sm.current == "Home":
                return False
            else:
                self.sm.current = "Home"
                return True
        return False


if __name__ == "__main__":
    MainApp().run()
