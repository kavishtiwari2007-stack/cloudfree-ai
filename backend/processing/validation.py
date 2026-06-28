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

def calculate_iou(mask1: np.ndarray, mask2: np.ndarray) -> float:
    """Calculates Intersection over Union (IoU) for binary arrays"""
    intersection = np.logical_and(mask1, mask2)
    union = np.logical_or(mask1, mask2)
    union_sum = np.sum(union)
    if union_sum == 0:
        return 1.0
    return float(np.sum(intersection) / union_sum)

def calculate_boundary_accuracy(img1: np.ndarray, img2: np.ndarray) -> float:
    """Computes alignment of structural edge boundary maps using simple Sobel gradients"""
    # Simple spatial difference to extract edges
    diff1_x = np.abs(img1[:, :-1, :-1] - img1[:, :-1, 1:])
    diff2_x = np.abs(img2[:, :-1, :-1] - img2[:, :-1, 1:])
    
    # Threshold gradients to create boundary maps
    edge1 = diff1_x > 0.1
    edge2 = diff2_x > 0.1
    
    # Calculate IoU of structural boundaries
    return calculate_iou(edge1, edge2)


class ScientificValidator:
    """
    Scientific Quality Assurance (QA) Validation Service.
    Divided into three operational checks:
    1. Image Quality (PSNR, SSIM, RMSE)
    2. Spectral Integrity (SAM, NDVI Delta)
    3. Geometric Consistency (IoU, Boundary Accuracy)
    """
    def __init__(self, max_value: float = 1.0):
        self.max_val = max_value

    def validate_scene(self, reference_bands: np.ndarray, reconstructed_bands: np.ndarray) -> dict:
        assert reference_bands.shape == reconstructed_bands.shape, "Arrays must have matching shapes."
        
        # 1. Image Quality
        mse = calculate_mse(reference_bands, reconstructed_bands)
        rmse = calculate_rmse(reference_bands, reconstructed_bands)
        psnr = calculate_psnr(reference_bands, reconstructed_bands, self.max_val)
        ssim = calculate_ssim(reference_bands, reconstructed_bands, self.max_val)
        
        # 2. Spectral Integrity
        sam = calculate_spectral_angle_mapper(reference_bands, reconstructed_bands)
        ref_ndvi = (reference_bands[3] - reference_bands[2]) / (reference_bands[3] + reference_bands[2] + 1e-5)
        recon_ndvi = (reconstructed_bands[3] - reconstructed_bands[2]) / (reconstructed_bands[3] + reconstructed_bands[2] + 1e-5)
        mean_ndvi_delta = float(np.mean(np.abs(ref_ndvi - recon_ndvi)))
        
        # 3. Geometric Consistency
        # Create mock binary segmentations via thresholding
        ref_mask = reference_bands[0] > 0.4
        recon_mask = reconstructed_bands[0] > 0.4
        iou = calculate_iou(ref_mask, recon_mask)
        boundary_acc = calculate_boundary_accuracy(reference_bands, reconstructed_bands)

        return {
            "image_quality": {
                "peak_signal_noise_ratio_db": psnr,
                "structural_similarity_index": ssim,
                "root_mean_squared_error": rmse
            },
            "spectral_integrity": {
                "spectral_angle_mapper_rad": sam,
                "mean_ndvi_delta": mean_ndvi_delta
            },
            "geometric_consistency": {
                "intersection_over_union": iou,
                "boundary_accuracy_index": boundary_acc
            }
        }
