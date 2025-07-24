from fastapi import FastAPI, Query, Response, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import os
from app.config import settings
from app.logger_config import logger
from app.utils import generate_image
from app.db import get_engine, create_tables, get_session, save_image, get_image_by_description

# Initialize logging directly in this file


# --- Database and App Setup ---
engine = get_engine()
SessionLocal = get_session(engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed.")

@app.on_event("startup")
def startup_event():
    create_tables(engine)
    db = SessionLocal()
    description = f"resized_{settings.RESIZED_WIDTH}"
    if not get_image_by_description(db, description):
        logger.info(f"Generating and storing resized image (width={settings.RESIZED_WIDTH}).")
        try:
            img_bytes = generate_image(csv_path= settings.DATA_CSV_PATH, width=settings.RESIZED_WIDTH)
            save_image(db, description, img_bytes)
        except Exception as e:
            logger.critical(f"FATAL: Could not create and store initial image on startup: {e}")
    db.close()

# === Endpoints for Direct Image Viewing ===

@app.get("/original-image")
def get_original_image():
    try:
        img_bytes = generate_image()
        return Response(content=img_bytes, media_type="image/png")
    except Exception as e:
        logger.error(f"Failed to generate original image: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/resized-image")
def get_resized_image(db: Session = Depends(get_db)):
    description = f"resized_{settings.RESIZED_WIDTH}"
    record = get_image_by_description(db, description)
    if not record:
        raise HTTPException(status_code=404, detail="Resized image not found in DB.")
    return Response(content=record.image_blob, media_type="image/png")

@app.get("/depth-range-image")
def get_depth_range_image(
    depth_min: float = Query(..., description="Minimum depth value"),
    depth_max: float = Query(..., description="Maximum depth value"),
):
    try:
        img_bytes = generate_image(depth_min=depth_min, depth_max=depth_max)
        return Response(content=img_bytes, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate depth-range image: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# === Endpoints for Prompting Image Downloads ===

@app.get("/download-original")
def download_original_image():
    try:
        img_bytes = generate_image()
        headers = {'Content-Disposition': 'attachment; filename="original_image.png"'}
        return Response(content=img_bytes, media_type="image/png", headers=headers)
    except Exception as e:
        logger.error(f"Failed to generate original image for download: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/download-resized")
def download_resized_image(db: Session = Depends(get_db)):
    description = f"resized_{settings.RESIZED_WIDTH}"
    record = get_image_by_description(db, description)
    if not record:
        raise HTTPException(status_code=404, detail="Resized image not found in DB.")
    headers = {'Content-Disposition': f'attachment; filename="resized_image_w{settings.RESIZED_WIDTH}.png"'}
    return Response(content=record.image_blob, media_type="image/png", headers=headers)

@app.get("/download-depth-range")
def download_depth_range_image(
    depth_min: float = Query(..., description="Minimum depth value"),
    depth_max: float = Query(..., description="Maximum depth value"),
):
    try:
        img_bytes = generate_image(depth_min=depth_min, depth_max=depth_max)
        filename = f"depth_range_{depth_min}_to_{depth_max}.png"
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
        return Response(content=img_bytes, media_type="image/png", headers=headers)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate depth-range image for download: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
