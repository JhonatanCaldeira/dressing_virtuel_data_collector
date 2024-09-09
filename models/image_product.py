from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from models import article_type, color, gender, season, usage_type
from . import Base

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