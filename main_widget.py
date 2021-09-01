import traceback
from kivymd.uix.screen import MDScreen
from pyModbusTCP.client import ModbusClient
from orm_engine import init_db
from threading import Thread, Lock
from datetime import datetime
from time import sleep
from kivy.core.window import Window
from datacards import CardCoil, CardHoldingRegister, CardInputRegister
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
import json
from timeseriesgraph import TimeSeriesGraph
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime


class DataGraphWidget(BoxLayout):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width=1.5, color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax


class MyRoundedRectangle(RoundedRectangle):
    def __init__(self, pos_hint=None, **kwargs) -> None:
        super().__init__(**kwargs)

        self.pos_hint = pos_hint

    def update_position(self, parent_size):
        if self.pos_hint != None:
            self.pos = (parent_size[0]*self.pos_hint['center_x'] - self.size[0]/2,
                        parent_size[1]*self.pos_hint['center_y'] - self.size[1]/2)   

class ObjectWidget(Widget):

    background_color = ListProperty((0.5,0.5,0.5,1))
    color_property = ListProperty((1,0,0,1))
      
    def __init__(self, size, obj_size, pos_hint, radius, **kwargs):
  
        super(ObjectWidget, self).__init__(**kwargs)

        # Arranging Canvas
        with self.canvas:
  
            self.rect_color = Color(rgba=(1,0,0,1))  # set the colour 
  
            # Seting the size and position of image
            # image must be in same folder        

            pos_hint = self.new_pos_hint(pos_hint)

            self.rect =  MyRoundedRectangle( size = obj_size, radius=radius, pos_hint=pos_hint)
            
            # Update the canvas as the screen size change
            # if not use this next 5 line the
            # code will run but not cover the full screen

            self.bind(pos = self.update_rect, size = self.update_rect)
  
    # update function which makes the canvas adjustable.
    def update_rect(self, *args):
        self.rect.update_position(self.size)
        
        # self.rect.size = self.size

    def update_color(self,color):
        self.rect_color.rgba = color

    def get_size(self):
        return [self.width, self.height]

    def new_pos_hint(self,pos_hint):
        img_width = 743

        new_pos_hint = pos_hint
        print(pos_hint)
        new_pos_hint['center_x'] = (pos_hint['center_x'] - 0.5) * (img_width / 1280) + 0.5
        print(new_pos_hint)
        return new_pos_hint



class MainWidget(MDScreen):

    _is_update_enabled = True

    tag_types = {  'Input Register':   'alpha-i-circle',
                    'Holding Register': 'alpha-h-circle',
                    'Coil':             'electric-switch'}


    def __init__(self, scan_time, server_ip, server_port, **kwargs):
        super().__init__(**kwargs)

        with open('tags.txt') as tags_file:
            self._tags = json.load(tags_file)

        self.size_img_esteira = [958,773]

        self._scan_time = scan_time
        self._modclient = ModbusClient(host=server_ip, port=server_port)
        Session = init_db("database/scada.db")
        self._session = Session()
        self._lock = Lock()
        self.create_datacards()
        self._modbusdata = {}
        self._current_obj = {'peso_obj':0}
        self.new_obj = False
        self.create_new_obj()
        self._graph = DataGraphWidget(20,(1,0,0,1))
        self.ids.graph_nav.add_widget(self._graph)



    def create_datacards(self):
        for tag in self._tags:
            if tag['type'] == "input":
                self.ids.modbus_data.add_widget(CardInputRegister(tag,self._modclient))
            elif tag['type'] == "holding":
                self.ids.modbus_data.add_widget(CardHoldingRegister(tag,self._modclient))
            elif tag['type'] == "coil":
                self.ids.modbus_data.add_widget(CardCoil(tag,self._modclient))


    def connect(self):
        if self.ids.bt_con.text == "CONECTAR":
            self.ids.bt_con.text = "DESCONECTAR"
            try:
                self._modclient.host = self.ids.hostname.text
                self._modclient.port = int(self.ids.port.text)
                self._modclient.open()
                self._start_process()
                Snackbar(text="Conexão realizada com sucesso", bg_color=(0,1,0,1)).open()
                self._ev = []
                # for card in self.ids.modbus_data.children:
                #     if card.tag['type'] == "holding" or card.tag['type'] == "coil":
                #         self._ev.append(Clock.schedule_once(card.update_data))
                #     else:
                #         self._ev.append(Clock.schedule_interval(card.update_data,self._scan_time))
            except Exception as e:
                print("Erro ao realizar a conexão com o servidor: ",e.args)
        else:
            self.ids.bt_con.text = "CONECTAR"
            for event in self._ev:
                event.cancel()
            self._modclient.close()
            Snackbar(text="Cliente desconectado", bg_color=(1,0,0,1)).open()

    def _start_process(self):
        """
        Método para a configuração do IP e porta do servidor MODBUS e inicializar uma thread para a leitura dos dados da interface gráfica
        """

        try:
            Window.set_system_cursor("wait")
            # self._modclient.open()
            Window.set_system_cursor("arrow")
            if self._modclient.is_open():
                # Separa a interface do gerenciamento de dados
                self.update_thread = Thread(target=self._updater_loop)
                self.update_thread.start()
        except Exception as e:
            print("Erro de conexão ->", e.args[0])

    def _updater_loop(self):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface e inserção dos dados no banco de dados
        """
        try:
            while self._is_update_enabled:
                # ler os dados
                self._lock.acquire()
                self._read_data()
                self._lock.release()
                # atualizar a interface
                self._update_gui()
                # gravar no banco de dados

                sleep(self._scan_time)
        except Exception as e:
            print("Erro -> ", e.args)
            traceback.print_exc()
        finally:
            if self._lock.locked():
                self._lock.release()

    def _read_data(self):
        try:
            for tag in self._tags:
                if tag['description'] not in self._modbusdata:
                    self._modbusdata[tag['description']] = 0      

                value = None
                
               
                if tag['type'] == "input":
                    value = self._modclient.read_input_registers(tag['addr'],1)
                elif tag['type'] == "holding":
                    value = self._modclient.read_holding_registers(tag['addr'],1)
                elif tag['type'] == "coil":
                    value = self._modclient.read_coils(tag['addr'],1)
                if value != None:
                    self._modbusdata[tag['description']] = value[0]
                # else:
                #     print("Erro de leitura")

               

            if self._modbusdata['peso_obj'] != self._current_obj['peso_obj'] and self._modbusdata['peso_obj'] != 0:
                self.new_obj = True
                self._current_obj['peso_obj'] = self._modbusdata['peso_obj']
                self._current_obj['cor_obj_R'] = self._modbusdata['cor_obj_R']
                self._current_obj['cor_obj_G'] = self._modbusdata['cor_obj_G']
                self._current_obj['cor_obj_B'] = self._modbusdata['cor_obj_B']
                print(self.rectangle.get_size())
        except:
            traceback.print_exc()
        
        
    def _update_gui(self):
        for card in self.ids.modbus_data.children:
            card.set_data(self._modbusdata[card.tag['description']])

        if self.new_obj:
            self.new_obj = False
            self.update_obj_color()

        self._graph.ids.graph.updateGraph((datetime.now(),self._modbusdata['tensao']),0)
        print(self.ids.esteira_img.size)


    def stop_refresh(self):
        self._update_widgets = False
        self._is_update_enabled = False

    
    def create_new_obj(self):
        pos_hint={'center_x': 750/self.size_img_esteira[0], 'center_y': (self.size_img_esteira[1]-150)/self.size_img_esteira[1]}
        self.rectangle = ObjectWidget(size=self.size_img_esteira, obj_size=(50,50),pos_hint=pos_hint,radius=[10, 10, 10, 10])
        self.ids.desenho.add_widget(self.rectangle)
        print(self.rectangle.get_size())


    def update_obj_color(self):
        print(self._current_obj)
        self.rectangle.update_color((self._current_obj['cor_obj_R'],self._current_obj['cor_obj_G'],self._current_obj['cor_obj_B'],1))


    def get_data_db(self):
        """
        Coleta as informacoes da interface fornecidas pelo usuário e requisita a
        busca na DB
        """
        pass
        # try:
        #     init_date = datetime.strptime(
        #         self._hist_graph.ids.txt_init_time.text, "%d/%m/%Y %H:%M:%S"
        #     )
        #     final_date = datetime.strptime(
        #         self._hist_graph.ids.txt_final_time.text, "%d/%m/%Y %H:%M:%S"
        #     )

        #     cols = []
        #     for sensor in self._hist_graph.ids.sensores.children:
        #         if sensor.ids.check_box.active:
        #             cols.append(sensor.id)

        #     if init_date is None or final_date is None or len(cols) == 0:
        #         return

        #     cols.append("timestamp")

        #     self._lock.acquire()

        #     self._lock.release()

        #     dados = {}
        #     for col in cols:
        #         if col == "timestamp":
        #             dados[col] = [
        #                 getattr(obj, col).strftime("%d/%m/%Y %H:%M:%S") for obj in query
        #             ]
        #         else:
        #             dados[col] = [getattr(obj, col) for obj in query]

        #     if dados is None or len(dados["timestamp"]) == 0:
        #         return

        #     self._hist_graph.ids.graph.clearPlots()

        #     for key, value in dados.items():
        #         if key == "timestamp":
        #             continue
        #         p = LinePlot(line_width=1.5, color=self._tags[key]["color"])
        #         p.points = [(x, value[x]) for x in range(len(value))]
        #         self._hist_graph.ids.graph.add_plot(p)

        #     self._hist_graph.ids.graph.xmax = len(dados[cols[0]])
        #     self._hist_graph.ids.graph.update_x_labels(
        #         [datetime.strptime(x, "%d/%m/%Y %H:%M:%S") for x in dados["timestamp"]]
        #     )

        # except Exception as e:
        #     print("Erro na coleta de dados -> ", e.args[0])
