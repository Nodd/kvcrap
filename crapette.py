import kivy

kivy.require("1.11.0")
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout


class BackGround(FloatLayout):
    pass


# main app
class CrapetteApp(App):
    def build(self):
        self.title = "Crapette in Kivy"
        self.icon = "images/png/2x/suit-spade.png"


if __name__ == "__main__":
    CrapetteApp().run()
