from kivy.base import Builder
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu

Builder.load_file("pages.kv")

class RoundedButton(Button):
    pass
class SetPage(SettingsWithNoMenu):
    pass

class Page3(Screen):
    pass