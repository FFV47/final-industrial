from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EsteiraPrincipal(Base):
    """
    Dados de monitoramento da esteira principal
    """

    __tablename__ = "esteira_main"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    estado_atuador = Column(Boolean)
    bt_on_off = Column(Boolean)
    t_part = Column(Float)
    freq_des = Column(Integer)
    freq_mot = Column(Float)
    tensao = Column(Integer)
    rotacao = Column(Integer)
    pot_entrada = Column(Float)
    corrente = Column(Float)
    temp_estator = Column(Float)
    vel_esteira = Column(Float)
    carga = Column(Float)
    peso_obj = Column(Integer)
    cor_obj_R = Column(Integer)
    cor_obj_G = Column(Integer)
    cor_obj_B = Column(Integer)

    def __repr__(self):
        return "<Principal(id=%s, timestamp=%s)>" % (self.id, self.timestamp)


class EsteiraSecundaria(Base):
    """
    Dados das esteiras secundárias
    """

    __tablename__ = "esteira_sec"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    num_obj_est_1 = Column(Integer)
    num_obj_est_2 = Column(Integer)
    num_obj_est_3 = Column(Integer)
    num_obj_est_nc = Column(Integer)
    filtro_est_1 = Column(Boolean)
    filtro_est_2 = Column(Boolean)
    filtro_est_3 = Column(Boolean)

    def __repr__(self):
        return "<Secundaria(id=%s)>" % (self.id)


class Filtro(Base):
    """
    Configurações dos filtros
    """

    __tablename__ = "filtro_conf"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    cor_r_1 = Column(Integer)
    cor_g_1 = Column(Integer)
    cor_b_1 = Column(Integer)
    massa_1 = Column(Integer)
    cor_r_2 = Column(Integer)
    cor_g_2 = Column(Integer)
    cor_b_2 = Column(Integer)
    massa_2 = Column(Integer)
    cor_r_3 = Column(Integer)
    cor_g_3 = Column(Integer)
    cor_b_3 = Column(Integer)
    massa_3 = Column(Integer)

    def __repr__(self):
        return "<FiltroConf(id=%s)>" % (self.id)
