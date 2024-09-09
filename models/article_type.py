from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from models.subcategory import SubCategory 

from . import Base

class ArticleType(Base):
    __tablename__ = 'tb_articletype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    id_subcategory = Column(Integer, ForeignKey("tb_productsubcategories.id"))
    sub_category = relationship("SubCategory")
