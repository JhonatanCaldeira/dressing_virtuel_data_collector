from pydantic import BaseModel

class Color(BaseModel):
    """
    Schema for representing color information.
    
    Attributes:
        id (int | None): The unique identifier for the color. Optional.
        name (str): The name of the color.
    """
    id: int|None
    name: str

class Season(BaseModel):
    """
    Schema for representing season information.
    
    Attributes:
        id (int | None): The unique identifier for the season. Optional.
        name (str): The name of the season.
    """
    id: int|None
    name: str

class Gender(BaseModel):
    """
    Schema for representing gender information.
    
    Attributes:
        id (int | None): The unique identifier for the gender. Optional.
        gender (str): The gender description.
    """
    id: int|None
    gender: str

class UsageType(BaseModel):
    """
    Schema for representing usage type information.
    
    Attributes:
        id (int | None): The unique identifier for the usage type. Optional.
        name (str): The name of the usage type.
    """
    id: int|None
    name: str

class ArticleType(BaseModel):
    """
    Schema for representing article type information.
    
    Attributes:
        id (int | None): The unique identifier for the article type. Optional.
        name (str): The name of the article type.
        id_subcategory (int): The unique identifier for the subcategory related to this article type.
    
    Config:
        orm_mode (bool): Enables compatibility with ORM models.
    """
    id: int|None
    name: str
    id_subcategory: int

    class Config:
        orm_mode = True  

class SubCategory(BaseModel):
    """
    Schema for representing subcategory information.
    
    Attributes:
        id (int | None): The unique identifier for the subcategory. Optional.
        name (str): The name of the subcategory.
        id_category (int): The unique identifier for the category related to this subcategory.
        article_types (list[ArticleType]): List of article types related to this subcategory.
    
    Config:
        orm_mode (bool): Enables compatibility with ORM models.
    """
    id: int|None
    name: str
    id_category: int
    article_types: list[ArticleType] = []

    class Config:
        orm_mode = True

class Category(BaseModel):
    """
    Schema for representing category information.
    
    Attributes:
        id (int | None): The unique identifier for the category. Optional.
        name (str): The name of the category.
        sub_categories (list[SubCategory]): List of subcategories related to this category.
    """
    id: int|None
    name: str
    sub_categories: list[SubCategory] = []

class ImageProduct(BaseModel):
    """
    Schema for representing image product information.
    
    Attributes:
        id (int | None): The unique identifier for the image product. Optional.
        path (str): The file path of the image.
        id_usagetype (int): The unique identifier for the usage type of the image.
        id_gender (int): The unique identifier for the gender associated with the image.
        id_season (int): The unique identifier for the season associated with the image.
        id_color (int): The unique identifier for the color associated with the image.
        id_articletype (int): The unique identifier for the article type of the image.
    
    Config:
        orm_mode (bool): Enables compatibility with ORM models.
    """
    id: int|None
    path: str
    id_usagetype: int
    id_gender: int
    id_season: int
    id_color: int
    id_articletype: int

    class Config:
        orm_mode = True

class ImageProductDetailed(BaseModel):
    """
    Schema for representing detailed image product information.
    
    Attributes:
        id (int): The unique identifier for the image product.
        path (str): The file path of the image.
        gender (str): Gender associated with the image.
        color (str): Color associated with the image.
        season (str): Season associated with the image.
        article (str): Article type associated with the image.
        category (str): Category associated with the image.
        sub_category (str): Subcategory associated with the image.
        usage_type (str): Usage type associated with the image.
    
    Config:
        orm_mode (bool): Enables compatibility with ORM models.
    """
    id: int
    path: str
    gender: str
    color: str
    season: str
    article: str
    category: str
    sub_category: str
    usage_type: str
    class Config:
        orm_mode = True
    
class ImageClassification(BaseModel):
    path: str
    list_of_categories: list[str] = []

class FormClassification(BaseModel):
    dict_of_categories: dict = {}

class ImageSegmentation(BaseModel):
    path: str

class ImageDetection(BaseModel):
    image_path: str
    category_to_detect: str

class CreateClient(BaseModel):
    email: str
    password: str

class CreateClientResp(BaseModel):
    status: int
    message: str

class ClientAuth(BaseModel):
    email: str
    password: str

class ClientAuthResp(BaseModel):
    id: int
    email: str