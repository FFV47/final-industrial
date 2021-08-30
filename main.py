from kivymd.app import MDApp
from main_widget import MainWidget


class BasicApp(MDApp):
    def build(self):
        self.theme_cls.primary_pallete = "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_pallete = "Blue"
        return MainWidget()


if __name__ == "__main__":
    BasicApp().run()
