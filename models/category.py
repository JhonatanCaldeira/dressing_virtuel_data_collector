from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship

from . import Base

class Category(Base):
    __tablename__ = 'tb_productcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
