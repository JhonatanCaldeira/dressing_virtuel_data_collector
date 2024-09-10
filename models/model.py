from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Color(Base):
    __tablename__ = 'tb_colors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class Gender(Base):
    __tablename__ = 'tb_gender'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gender = Column(String(50))

class Season(Base):
    __tablename__ = 'tb_seasons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class UsageType(Base):
    __tablename__ = 'tb_usagetype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class Category(Base):
    __tablename__ = 'tb_productcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class SubCategory(Base):
    __tablename__ = 'tb_productsubcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    id_category = Column(Integer, ForeignKey("tb_productcategories.id"))
    category = relationship("Category")

class ArticleType(Base):
    __tablename__ = 'tb_articletype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    id_subcategory = Column(Integer, ForeignKey("tb_productsubcategories.id"))
    sub_category = relationship("SubCategory")

class ImageProduct(Base):
    __tablename__ = 'tb_imageproduct'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(255))

    id_usagetype = Column(Integer, ForeignKey("tb_usagetype.id"))
    usage_type = relationship("UsageType")

    id_gender = Column(Integer, ForeignKey("tb_gender.id"))
    gender = relationship("Gender")

    id_season = Column(Integer, ForeignKey("tb_seasons.id"))
    season = relationship("Season")

    id_color = Column(Integer, ForeignKey("tb_colors.id"))
    color = relationship("Color")

    id_articletype= Column(Integer, ForeignKey("tb_articletype.id"))
    article_type = relationship("ArticleType")