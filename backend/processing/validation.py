import numpy as np

def calculate_mse(img1: np.ndarray, img2: np.ndarray) -> float:
    return float(np.mean((img1 - img2) ** 2))

def calculate_rmse(img1: np.ndarray, img2: np.ndarray) -> float:
    return float(np.sqrt(calculate_mse(img1, img2)))

def calculate_psnr(img1: np.ndarray, img2: np.ndarray, max_val: float = 1.0) -> float:
    mse = calculate_mse(img1, img2)
    if mse == 0:
        return float('inf')
    return float(20 * np.log10(max_val) - 10 * np.log10(mse))

def calculate_ssim(img1: np.ndarray, img2: np.ndarray, max_val: float = 1.0) -> float:
    mu1 = np.mean(img1)
    mu2 = np.mean(img2)
    var1 = np.var(img1)
    var2 = np.var(img2)
    cov = np.mean((img1 - mu1) * (img2 - mu2))
    
    k1, k2 = 0.01, 0.03
    c1 = (k1 * max_val) ** 2
    c2 = (k2 * max_val) ** 2
    
    numerator = (2 * mu1 * mu2 + c1) * (2 * cov + c2)
    denominator = (mu1**2 + mu2**2 + c1) * (var1 + var2 + c2)
    
    return float(np.clip(numerator / denominator, -1.0, 1.0))

def calculate_spectral_angle_mapper(img1: np.ndarray, img2: np.ndarray) -> float:
    if len(img1.shape) == 2:
        img1 = np.expand_dims(img1, axis=0)
        img2 = np.expand_dims(img2, axis=0)
        
    bands, h, w = img1.shape
    v1 = img1.reshape(bands, -1).T
    v2 = img2.reshape(bands, -1).T
    
    dot_product = np.sum(v1 * v2, axis=1)
    norm1 = np.linalg.norm(v1, axis=1)
    norm2 = np.linalg.norm(v2, axis=1)
    
    denominator = norm1 * norm2
    denominator[denominator == 0] = 1e-10
    
    cosine_theta = np.clip(dot_product / denominator, -1.0, 1.0)
    return float(np.mean(np.arccos(cosine_theta)))


class ScientificValidator:
    """
    Scientific validation service structured into distinct modules:
    1. Reconstruction Validation (PSNR, SSIM, RMSE)
    2. Spectral Validation (NDVI delta, SAM)
    3. Uncertainty Validation (Confidence metrics, pixel standard deviation)
    """
    def __init__(self, max_value: float = 1.0):
        self.max_val = max_value

    def validate_scene(self, reference_bands: np.ndarray, reconstructed_bands: np.ndarray) -> dict:
        assert reference_bands.shape == reconstructed_bands.shape, "Arrays must have matching shapes."
        
        # 1. Reconstruction Validation
        mse = calculate_mse(reference_bands, reconstructed_bands)
        rmse = calculate_rmse(reference_bands, reconstructed_bands)
        psnr = calculate_psnr(reference_bands, reconstructed_bands, self.max_val)
        ssim = calculate_ssim(reference_bands, reconstructed_bands, self.max_val)
        
        # 2. Spectral Validation
        sam = calculate_spectral_angle_mapper(reference_bands, reconstructed_bands)
        
        # Simulated NDVI band calculations (B4 is NIR - index 3, B3 is Red - index 2)
        # NDVI = (NIR - Red) / (NIR + Red)
        ref_ndvi = (reference_bands[3] - reference_bands[2]) / (reference_bands[3] + reference_bands[2] + 1e-5)
        recon_ndvi = (reconstructed_bands[3] - reconstructed_bands[2]) / (reconstructed_bands[3] + reconstructed_bands[2] + 1e-5)
        mean_ndvi_delta = float(np.mean(np.abs(ref_ndvi - recon_ndvi)))
        
        # 3. Uncertainty Validation
        # Confidence score mapping based on reconstruction deviation
        pixel_deviation = np.abs(reference_bands - reconstructed_bands)
        mean_pixel_reliability = float(1.0 - np.mean(pixel_deviation))
        mean_confidence_score = float(np.clip(mean_pixel_reliability * 100, 0, 100))

        return {
            "reconstruction_validation": {
                "peak_signal_noise_ratio_db": psnr,
                "structural_similarity_index": ssim,
                "root_mean_squared_error": rmse
            },
            "spectral_validation": {
                "spectral_angle_mapper_rad": sam,
                "mean_ndvi_delta": mean_ndvi_delta
            },
            "uncertainty_validation": {
                "mean_confidence_score": mean_confidence_score,
                "pixel_reliability_index": mean_pixel_reliability
            }
        }
