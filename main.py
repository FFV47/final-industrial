from kivymd.app import MDApp
from main_widget import MainWidget
from kivy.config import Config
from kivy.core.window import Window
Config.set('kivy', 'exit_on_escape', '0')


class BasicApp(MDApp):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        self.theme_cls.primary_pallete = "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_pallete = "Blue"
        self.main_widget = MainWidget(scan_time=1,server_ip="127.0.0.1",server_port=502)
        return self.main_widget

    def on_request_close(self, *args):
        print("Closing")
        self.main_widget.stop_refresh()
        self.stop()


if __name__ == '__main__':
    Window.size = (1280,720)
    BasicApp().run()
