from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class Home(BoxLayout):
    pass

class MainApp(App):
    def build(self):
        return Home()

if __name__=="__main__":
    MainApp().run()