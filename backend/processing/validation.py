import numpy as np

def calculate_mse(img1: np.ndarray, img2: np.ndarray) -> float:
    """Computes Mean Squared Error between two raster arrays"""
    return float(np.mean((img1 - img2) ** 2))

def calculate_rmse(img1: np.ndarray, img2: np.ndarray) -> float:
    """Computes Root Mean Squared Error between two raster arrays"""
    return float(np.sqrt(calculate_mse(img1, img2)))

def calculate_psnr(img1: np.ndarray, img2: np.ndarray, max_val: float = 1.0) -> float:
    """
    Computes Peak Signal-to-Noise Ratio (PSNR).
    Formula: PSNR = 10 * log10(MAX^2 / MSE)
    """
    mse = calculate_mse(img1, img2)
    if mse == 0:
        return float('inf')
    return float(20 * np.log10(max_val) - 10 * np.log10(mse))

def calculate_ssim(img1: np.ndarray, img2: np.ndarray, max_val: float = 1.0) -> float:
    """
    Simplified Structural Similarity Index (SSIM) for raster validation.
    Computes luminance, contrast, and structural comparison components.
    """
    # Mean
    mu1 = np.mean(img1)
    mu2 = np.mean(img2)
    
    # Variance & Covariance
    var1 = np.var(img1)
    var2 = np.var(img2)
    cov = np.mean((img1 - mu1) * (img2 - mu2))
    
    # Constants for stability
    k1 = 0.01
    k2 = 0.03
    c1 = (k1 * max_val) ** 2
    c2 = (k2 * max_val) ** 2
    
    numerator = (2 * mu1 * mu2 + c1) * (2 * cov + c2)
    denominator = (mu1**2 + mu2**2 + c1) * (var1 + var2 + c2)
    
    ssim_val = numerator / denominator
    return float(np.clip(ssim_val, -1.0, 1.0))

def calculate_spectral_angle_mapper(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Computes Spectral Angle Mapper (SAM) in radians.
    Determines spectral similarity between target and reconstructed bands.
    Formula: theta = arccos( (A . B) / (||A|| * ||B||) )
    """
    # Reshape arrays to [pixels, bands]
    # Expecting inputs of size [Bands, Height, Width]
    if len(img1.shape) == 2:
        img1 = np.expand_dims(img1, axis=0)
        img2 = np.expand_dims(img2, axis=0)
        
    bands, h, w = img1.shape
    v1 = img1.reshape(bands, -1).T
    v2 = img2.reshape(bands, -1).T
    
    dot_product = np.sum(v1 * v2, axis=1)
    norm1 = np.linalg.norm(v1, axis=1)
    norm2 = np.linalg.norm(v2, axis=1)
    
    # Avoid zero division
    denominator = norm1 * norm2
    denominator[denominator == 0] = 1e-10
    
    cosine_theta = dot_product / denominator
    cosine_theta = np.clip(cosine_theta, -1.0, 1.0)
    
    theta = np.arccos(cosine_theta)
    # Return mean spectral angle across all pixel vectors
    return float(np.mean(theta))


class ScientificValidator:
    """
    SOLID service wrapper executing spectral and spatial validation checks
    on the AI reconstructed multi-spectral satellite imagery.
    """
    def __init__(self, max_value: float = 1.0):
        self.max_val = max_value

    def validate_scene(self, reference_bands: np.ndarray, reconstructed_bands: np.ndarray) -> dict:
        """Executes full suite of scientific quality verification metrics"""
        # Ensure identical dimensions
        assert reference_bands.shape == reconstructed_bands.shape, "Bands must have matching dimensions for validation."
        
        mse = calculate_mse(reference_bands, reconstructed_bands)
        rmse = calculate_rmse(reference_bands, reconstructed_bands)
        psnr = calculate_psnr(reference_bands, reconstructed_bands, self.max_val)
        ssim = calculate_ssim(reference_bands, reconstructed_bands, self.max_val)
        sam = calculate_spectral_angle_mapper(reference_bands, reconstructed_bands)
        
        # Spectral consistency check
        # High deviation (>0.1 rad in SAM or SSIM < 0.8) flags warnings
        valid_consistency = (sam < 0.08) and (ssim > 0.85)
        
        return {
            "mean_squared_error": mse,
            "root_mean_squared_error": rmse,
            "peak_signal_noise_ratio_db": psnr,
            "structural_similarity_index": ssim,
            "spectral_angle_mapper_rad": sam,
            "spectral_consistency_check": "PASSED" if valid_consistency else "WARNING_DEVIATION"
        }
