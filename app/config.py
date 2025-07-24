import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = os.getenv('APP_NAME', 'Depth Image API')
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///depth_images.db')
    DATA_CSV_PATH: str = os.getenv('DATA_CSV_PATH', 'app/data/data.csv')
    DEFAULT_COLORMAP: str = os.getenv('DEFAULT_COLORMAP', 'magma')
    RESIZED_WIDTH: int = int(os.getenv('RESIZED_WIDTH', 150))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG')
    IMAGE_NAME: str = os.getenv('IMAGE_NAME', 'resized_150_magma')

settings = Settings()
