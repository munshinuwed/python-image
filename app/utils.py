import pandas as pd
import numpy as np
from skimage.transform import resize
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import io
from app.logger_config import logger

from app.config import settings


def generate_image(
    csv_path: str = settings.DATA_CSV_PATH,
    width: int = None,
    depth_min: float = None,
    depth_max: float = None,
    colormap: str = settings.DEFAULT_COLORMAP
) -> bytes:
    """
    Generates an image from CSV data.
    - If width is given, it resizes the image.
    - If depth filters are given, it filters the data before generating the image.
    """
    try:
        df = pd.read_csv(csv_path)
        # Fill invalid values to preserve row count, ensuring depth mapping is accurate
        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

        if depth_min is not None and depth_max is not None:
            df = df[(df['depth'] >= depth_min) & (df['depth'] <= depth_max)]
        
        if df.empty:
            raise ValueError("No data available for the specified depth range.")

        image_data = df.iloc[:, 1:].to_numpy(dtype=np.uint8)

        if width is not None:
            image_data = resize(
                image_data,
                (image_data.shape[0], width),
                order=1,
                anti_aliasing=True,
                preserve_range=True
            ).astype(np.uint8)

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(image_data, aspect='auto', cmap=colormap)
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        
        logger.info("Image generated successfully.")
        return buf.read()
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise
