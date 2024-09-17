from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Color(Base):
    """
    Model for storing color information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Name of the color.
    """
    __tablename__ = 'tb_colors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class Gender(Base):
    """
    Model for storing gender information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        gender (str): Gender description.
    """
    __tablename__ = 'tb_gender'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gender = Column(String(50))

class Season(Base):
    """
    Model for storing season information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Name of the season.
    """
    __tablename__ = 'tb_seasons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class UsageType(Base):
    """
    Model for storing usage type information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Name of the usage type.
    """
    __tablename__ = 'tb_usagetype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class Category(Base):
    """
    Model for storing product category information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Name of the category.
    """
    __tablename__ = 'tb_productcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class SubCategory(Base):
    """
    Model for storing product subcategory information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Name of the subcategory.
        id_category (int): Foreign key linking to Category.
        category (Category): Relationship to the Category model.
    """
    __tablename__ = 'tb_productsubcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    id_category = Column(Integer, ForeignKey("tb_productcategories.id"))
    category = relationship("Category")

class ArticleType(Base):
    """
    Model for storing article type information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Name of the article type.
        id_subcategory (int): Foreign key linking to SubCategory.
        sub_category (SubCategory): Relationship to the SubCategory model.
    """
    __tablename__ = 'tb_articletype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    id_subcategory = Column(Integer, ForeignKey("tb_productsubcategories.id"))
    sub_category = relationship("SubCategory")

class ImageProduct(Base):
    """
    Model for storing image product information.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        path (str): Path to the image file.
        id_usagetype (int): Foreign key linking to UsageType.
        usage_type (UsageType): Relationship to the UsageType model.
        id_gender (int): Foreign key linking to Gender.
        gender (Gender): Relationship to the Gender model.
        id_season (int): Foreign key linking to Season.
        season (Season): Relationship to the Season model.
        id_color (int): Foreign key linking to Color.
        color (Color): Relationship to the Color model.
        id_articletype (int): Foreign key linking to ArticleType.
        article_type (ArticleType): Relationship to the ArticleType model.
    """
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