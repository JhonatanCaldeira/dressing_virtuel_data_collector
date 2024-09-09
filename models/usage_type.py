from sqlalchemy import Integer, String, Column
from . import Base

class UsageType(Base):
    __tablename__ = 'tb_usagetype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))