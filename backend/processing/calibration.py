import numpy as np
import rasterio
from typing import Dict, List

def dn_to_radiance(dn: np.ndarray, gain: float, offset: float) -> np.ndarray:
    """Converts Digital Number (DN) band values to radiance units (W/m2/sr/um)"""
    radiance = dn * gain + offset
    return np.max(0.0, radiance)

def calculate_toa_reflectance(
    radiance: np.ndarray,
    solar_irradiance: float,
    sun_elevation_deg: float,
    earth_sun_distance_au: float
) -> np.ndarray:
    """
    Computes Top of Atmosphere (TOA) Reflectance.
    Formula: TOA = (pi * L * d^2) / (ESUN * sin(theta))
      - L = Radiance
      - d = Earth-Sun distance in astronomical units
      - ESUN = Mean solar exoatmospheric irradiance
      - theta = Sun elevation angle
    """
    sun_elevation_rad = np.radians(sun_elevation_deg)
    solar_zenith_cos = np.sin(sun_elevation_rad)
    
    numerator = np.pi * radiance * (earth_sun_distance_au ** 2)
    denominator = solar_irradiance * solar_zenith_cos
    
    toa_reflectance = numerator / denominator
    # Reflectance must be clipped between 0.0 and 1.0 for physical validity
    return np.clip(toa_reflectance, 0.0, 1.0)


class RadiometricCalibrator:
    """
    SOLID compliant service to calibrate raw LISS-IV scene files.
    Calculates physical reflectance arrays for Green (B2), Red (B3), and NIR (B4) bands.
    """
    def __init__(self, metadata: Dict):
        self.sun_elevation = metadata.get("sun_elevation", 45.0)
        self.earth_sun_dist = metadata.get("earth_sun_distance", 1.0)
        # Standard Resourcesat-2 LISS-IV ESUN values for bands 2, 3, 4
        self.esun_values = {
            2: 1851.3, # Band 2 (Green)
            3: 1583.7, # Band 3 (Red)
            4: 1113.7  # Band 4 (NIR)
        }
        # Gains and Offsets
        self.gains = metadata.get("gains", {2: 0.15, 3: 0.12, 4: 0.08})
        self.offsets = metadata.get("offsets", {2: 0.0, 3: 0.0, 4: 0.0})

    def calibrate_scene(self, input_tif_path: str, output_tif_path: str) -> bool:
        """Reads raw multi-band TIFF, runs conversion, and saves TOA Reflectance stack"""
        try:
            with rasterio.open(input_tif_path) as src:
                profile = src.profile.copy()
                # Update output data type to Float32 to support decimal reflectance values
                profile.update(dtype=rasterio.float32, nodata=0.0)
                
                num_bands = src.count
                
                with rasterio.open(output_tif_path, 'w', **profile) as dst:
                    for b in range(1, num_bands + 1):
                        dn_data = src.read(b).astype(np.float32)
                        
                        # Get calibration factors corresponding to current band index
                        gain = self.gains.get(b, 1.0)
                        offset = self.offsets.get(b, 0.0)
                        esun = self.esun_values.get(b, 1000.0)
                        
                        # 1. DN to Radiance
                        radiance = dn_data * gain + offset
                        
                        # 2. Radiance to TOA Reflectance
                        toa = calculate_toa_reflectance(
                            radiance=radiance,
                            solar_irradiance=esun,
                            sun_elevation_deg=self.sun_elevation,
                            earth_sun_distance_au=self.earth_sun_dist
                        )
                        
                        # Preserve nodata areas (raw pixel 0 stays 0)
                        toa[dn_data == 0] = 0.0
                        
                        dst.write(toa, b)
            return True
        except Exception as e:
            print(f"Calibration failed for scene {input_tif_path}: {e}")
            return False
