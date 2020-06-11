import kivy

kivy.require("1.11.0")
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout


class BackGround(FloatLayout):
    pass


class FoundationWidget(RelativeLayout):
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            print("fufu", touch)


class TableauWidgetLeft(RelativeLayout):
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            print("tata left", touch)


class TableauWidgetRight(RelativeLayout):
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            print("tata right", touch)


class PlayerPileWidget(RelativeLayout):
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            print("player", touch)


# main app
class CrapetteApp(App):
    def build(self):
        self.title = "Crapette in Kivy"
        self.icon = "images/png/2x/suit-spade.png"


if __name__ == "__main__":
    CrapetteApp().run()
