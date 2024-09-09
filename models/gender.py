from sqlalchemy import Integer, String, Column
from . import Base

class Gender(Base):
    __tablename__ = 'tb_gender'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gender = Column(String(50))