from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy_garden.graph import LinePlot
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.graphics import Color
from timeseriesgraph import TimeSeriesGraph
import copy

class DataGraphWidget(BoxLayout):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width=1.5, color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax


class MyRoundedRectangle(RoundedRectangle):
    def __init__(self, size_img, pos_hint=None, **kwargs) -> None:
        super().__init__(**kwargs)

        self.my_pos_hint = pos_hint
        self.size_img = size_img
        self.update_position(pos_hint)

    def update_position(self, pos_hint, parent_size=[1280,600]):

        if pos_hint != None:
            self.pos = (parent_size[0]*pos_hint['center_x'] - self.size[0]/2,
                        parent_size[1]*pos_hint['center_y'] - self.size[1]/2)   


class ObjectWidget(Widget):

    background_color = ListProperty((0.5,0.5,0.5,1))
    color_property = ListProperty((1,0,0,1))
      
    def __init__(self, size_img, obj_size, pos_px, radius, **kwargs):
  
        super(ObjectWidget, self).__init__(**kwargs)

        # Arranging Canvas
        with self.canvas:
  
            self.rect_color = Color(rgba=(1,0,0,1))  # set the colour 
  
            # Seting the size and position of image
            # image must be in same folder      
            
            self.size_img = size_img  

            self.rect_pos_hint = self.px2pos_hint(pos_px)
            new_pos_hint = self.new_pos_hint(self.rect_pos_hint)
            self.rect =  MyRoundedRectangle( size = obj_size, size_img=size_img, radius=radius, pos_hint=new_pos_hint)
            
            # Update the canvas as the screen size change
            # if not use this next 5 line the
            # code will run but not cover the full screen

            self.bind(pos = self.update_rect, size = self.update_rect)
  
    # update function which makes the canvas adjustable.
    def update_rect(self, *args):
        new_pos_hint = self.new_pos_hint(self.rect_pos_hint)
        self.rect.update_position(new_pos_hint, parent_size=self.size)
        

    def update_color(self,color):
        self.rect_color.rgba = color

    def get_size(self):
        return [self.width, self.height]

    def new_pos_hint(self, pos_hint):
        """ Calcula novo pos_hint considerando as bordas da imagem causada pela diferença 
            de tamanho entra a imagem da esteira e o widget onde ela foi inserida
         """

        parent_size = self.size
        # corrige falsa leitura de tamanho na inicialização do código
        if parent_size == [100,100]:
            parent_size = [1280,600]

        # calcula largura real da imagem a partir da proporção da altura entre a imagem e o widget pai
        img_width = self.size_img[0] * (parent_size[1]/self.size_img[1])

        # cria uma copia sem referencia ao dicionario original 
        new_pos_hint = copy.deepcopy(pos_hint)

        # ajusta o pos_hint proporcionalmente a diferença de largura da imagem e o widget pai
        new_pos_hint['center_x'] = (pos_hint['center_x'] - 0.5) * (img_width / parent_size[0]) + 0.5

        return new_pos_hint

    
    def set_rect_pos_px(self, position_px):
        """ Muda posicao da caixa em relação a imagem da estera em pixels """

        self.rect_pos_hint = self.px2pos_hint(position_px)
        new_pos_hint = self.new_pos_hint(self.rect_pos_hint)
        self.rect.update_position(new_pos_hint, parent_size=self.size)
    
    def px2pos_hint(self, pos_px):
        """ Calcula o pos_hint relativo a imagem da esteira """

        pos_hint_x = pos_px[0]/self.size_img[0]
        pos_hint_y = (self.size_img[1]-pos_px[1])/self.size_img[1]
        pos_hint = {'center_x': pos_hint_x, 'center_y': pos_hint_y}
        return pos_hint
