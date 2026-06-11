from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PersonajeDB(Base):
    __tablename__ = "personajes_master"
    
    id_personaje = Column(Integer, primary_key=True, autoincrement=False)
    
    nombre = Column(String(100), nullable=False)
    estado = Column(String(20))
    especie = Column(String(50))
    genero = Column(String(20))
    tipo = Column(String(100))
    
    origen_nombre = Column(String(100))
    ubicacion_nombre = Column(String(100))
    
    total_episodios = Column(Integer, default=0)
    tiene_tipo_especial = Column(Boolean, default=False)
    
    fecha_extraccion = Column(Date)
    
    @classmethod
    def crear_tabla_si_no_existe(cls, engine):
        """Crea la tabla si no existe (resiliencia)"""
        Base.metadata.create_all(bind=engine)