import json
import traceback
from datetime import datetime
from threading import Lock, Thread
from time import sleep

from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import BoxLayout
from pyModbusTCP.client import ModbusClient

from datacards import CardCoil, CardHoldingRegister, CardInputRegister
from frontend import DataGraphWidget, ObjectWidget, NewTagContent, GraphConfigContent
from models import EsteiraPrincipal, EsteiraSecundaria, Filtro
from orm_engine import init_db
import traceback


class MainWidget(MDScreen):

    _is_update_enabled = True

    tag_types = {
        "Input Register": "alpha-i-circle",
        "Holding Register": "alpha-h-circle",
        "Coil": "electric-switch",
    }

    def __init__(self, scan_time, server_ip, server_port, **kwargs):
        super().__init__(**kwargs)

        with open("tags.json") as tags_file:
            self._tags = json.load(tags_file)

        self.size_img_esteira = [958, 773]

        self._scan_time = scan_time
        self._modclient = ModbusClient(host=server_ip, port=server_port)
        Session = init_db("database/scada.db")
        self._session = Session()
        self._lock = Lock()
        self.create_datacards()

        self._modbusdata = {}
        for tag in self._tags:
            tag_name = tag["description"]
            self._modbusdata[tag_name] = 0

        self._current_obj = {}
        self._current_obj["peso_obj"] = 0
        self.new_obj = False

        self._current_obj["cor_obj_R"] = 0
        self._current_obj["cor_obj_G"] = 0
        self._current_obj["cor_obj_B"] = 0

        self._graph = DataGraphWidget(20, (1, 0, 0, 1))
        self.ids.graph_nav.add_widget(self._graph)

        self._est_1_list = []
        self._est_2_list = []
        self._est_3_list = []
        self._est_nc_list = []

        self.dialog = None
        self.dialog_hist = None

        # pode ser do tipo 'realtime' ou 'hist'
        self.graph_type = "realtime"

    def config_planta(self):
        self.show_dialog()
        print("Config planta")

    def update_filter(self, filt_key, value):
        for card in self.ids.modbus_data.children:
            if card.tag["description"] == filt_key:
                if card.tag["type"] == "holding":
                    card.set_data(int(value * 255))
                    card.write_data(value=int(value * 255))
                else:
                    card.set_data(value)
                    card.write_data(value=value)

    def show_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Configuração dos Filtros",
                type="custom",
                content_cls=NewTagContent(self.update_filter),
                buttons=[
                    MDFlatButton(text="Fechar", on_release=self.close_dialog),
                ],
            )
            self.dialog.content_cls.update_content(self._modbusdata)

        self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss(force=True)

    def show_dialog_hist(self):
        if not self.dialog_hist:
            self.dialog_hist = MDDialog(
                title="Dados Históricos",
                type="custom",
                content_cls=GraphConfigContent(self.read_dados_historicos),
                buttons=[
                    MDFlatButton(text="Fechar", on_release=self.close_dialog_hist),
                    MDFlatButton(text="Salvar", on_release=self.update_graph),
                ],
            )

        self.dialog_hist.open()

    def read_dados_historicos(self, timestamps, cols):
        try:
            init_date = datetime.strptime(timestamps[0], "%d/%m/%Y %H:%M:%S")
            final_date = datetime.strptime(timestamps[1], "%d/%m/%Y %H:%M:%S")

            self._lock.acquire()
            query = (
                self._session.query(EsteiraPrincipal)
                .filter(EsteiraPrincipal.timestamp.between(init_date, final_date))
                .all()
            )
            self._lock.release()

            dados = {}
            for col in cols:
                dados[col] = [getattr(obj, col) for obj in query]

            if dados is None or len(dados["timestamp"]) == 0:
                return None

            return dados

        except Exception as e:
            print("Erro na coleta de dados -> ", e.args)
            traceback.print_exc()

    def close_dialog_hist(self, *args):
        self.dialog_hist.dismiss(force=True)

    def create_datacards(self):
        """
        Cria os cards widgets na interface
        """
        for tag in self._tags:
            if tag["type"] == "input":
                self.ids.modbus_data.add_widget(
                    CardInputRegister(tag, self._modclient, lock=self._lock)
                )
            elif tag["type"] == "holding":
                self.ids.modbus_data.add_widget(
                    CardHoldingRegister(tag, self._modclient, lock=self._lock)
                )
            elif tag["type"] == "coil":
                self.ids.modbus_data.add_widget(
                    CardCoil(tag, self._modclient, lock=self._lock)
                )

    def connect(self):
        self._ev = []
        if self.ids.bt_con.text == "CONECTAR":

            self.ids.bt_con.text = "DESCONECTAR"
            try:
                self._modclient.host = self.ids.hostname.text
                self._modclient.port = int(self.ids.port.text)

                Window.set_system_cursor("wait")
                self._modclient.open()
                Window.set_system_cursor("arrow")
                if self._modclient.is_open():
                    self._start_process()

                    Snackbar(
                        text="Conexão realizada com sucesso", bg_color=(0, 1, 0, 1)
                    ).open()
                else:
                    print("Não foi possível conectar ao servidor")

            except Exception as e:
                print("Erro ao realizar a conexão com o servidor: ", e.args)
        else:
            self.ids.bt_con.text = "CONECTAR"

            if self._ev and len(self._ev):
                for event in self._ev:
                    event.cancel()

            self._modclient.close()
            Snackbar(text="Cliente desconectado", bg_color=(1, 0, 0, 1)).open()

    def _start_process(self):
        """
        Método para a configuração do IP e porta do servidor MODBUS e inicializar uma thread para a leitura dos dados da interface gráfica
        """

        try:
            if self._modclient.is_open():
                self._read_data()
                self._update_filter_DB()
                # Separa a interface do gerenciamento de dados

                self.update_thread = Thread(target=self._updater_loop)

                self.update_thread.start()
        except Exception as e:
            print("Erro ao iniciar thread ->", e.args[0])

    def _updater_loop(self, dt=None):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface e inserção dos dados no banco de dados
        """
        try:
            while self._is_update_enabled:
                # ler os dados
                self._read_data()
                # atualizar a interface
                Clock.schedule_once(self._update_gui)

                # gravar no banco de dados
                self._write_to_DB()

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
                tag_name = tag["description"]
                if tag_name not in self._modbusdata:
                    self._modbusdata[tag_name] = 0

                value = None

                self._lock.acquire()

                if tag["type"] == "input":
                    value = self._modclient.read_input_registers(tag["addr"], 1)
                elif tag["type"] == "holding":
                    value = self._modclient.read_holding_registers(tag["addr"], 1)
                elif tag["type"] == "coil":
                    value = self._modclient.read_coils(tag["addr"], 1)
                self._lock.release()

                if value is not None:
                    self._modbusdata[tag_name] = value[0]

            if (
                self._modbusdata["peso_obj"] != self._current_obj["peso_obj"]
                and self._modbusdata["peso_obj"] != 0
            ):
                self.new_obj = True
                self._current_obj["peso_obj"] = self._modbusdata["peso_obj"]
                self._current_obj["cor_obj_R"] = self._modbusdata["cor_obj_R"]
                self._current_obj["cor_obj_G"] = self._modbusdata["cor_obj_G"]
                self._current_obj["cor_obj_B"] = self._modbusdata["cor_obj_B"]
        except:
            traceback.print_exc()

    def _update_gui(self, dt=None):
        for card in self.ids.modbus_data.children:
            if card.tag["type"] != "coil" and card.tag["type"] != "holding":
                card.set_data(self._modbusdata[card.tag["description"]])

        if self.new_obj:
            self.new_obj = False
            obj_color = (
                self._current_obj["cor_obj_R"] / 255,
                self._current_obj["cor_obj_G"] / 255,
                self._current_obj["cor_obj_B"] / 255,
                1,
            )
            # Conf do filtro de cor da esteira 1
            filtro_cor_1 = (
                self._modbusdata["filtro_cor_r_1"] / 255,
                self._modbusdata["filtro_cor_g_1"] / 255,
                self._modbusdata["filtro_cor_b_1"] / 255,
                1,
            )
            # Conf do filtro de cor da esteira 2
            filtro_cor_2 = (
                self._modbusdata["filtro_cor_r_2"] / 255,
                self._modbusdata["filtro_cor_g_2"] / 255,
                self._modbusdata["filtro_cor_b_2"] / 255,
                1,
            )
            # Conf do filtro de cor da esteira 3
            filtro_cor_3 = (
                self._modbusdata["filtro_cor_r_3"] / 255,
                self._modbusdata["filtro_cor_g_3"] / 255,
                self._modbusdata["filtro_cor_b_3"] / 255,
                1,
            )

            # consulta qual filtro deve ser usado
            use_cor_1 = self._modbusdata["filtro_est_1"]
            use_cor_2 = self._modbusdata["filtro_est_2"]
            use_cor_3 = self._modbusdata["filtro_est_3"]

            obj_est_1_cor = obj_color == filtro_cor_1
            obj_est_1_massa = (
                self._current_obj["peso_obj"] == self._modbusdata["filtro_massa_1"]
            )

            obj_est_2_cor = obj_color == filtro_cor_2
            obj_est_2_massa = (
                self._current_obj["peso_obj"] == self._modbusdata["filtro_massa_2"]
            )

            obj_est_3_cor = obj_color == filtro_cor_3
            obj_est_3_massa = (
                self._current_obj["peso_obj"] == self._modbusdata["filtro_massa_3"]
            )

            new_obj = self.create_new_obj(obj_color)

            if (obj_est_1_cor and use_cor_1) or (obj_est_1_massa and not use_cor_1):
                new_obj.move_x([152, 645])
                self._est_1_list.append(new_obj)

            elif (obj_est_2_cor and use_cor_2) or (obj_est_2_massa and use_cor_2):
                new_obj.move_x([295, 645])
                self._est_2_list.append(new_obj)

            elif (obj_est_3_cor and use_cor_3) or (obj_est_3_massa and use_cor_3):
                new_obj.move_x([438, 645])
                self._est_3_list.append(new_obj)

            else:
                new_obj.move_x([574, 645])
                self._est_nc_list.append(new_obj)

        self.check_num_objs()

        if self.graph_type == "realtime":
            self._graph.ids.graph_peso.updateGraph(
                (datetime.now(), self._modbusdata["peso_obj"]), 0
            )
            self._graph.ids.graph_R.updateGraph(
                (datetime.now(), self._modbusdata["cor_obj_R"]), 0
            )
            self._graph.ids.graph_G.updateGraph(
                (datetime.now(), self._modbusdata["cor_obj_G"]), 0
            )
            self._graph.ids.graph_B.updateGraph(
                (datetime.now(), self._modbusdata["cor_obj_B"]), 0
            )

    def update_graph(self, button):

        show_peso = self.dialog_hist.content_cls.ids.graph_peso.active
        show_R = self.dialog_hist.content_cls.ids.graph_R.active
        show_G = self.dialog_hist.content_cls.ids.graph_G.active
        show_B = self.dialog_hist.content_cls.ids.graph_B.active

        graph_id_tag = {
            "graph_peso": "peso_obj",
            "graph_R": "cor_obj_R",
            "graph_G": "cor_obj_G",
            "graph_B": "cor_obj_B",
        }
        show_graphs = {
            "graph_peso": show_peso,
            "graph_R": show_R,
            "graph_G": show_G,
            "graph_B": show_B,
        }

        self._graph.update_graph_config(self.graph_type, show_graphs)

        if self.dialog_hist.content_cls.ids.realtime.active:
            self.graph_type = "realtime"
        elif self.dialog_hist.content_cls.ids.hist.active:
            self.graph_type = "hist"
            timestamps = [
                self.dialog_hist.content_cls.ids.init_date_txt.text,
                self.dialog_hist.content_cls.ids.final_date_txt.text,
            ]
            cols = ["timestamp"]
            for key, value in show_graphs.items():
                if value is True:
                    cols.append(graph_id_tag[key])
            dados_hist = self.read_dados_historicos(timestamps, cols)

            self._graph.update_graph_dados_hist(dados_hist)

    def check_num_objs(self):
        if (
            self._modbusdata["num_obj_est_1"] < len(self._est_1_list)
            and len(self._est_1_list) > 0
        ):
            obj = self._est_1_list.pop(0)
            self.ids.desenho.remove_widget(obj)
        if (
            self._modbusdata["num_obj_est_2"] < len(self._est_2_list)
            and len(self._est_2_list) > 0
        ):
            obj = self._est_2_list.pop(0)
            self.ids.desenho.remove_widget(obj)
        if (
            self._modbusdata["num_obj_est_3"] < len(self._est_3_list)
            and len(self._est_3_list) > 0
        ):
            obj = self._est_3_list.pop(0)
            self.ids.desenho.remove_widget(obj)
        if (
            self._modbusdata["num_obj_est_nc"] < len(self._est_nc_list)
            and len(self._est_nc_list) > 0
        ):
            obj = self._est_nc_list.pop(0)
            self.ids.desenho.remove_widget(obj)

    def stop_refresh(self):

        self._update_widgets = False
        self._is_update_enabled = False
        self._modclient.close()

    def create_new_obj(self, color):

        new_obj = ObjectWidget(
            size_img=self.size_img_esteira,
            obj_size=(50, 50),
            radius=[10, 10, 10, 10],
            pos_px=[762, 155],
            color=color,
        )
        self.ids.desenho.add_widget(new_obj)
        return new_obj

    def update_obj_color(self):
        self.rectangle.update_color(
            (
                self._current_obj["cor_obj_R"],
                self._current_obj["cor_obj_G"],
                self._current_obj["cor_obj_B"],
                1,
            )
        )

    def _write_to_DB(self):
        principal = EsteiraPrincipal(
            timestamp=datetime.now().replace(microsecond=0),
            estado_atuador=self._modbusdata["estado_atuador"],
            bt_on_off=self._modbusdata["bt_on_off"],
            t_part=self._modbusdata["t_part"],
            freq_des=self._modbusdata["freq_des"],
            freq_mot=self._modbusdata["freq_mot"],
            tensao=self._modbusdata["tensao"],
            rotacao=self._modbusdata["rotacao"],
            pot_entrada=self._modbusdata["pot_entrada"],
            corrente=self._modbusdata["corrente"],
            temp_estator=self._modbusdata["temp_estator"],
            vel_esteira=self._modbusdata["vel_esteira"],
            carga=self._modbusdata["carga"],
            peso_obj=self._modbusdata["peso_obj"],
            cor_obj_R=self._modbusdata["cor_obj_R"],
            cor_obj_G=self._modbusdata["cor_obj_G"],
            cor_obj_B=self._modbusdata["cor_obj_B"],
        )

        secundaria = EsteiraSecundaria(
            timestamp=datetime.now().replace(microsecond=0),
            num_obj_est_1=self._modbusdata["num_obj_est_1"],
            num_obj_est_2=self._modbusdata["num_obj_est_2"],
            num_obj_est_3=self._modbusdata["num_obj_est_3"],
            num_obj_est_nc=self._modbusdata["num_obj_est_nc"],
            filtro_est_1=self._modbusdata["filtro_est_1"],
            filtro_est_2=self._modbusdata["filtro_est_2"],
            filtro_est_3=self._modbusdata["filtro_est_3"],
        )

        self._lock.acquire()
        self._session.add(principal)
        self._session.add(secundaria)
        self._session.commit()
        self._lock.release()

    def _update_filter_DB(self):
        filtro = Filtro(
            timestamp=datetime.now().replace(microsecond=0),
            cor_r_1=self._modbusdata["filtro_cor_r_1"],
            cor_g_1=self._modbusdata["filtro_cor_g_1"],
            cor_b_1=self._modbusdata["filtro_cor_b_1"],
            massa_1=self._modbusdata["filtro_massa_1"],
            cor_r_2=self._modbusdata["filtro_cor_r_2"],
            cor_g_2=self._modbusdata["filtro_cor_g_2"],
            cor_b_2=self._modbusdata["filtro_cor_b_2"],
            massa_2=self._modbusdata["filtro_massa_2"],
            cor_r_3=self._modbusdata["filtro_cor_r_3"],
            cor_g_3=self._modbusdata["filtro_cor_g_3"],
            cor_b_3=self._modbusdata["filtro_cor_b_3"],
            massa_3=self._modbusdata["filtro_massa_3"],
        )

        self._lock.acquire()
        self._session.add(filtro)
        self._session.commit()
        self._lock.release()
