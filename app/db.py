from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.logger_config import logger

from app.config import settings

Base = declarative_base()

class StoredImage(Base):
    __tablename__ = "stored_image_aiq"
    id = Column(Integer, primary_key=True)
    description = Column(String, index=True)
    image_blob = Column(LargeBinary)

def get_engine():
    return create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

def create_tables(engine):
    Base.metadata.create_all(engine, checkfirst=True)
    logger.info("Database tables verified/created successfully.")

def get_session(engine):
    return sessionmaker(autocommit=False, autoflush=True, bind=engine)

def save_image(db: Session, description: str, image_bytes: bytes):
    try:
        db_image = StoredImage(description=description, image_blob=image_bytes)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        logger.info(f"Image '{description}' saved to database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save image '{description}': {e}")
        raise

def get_image_by_description(db: Session, description: str):
    return db.query(StoredImage).filter(StoredImage.description == description).first()
