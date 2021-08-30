from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class EsteiraPrincipal(Base):
    """
    Dados de monitoramento da esteira principal
    """

    __tablename__ = "esteira_main"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
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
    num_obj_est1 = Column(Integer)
    num_obj_est2 = Column(Integer)
    num_obj_est3 = Column(Integer)
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
    filtro_cor_r1 = Column(Integer)
    filtro_cor_g1 = Column(Integer)
    filtro_cor_b1 = Column(Integer)
    filtro_cor_massa1 = Column(Integer)
    filtro_cor_r2 = Column(Integer)
    filtro_cor_g2 = Column(Integer)
    filtro_cor_b2 = Column(Integer)
    filtro_cor_massa2 = Column(Integer)
    filtro_cor_r3 = Column(Integer)
    filtro_cor_g3 = Column(Integer)
    filtro_cor_b3 = Column(Integer)
    filtro_cor_massa3 = Column(Integer)

    def __repr__(self):
        return "<FiltroConf(id=%s)>" % (self.id)
