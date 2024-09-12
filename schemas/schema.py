from pydantic import BaseModel

#Schemas que sao responsaveis por definir o formato de retorno de cada 
#tipo de objeto

class Color(BaseModel):
    id: int|None
    name: str

class Season(BaseModel):
    id: int|None
    name: str

class Gender(BaseModel):
    id: int|None
    gender: str

class UsageType(BaseModel):
    id: int|None
    name: str

class ArticleType(BaseModel):
    id: int|None
    name: str
    id_subcategory: int

    class Config:
        orm_mode = True  

class SubCategory(BaseModel):
    id: int|None
    name: str
    id_category: int
    article_types: list[ArticleType] = []

    class Config:
        orm_mode = True

class Category(BaseModel):
    id: int|None
    name: str
    sub_categories: list[SubCategory] = []

class ImageProduct(BaseModel):
    id: int|None
    path: str
    id_usagetype: int
    id_gender: int
    id_season: int
    id_color: int
    id_articletype: int

    class Config:
        orm_mode = True