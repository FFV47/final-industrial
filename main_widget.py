from kivymd.uix.screen import MDScreen
from pyModbusTCP.client import ModbusClient
from orm_engine import init_db
from threading import Thread, Lock
from datetime import datetime
from time import sleep
from kivy.core.window import Window


class MainWidget(MDScreen):

    _is_update_enabled = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scan_time = kwargs["scan_time"]
        self._client = ModbusClient(host=kwargs["server_ip"], port=kwargs["server_port"])
        Session = init_db("database/scada.db")
        self._session = Session()
        self._lock = Lock()

    def _start_process(self):
        """
        Método para a configuração do IP e porta do servidor MODBUS e inicializar uma thread para a leitura dos dados da interface gráfica
        """

        try:
            Window.set_system_cursor("wait")
            self._client.open()
            Window.set_system_cursor("arrow")
            if self._client.is_open():
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
                self._read_data()
                # atualizar a interface
                self._update_gui()
                # gravar no banco de dados

                self._lock.acquire()
                self._lock.release()

                sleep(self._scan_time / 1000)
        except Exception as e:
            print("Erro -> ", e.args[0])
        finally:
            if self._lock.locked():
                self._lock.release()

    def _read_data(self):
        pass

    def _update_gui(self):
        pass

    def stop_refresh(self):
        self._update_widgets = False

    def get_data_db(self):
        """
        Coleta as informacoes da interface fornecidas pelo usuário e requisita a
        busca na DB
        """
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
