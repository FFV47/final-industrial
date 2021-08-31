from copy import Error
import traceback
from kivymd.uix import boxlayout
from kivymd.uix.screen import MDScreen
# from kivymd.uix.boxlayout import BoxLayout
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


class MyRoundedRectangle(RoundedRectangle):
    def __init__(self, pos_hint=None, **kwargs) -> None:
        super().__init__(**kwargs)

        self.pos_hint = pos_hint

    def update_position(self, parent_size):
        if self.pos_hint != None:
            self.pos = (parent_size[0]*self.pos_hint['center_x'] - self.size[0]/2,
                        parent_size[1]*self.pos_hint['center_y'] - self.size[1]/2)   

class CanvasWidget(Widget):
      
    def __init__(self, size, pos_hint, radius, **kwargs):
  
        super(CanvasWidget, self).__init__(**kwargs)

        # Arranging Canvas
        with self.canvas:
  
            self.color = [1, 0, 0, 1]
            Color(rgba=self.color)  # set the colour 
  
            # Seting the size and position of image
            # image must be in same folder 
            
        
            self.rect =  MyRoundedRectangle( size = size, radius=radius, pos_hint=pos_hint)
            
            # Update the canvas as the screen size change
            # if not use this next 5 line the
            # code will run but not cover the full screen

            self.bind(pos = self.update_rect, size = self.update_rect)
  
    # update function which makes the canvas adjustable.
    def update_rect(self, *args):
        self.rect.update_position(self.size)
        
        # self.rect.size = self.size


class MainWidget(MDScreen):

    _is_update_enabled = True

    tag_types = {  'Input Register':   'alpha-i-circle',
                    'Holding Register': 'alpha-h-circle',
                    'Coil':             'electric-switch'}

    _tags = [   {'description':'estado_atuador', 'addr': 801, 'type': 'coil', 'mult': None},
                {'description':'bt_on_off','addr':802, 'type': 'coil', 'mult': None},
                {'description':'t_part','addr':798, 'type': 'holding', 'mult': 10},
                {'description':'freq_des','addr':799, 'type': 'holding', 'mult': 1},
                {'description':'freq_mot','addr':800, 'type': 'input', 'mult': 10},
                {'description':'tensao','addr':801, 'type': 'input', 'mult': 1},
                {'description':'rotacao','addr':803, 'type': 'input', 'mult': 1},
                {'description':'pot_entrada','addr':804, 'type': 'input', 'mult': 10},
                {'description':'corrente','addr':805, 'type': 'input', 'mult': 100},
                {'description':'temp_estator','addr':806, 'type': 'input', 'mult': 10},
                {'description':'vel_esteira','addr':807, 'type': 'input', 'mult': 100},
                {'description':'carga','addr':808, 'type': 'input', 'mult': 100},
                {'description':'peso_obj','addr':809, 'type': 'input', 'mult': 1},
                {'description': 'cor_obj_R','addr':810, 'type': 'input', 'mult': 1},
                {'description': 'cor_obj_G','addr':811, 'type': 'input', 'mult': 1},
                {'description':'cor_obj_B','addr':812, 'type': 'input', 'mult': 1},

                {'description': 'numObj_est_1','addr':813, 'type': 'input', 'mult': 1},
                {'description': 'numObj_est_2','addr':814, 'type': 'input', 'mult': 1},
                {'description': 'numObj_est_3','addr':815, 'type': 'input', 'mult': 1},
                {'description': 'numObj_est_nc','addr':816, 'type': 'input', 'mult': 1},
                {'description': 'filtro_est_1','addr':901, 'type': 'coil', 'mult': None},
                {'description': 'filtro_est_2','addr':902, 'type': 'coil', 'mult': None},
                {'description': 'filtro_est_3','addr':903, 'type': 'coil', 'mult': None},

                {'description': 'filtro_cor_r_1','addr':1001, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_g_1','addr':1002, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_b_1','addr':1003, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_massa_1','addr':1004, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_r_2','addr':1011, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_g_2','addr':1012, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_b_2','addr':1013, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_massa_2','addr':1014, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_r_3','addr':1021, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_g_3','addr':1022, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_cor_b_3','addr':1023, 'type': 'holding', 'mult': 1},
                {'description': 'filtro_massa_3','addr':1024, 'type': 'holding', 'mult': 1},
    ]

    def __init__(self, scan_time, server_ip, server_port, **kwargs):
        super().__init__(**kwargs)
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
                for card in self.ids.modbus_data.children:
                    if card.tag['type'] == "holding" or card.tag['type'] == "coil":
                        self._ev.append(Clock.schedule_once(card.update_data))
                    else:
                        self._ev.append(Clock.schedule_interval(card.update_data,self._scan_time))
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
                update_thread = Thread(target=self._updater_loop)
                update_thread.start()
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
                # self._read_data()
                self._lock.release()
                # atualizar a interface
                self._update_gui()
                # gravar no banco de dados


                

                sleep(self._scan_time / 1000)
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
                    self._modbusdata[tag['description']] = {'value':0}        

                value = None
                
               
                if tag['type'] == "input":
                    value = self._modclient.read_input_registers(tag['addr'],1)
                elif tag['type'] == "holding":
                    value = self._modclient.read_holding_registers(tag['addr'],1)
                elif tag['type'] == "coil":
                    value = self._modclient.read_coils(tag['addr'],1)
                if value != None:
                    self._modbusdata[tag['description']]['value'] = value[0]
                # else:
                #     print("Erro de leitura")
               

            if self._modbusdata['peso_obj']['value'] != self._current_obj['peso_obj'] and self._modbusdata['peso_obj']['value'] != 0:
                self.new_obj = True
                self._current_obj['peso_obj'] = self._modbusdata['peso_obj']['value']
        except:
            traceback.print_exc()
        
        
    def _update_gui(self):
        if self.new_obj:
            self.new_obj = False
            self.update_obj_color()


    def stop_refresh(self):
        self._update_widgets = False

    
    def create_new_obj(self):
        self.rectangle = CanvasWidget(size=(100,100),pos_hint={'center_x': 0.4, 'center_y': 0.4},radius=[10, 10, 10, 10])
        self.ids.desenho.add_widget(self.rectangle)

    def update_obj_color(self):
        print(self.rectangle.color)
        self.rectangle.color[0] = self._modbusdata['cor_obj_R']['value']
        self.rectangle.color[1] = self._modbusdata['cor_obj_G']['value']
        self.rectangle.color[2] = self._modbusdata['cor_obj_B']['value']


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
