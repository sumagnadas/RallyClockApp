from kivy.app import App
from kivy.uix.widget import Widget

class HomeWidget(Widget):
    pass

class MainApp(App):
    def build(self):
        return HomeWidget()

if __name__=="__main__":
    MainApp().run()