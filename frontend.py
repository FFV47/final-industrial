import copy

from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy_garden.graph import LinePlot

from timeseriesgraph import TimeSeriesGraph


class NewTagContent(BoxLayout):
    def __init__(self, update_func, **kwargs):
        self.update_func = update_func
        super().__init__(**kwargs)

    def update_filter(self, checkbox, value, filt_key, filt_type=None):
        if filt_type == "Massa":
            value = not value
        if isinstance(value, bool):
            self.update_func(filt_key, value)

    def update_content(self, modbusdata):
        ids = self.ids.keys()
        valid_keys = set(ids).intersection(modbusdata.keys())
        for key in valid_keys:
            self.ids[key].active = modbusdata[key]
        self.ids["filtro_est_1_massa"].active = not modbusdata["filtro_est_1"]
        self.ids["filtro_est_2_massa"].active = not modbusdata["filtro_est_2"]
        self.ids["filtro_est_3_massa"].active = not modbusdata["filtro_est_3"]


class GraphConfigContent(BoxLayout):
    def __init__(self, update_func, **kwargs):
        self.update_func = update_func
        self.graph_type = "realtime"
        super().__init__(**kwargs)

    def update_config(self, checkbox, value, filt_key, graph_type=None):
        if self.graph_type != graph_type:
            if isinstance(value, bool):
                self.update_func(filt_key, value)


class DataGraphWidget(BoxLayout):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)

        self.graph_type = "realtime"

        self.xmax = xmax
        self.graph_dict = {}

        self.plot = LinePlot(line_width=1.5, color=(1, 1, 1, 1))
        self.ids.graph_peso.add_plot(self.plot)
        self.ids.graph_peso.xmax = xmax

        self.graph_dict["graph_peso"] = self.ids["graph_peso"]

        self.plot = LinePlot(line_width=1.5, color=(1, 0, 0, 1))
        self.ids.graph_R.add_plot(self.plot)
        self.ids.graph_R.xmax = xmax

        self.graph_dict["graph_R"] = self.ids["graph_R"]

        self.plot = LinePlot(line_width=1.5, color=(0, 1, 0, 1))
        self.ids.graph_G.add_plot(self.plot)
        self.ids.graph_G.xmax = xmax

        self.graph_dict["graph_G"] = self.ids["graph_G"]

        self.plot = LinePlot(line_width=1.5, color=(0, 0, 1, 1))
        self.ids.graph_B.add_plot(self.plot)
        self.ids.graph_B.xmax = xmax

        self.graph_dict["graph_B"] = self.ids["graph_B"]

        self.graph_ids = ["graph_peso", "graph_R", "graph_G", "graph_B"]
        self.active_graphs = {
            "graph_peso": True,
            "graph_R": True,
            "graph_G": True,
            "graph_B": True,
        }
        self.graph_id_tag = {
            "graph_peso": "peso_obj",
            "graph_R": "cor_obj_R",
            "graph_G": "cor_obj_G",
            "graph_B": "cor_obj_B",
        }

        self.graph_colors = {
            "graph_peso": (1, 1, 1, 1),
            "graph_R": (1, 0, 0, 1),
            "graph_G": (0, 1, 0, 1),
            "graph_B": (0, 0, 1, 1),
        }

    def update_graph_config(self, graph_type, show_graphs):
        if self.graph_type != graph_type:
            self.graph_type = graph_type
            update_graph_type = True
        else:
            update_graph_type = False

        if update_graph_type and self.graph_type == "realtime":
            for graph in self.graph_dict.values():
                graph.clearPlots()
                plot = LinePlot(line_width=1.5, color=(1, 1, 1, 1))
                graph.add_plot(plot)
                graph.xmax = self.xmax
        for graph_id in self.graph_ids:
            graph = self.graph_dict[graph_id]
            if self.active_graphs[graph_id] != show_graphs[graph_id]:
                self.active_graphs[graph_id] = show_graphs[graph_id]
                if show_graphs[graph_id]:
                    self.add_widget(self.graph_dict[graph_id])
                else:
                    self.remove_widget(self.graph_dict[graph_id])

    def update_graph_dados_hist(self, dados):

        if dados is not None:
            for graph_id in self.graph_ids:

                self.ids[graph_id].clearPlots()

                for key, value in dados.items():
                    if key == "timestamp":
                        continue
                    elif key == self.graph_id_tag[graph_id]:
                        p = LinePlot(line_width=1.5, color=self.graph_colors[graph_id])
                        p.points = [(x, value[x]) for x in range(0, len(value))]
                        self.ids[graph_id].add_plot(p)
                        self.ids[graph_id].update_x_labels(dados["timestamp"])


class MyRoundedRectangle(RoundedRectangle):
    def __init__(self, size_img, pos_hint=None, **kwargs) -> None:
        super().__init__(**kwargs)

        self.pos_hint = pos_hint
        self.size_img = size_img
        self.update_position(pos_hint)

    def update_position(self, pos_hint, parent_size=[1280, 600]):
        self.pos_hint = pos_hint
        if pos_hint != None:
            self.pos = (
                parent_size[0] * pos_hint["center_x"] - self.size[0] / 2,
                parent_size[1] * pos_hint["center_y"] - self.size[1] / 2,
            )


class ObjectWidget(Widget):

    background_color = ListProperty((0.5, 0.5, 0.5, 1))
    color_property = ListProperty((1, 0, 0, 1))

    def __init__(self, size_img, obj_size, pos_px, radius, color, **kwargs):

        super(ObjectWidget, self).__init__(**kwargs)

        # self.remove_listener = remove_listener
        self.speed = 2
        # Arranging Canvas
        with self.canvas:

            self.rect_color = Color(rgba=color)  # set the colour

            # Seting the size and position of image
            # image must be in same folder

            self.size_img = size_img

            self.rect_pos_px = pos_px
            self.rect_pos_hint = self.px2pos_hint(pos_px)
            new_pos_hint = self.new_pos_hint(self.rect_pos_hint)
            self.rect = MyRoundedRectangle(
                size=obj_size, size_img=size_img, radius=radius, pos_hint=new_pos_hint
            )

            # Update the canvas as the screen size change
            # if not use this next 5 line the
            # code will run but not cover the full screen

            self.bind(pos=self.update_rect, size=self.update_rect)

    # update function which makes the canvas adjustable.
    def update_rect(self, *args):
        new_pos_hint = self.new_pos_hint(self.rect_pos_hint)
        self.rect.update_position(new_pos_hint, parent_size=self.size)

    def update_color(self, color):
        self.rect_color.rgba = color

    def get_size(self):
        return [self.width, self.height]

    def new_pos_hint(self, pos_hint):
        """Calcula novo pos_hint considerando as bordas da imagem causada pela diferença
        de tamanho entra a imagem da esteira e o widget onde ela foi inserida
        """

        parent_size = self.size
        # corrige falsa leitura de tamanho na inicialização do código
        if parent_size == [100, 100]:
            parent_size = [1280, 600]

        # calcula largura real da imagem a partir da proporção da altura entre a imagem e o widget pai
        img_width = self.size_img[0] * (parent_size[1] / self.size_img[1])

        # cria uma copia sem referencia ao dicionario original
        new_pos_hint = copy.deepcopy(pos_hint)

        # ajusta o pos_hint proporcionalmente a diferença de largura da imagem e o widget pai
        new_pos_hint["center_x"] = (pos_hint["center_x"] - 0.5) * (
            img_width / parent_size[0]
        ) + 0.5

        return new_pos_hint

    def set_rect_pos_px(self, position_px):
        """Muda posicao da caixa em relação a imagem da esteira em pixels"""

        self.rect_pos_px = position_px
        self.rect_pos_hint = self.px2pos_hint(position_px)
        new_pos_hint = self.new_pos_hint(self.rect_pos_hint)
        self.rect.update_position(new_pos_hint, parent_size=self.size)

    def px2pos_hint(self, pos_px):
        """Calcula o pos_hint relativo a imagem da esteira"""

        pos_hint_x = pos_px[0] / self.size_img[0]
        pos_hint_y = (self.size_img[1] - pos_px[1]) / self.size_img[1]
        pos_hint = {"center_x": pos_hint_x, "center_y": pos_hint_y}
        return pos_hint

    def move_x(self, pos_px):

        self.target_rect_pos_px = pos_px
        self._ev = Clock.schedule_interval(self.update_movement_x, 1 / 20)

    def update_movement_x(self, dt):
        if self.rect_pos_px[0] > self.target_rect_pos_px[0]:
            self.rect_pos_px[0] -= self.speed
            self.set_rect_pos_px(self.rect_pos_px)
        else:
            self.move_y(self.target_rect_pos_px)
            return False

    def move_y(self, pos_px):

        self.target_rect_pos_px = pos_px
        self._ev = Clock.schedule_interval(self.update_movement_y, 1 / 20)

    def update_movement_y(self, dt):
        if self.rect_pos_px[1] < self.target_rect_pos_px[1]:
            self.rect_pos_px[1] += self.speed
            self.set_rect_pos_px(self.rect_pos_px)
        else:
            return False

    def remove(self):
        self.remove_listener(self)
