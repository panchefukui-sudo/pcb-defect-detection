import os
import cv2
import numpy as np
import logging

from . import config

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)


def load_image(image_path, resize_factor=None):
    if resize_factor is None:
        resize_factor = config.RESIZE_FACTOR

    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return None

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        logger.error(f"Failed to load image: {image_path}")
        return None

    if resize_factor != 1.0:
        h, w = image.shape[:2]
        image = cv2.resize(image, (int(w * resize_factor), int(h * resize_factor)))

    return image


def save_image(image, output_path):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    success = cv2.imwrite(output_path, image)
    if not success:
        logger.error(f"Failed to save image: {output_path}")
    return success


def enhance_image(image, contrast=None, brightness=None):
    if contrast is None:
        contrast = config.CONTRAST_FACTOR
    if brightness is None:
        brightness = config.BRIGHTNESS_FACTOR

    img = image.astype(np.float32) / 255.0
    img = img * contrast
    img = img + (brightness / 255.0)
    img = np.clip(img, 0.0, 1.0)
    return (img * 255).astype(np.uint8)


def draw_results(image, defects, draw_boxes=True, draw_labels=True):
    result = image.copy()
    if not defects:
        return result

    for defect in defects:
        x, y, w, h = defect['bbox']
        color = (0, 0, 255)

        if draw_boxes:
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)

        if draw_labels:
            label = f"{defect['type']}: {defect.get('confidence', 0):.2%}"
            cv2.putText(
                result,
                label,
                (x, max(10, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1,
                cv2.LINE_AA,
            )

    return result


def get_image_files(folder_path, extensions=None):
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']

    files = []
    for root, _, names in os.walk(folder_path):
        for name in names:
            ext = os.path.splitext(name)[1].lower()
            if ext in extensions:
                files.append(os.path.join(root, name))
    return sorted(files)


def create_comparison_image(original, result):
    if original.shape[:2] != result.shape[:2]:
        original = cv2.resize(original, (result.shape[1], result.shape[0]))
    combined = np.hstack([original, result])
    return combined
