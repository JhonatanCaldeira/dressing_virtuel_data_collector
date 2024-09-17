# Dressing Virtuel

Dressing Virtuel is a comprehensive solution for managing and evaluating fashion product images. The architecture includes several components, such as an API server, a CLIP model for image evaluation, an image scraper, and a Django application for managing and displaying images.

## Components

### 1. API Server (`api` folder)
A FastAPI-based server providing endpoints for managing fashion product attributes, including colors, seasons, genders, and more.

### 2. CLIP Model (`clip_model` folder)
Scripts for evaluating product images using a CLIP model. This model processes images and text descriptions to identify the most likely categories for each image.

### 3. Database Configuration (`database` folder)
SQLAlchemy models and CRUD operations for interacting with a PostgreSQL database. Configuration is managed via a YAML file.

### 4. Image Gallery (`image_gallery` folder)
A Django application that serves as a web interface for managing and displaying images. Includes models, views, and templates.

### 5. Image Scraper (`image_scraper` folder)
A Scrapy spider that scrapes images from a webpage, downloads them, and stores metadata in a SQLite database.

### 6. Utilities (`app.py`, `import_images.py`, `manage.py`)
Various utility scripts for managing and executing different parts of the project.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/dressing_virtuel.git
   cd dressing_virtuel
    ```

2. **Install dependencies:**

- Create and activate a virtual environment.
- Install Python dependencies:

```
bash
pip install -r requirements.txt
```

3. **Set up the database:**

- Ensure PostgreSQL is running and accessible.
- Update config/config.yaml with your database credentials.
- Run migrations if necessary (for Django).

4. **Run the API Server:**
```
bash
uvicorn api.api_server:app --reload
```

5. **Run the Django Application:**
```
bash
python image_gallery/manage.py runserver
```

6. **Run the Image Scraper:**
```
bash
cd image_scraper
scrapy crawl images
```

7. **Evaluate Images with CLIP:**
```
bash
python clip_model/product_evaluation.py
```

## Configuration
- API Server Configuration: Modify config/config.yaml to update database settings and other configurations.
- Django Settings: Adjust image_gallery/settings.py for Django-specific settings.
- Scrapy Settings: Customize image_scraper/settings.py as needed.

## Usage
- API Endpoints: Access the API at http://localhost:8000 for CRUD operations on fashion attributes.
- Image Gallery: Visit http://localhost:8000/image_gallery/ to view and manage images.
- Image Scraping: Use the Scrapy spider to scrape new images.
- Image Evaluation: Run the CLIP model to evaluate images and update the database with predictions.

## License
This project is licensed under the MIT License - see the LICENSE file for details.