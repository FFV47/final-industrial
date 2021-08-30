from kivymd.uix.card import MDCard
from pyModbusTCP.client import ModbusClient


class DataCard(MDCard):
    title = "Data Card"

    def __init__(self, tag: dict, client: ModbusClient, **kwargs):
        self.tag = tag
        self.title = tag["description"]
        self._client = client
        super().__init__(**kwargs)

    def update_data(self, dt):
        try:
            if self._client.is_open():
                self.set_data(self._read_data(self.tag["address"], 1)[0])
        except Exception as e:
            print("Erro ao realizar a leitura do dado -> ")
            for e in e.args:
                print(e)

    def write_data(self):
        try:
            if self._client.is_open():
                self._write_data_fcn(self.tag["address"], self.get_data())
        except Exception as e:
            print("Erro ao realizar a escrita do dado -> ")
            for e in e.args:
                print(e)


class CardHoldingRegister(DataCard):
    def __init__(self, tag: dict, client: ModbusClient, **kwargs):
        super().__init__(tag, client, **kwargs)
        self._read_data = self._client.read_holding_registers
        self._write_data_fcn = self._client.write_single_register

    def set_data(self, data):
        self.ids.textfield.text = str(data)

    def get_data(self):
        return int(self.ids.textfield.text)


class CardInputRegister(DataCard):
    def __init__(self, tag: dict, client: ModbusClient, **kwargs):
        super().__init__(tag, client, **kwargs)
        self._read_data = self._client.read_input_registers

    def set_data(self, data):
        self.ids.label.text = str(data)


class CardCoil(DataCard):
    def __init__(self, tag: dict, client: ModbusClient, **kwargs):
        super().__init__(tag, client, **kwargs)
        self._read_data = self._client.read_coils
        self._write_data_fcn = self._client.write_single_coil

    def set_data(self, data):
        self.ids.switch.active = data

    def get_data(self):
        return self.ids.switch.active
