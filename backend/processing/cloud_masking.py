import numpy as np
import cv2
import rasterio

class CloudShadowMasker:
    """
    Classical remote-sensing preprocessing engine to detect clouds and shadows.
    Applies multi-spectral indexing (Green + Red + NIR) + morphological cleaning.
    """
    def __init__(self, cloud_threshold: float = 0.35, shadow_threshold: float = 0.12):
        self.cloud_threshold = cloud_threshold
        self.shadow_threshold = shadow_threshold

    def generate_mask(self, calibrated_tif_path: str, output_mask_path: str) -> bool:
        """
        Reads a 3-band calibrated image (Band 1 = Green, Band 2 = Red, Band 3 = NIR).
        Generates a mask: 0 = Clear, 1 = Cloud Shadow, 2 = Cloud.
        """
        try:
            with rasterio.open(calibrated_tif_path) as src:
                # LISS-IV band mappings: Green (1), Red (2), NIR (3)
                green = src.read(1)
                red = src.read(2)
                nir = src.read(3)
                
                profile = src.profile.copy()
                profile.update(dtype=rasterio.uint8, count=1, nodata=0)

                # 1. Cloud Index (High visible reflectance and flat visible spectrum)
                # True if Green and Red are both above threshold
                cloud_mask = (green > self.cloud_threshold) & (red > self.cloud_threshold)
                
                # 2. Shadow Index (Low NIR reflectance)
                # True if NIR is very dark, but not a raw nodata pixel
                shadow_mask = (nir < self.shadow_threshold) & (nir > 0.005) & (~cloud_mask)

                # Compile output array: 0 for Clear, 1 for Shadow, 2 for Cloud
                mask_result = np.zeros_like(green, dtype=np.uint8)
                mask_result[shadow_mask] = 1
                mask_result[cloud_mask] = 2

                # 3. Morphological cleanup (closing to fill holes, opening to remove noise)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                mask_result = cv2.morphologyEx(mask_result, cv2.MORPH_CLOSE, kernel)
                mask_result = cv2.morphologyEx(mask_result, cv2.MORPH_OPEN, kernel)

                # Write single-band mask to file
                with rasterio.open(output_mask_path, 'w', **profile) as dst:
                    dst.write(mask_result, 1)
            return True
        except Exception as e:
            print(f"Cloud and shadow masking failed for {calibrated_tif_path}: {e}")
            return False
