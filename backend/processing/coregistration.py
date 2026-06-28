import numpy as np
import cv2
import rasterio
from rasterio.warp import reproject, Resampling

class ImageCoRegisterer:
    """
    Sub-pixel alignment service to co-register target and reference scenes.
    Uses ORB/SIFT keypoint extraction + Homography warping to align structures.
    In production, this queries the LoFTR GNN feature matcher.
    """
    def __init__(self, n_features: int = 2000):
        self.n_features = n_features
        self.sift = cv2.SIFT_create(nfeatures=self.n_features)

    def register_images(self, reference_path: str, target_path: str, aligned_output_path: str) -> bool:
        """
        Warps the target image to match the spatial coordinates of the reference image.
        Uses keypoint tracking on the red band (Band 2 / Channel 1) for strong structural edges.
        """
        try:
            with rasterio.open(reference_path) as ref_src, rasterio.open(target_path) as tar_src:
                ref_profile = ref_src.profile.copy()
                
                # 1. Read first band for keypoint matching (cast to Uint8)
                ref_band = ref_src.read(1)
                tar_band = tar_src.read(1)
                
                # Normalize to 0-255 range for OpenCV
                ref_norm = cv2.normalize(ref_band, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                tar_norm = cv2.normalize(tar_band, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

                # 2. Extract keypoints and descriptors
                kp_ref, desc_ref = self.sift.detectAndCompute(ref_norm, None)
                kp_tar, desc_tar = self.sift.detectAndCompute(tar_norm, None)

                if desc_ref is None or desc_tar is None:
                    raise ValueError("Keypoint descriptors could not be generated.")

                # 3. Flann matcher
                index_params = dict(algorithm=1, trees=5)
                search_params = dict(checks=50)
                flann = cv2.FlannBasedMatcher(index_params, search_params)
                matches = flann.knnMatch(desc_ref, desc_tar, k=2)

                # Ratio test
                good_matches = []
                for m, n in matches:
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)

                if len(good_matches) < 10:
                    raise ValueError("Insufficient feature matches between scenes (< 10 matches).")

                # 4. Compute Homography matrix via RANSAC
                pts_ref = np.float32([kp_ref[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                pts_tar = np.float32([kp_tar[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                
                H, mask = cv2.findHomography(pts_tar, pts_ref, cv2.RANSAC, 5.0)

                # 5. Warp target bands using homography to match reference dimensions
                tar_bands = tar_src.read()
                num_bands, height, width = tar_bands.shape
                aligned_bands = np.zeros((num_bands, ref_src.height, ref_src.width), dtype=ref_src.dtypes[0])

                for b in range(num_bands):
                    aligned_bands[b] = cv2.warpPerspective(
                        tar_bands[b], 
                        H, 
                        (ref_src.width, ref_src.height),
                        flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT,
                        borderValue=0
                    )

                # 6. Save aligned GeoTIFF matching reference geospatial footprint
                with rasterio.open(aligned_output_path, 'w', **ref_profile) as dst:
                    dst.write(aligned_bands)

            return True
        except Exception as e:
            print(f"Homography Co-Registration failed: {e}")
            # Fallback: Reproject target image geometrically using metadata if CV fails
            return self._fallback_metadata_align(reference_path, target_path, aligned_output_path)

    def _fallback_metadata_align(self, reference_path: str, target_path: str, output_path: str) -> bool:
        """Fallback: Geospatial projection matching via metadata if feature warping fails"""
        try:
            with rasterio.open(reference_path) as ref_src, rasterio.open(target_path) as tar_src:
                profile = ref_src.profile.copy()
                
                with rasterio.open(output_path, 'w', **profile) as dst:
                    for b in range(1, tar_src.count + 1):
                        reproject(
                            source=rasterio.band(tar_src, b),
                            destination=rasterio.band(dst, b),
                            src_transform=tar_src.transform,
                            src_crs=tar_src.crs,
                            dst_transform=ref_src.transform,
                            dst_crs=ref_src.crs,
                            resampling=Resampling.bilinear
                        )
            return True
        except Exception as e:
            print(f"Fallback geometric reprojection failed: {e}")
            return False
