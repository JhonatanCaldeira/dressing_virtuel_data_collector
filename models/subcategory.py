from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from models.category import Category
from . import Base


class SubCategory(Base):
    __tablename__ = 'tb_productsubcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    id_category = Column(Integer, ForeignKey("tb_productcategories.id"))
    category = relationship("Category")
