from sqlalchemy import Integer, String, Column
from . import Base

class Color(Base):
    __tablename__ = 'tb_colors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))