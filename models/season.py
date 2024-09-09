from sqlalchemy import Integer, String, Column
from . import Base

class Season(Base):
    __tablename__ = 'tb_seasons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))