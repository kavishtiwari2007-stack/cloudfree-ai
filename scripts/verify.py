import sys
import os

# Set root dir path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_imports():
    print("------------------------------------------")
    print("Initiating CloudFreeAI Codebase Verification...")
    print("------------------------------------------")
    
    modules = [
        ("models.unet_cloudnet", ["UNet", "CloudNet"]),
        ("models.temporal_transformer", ["TemporalFusionTransformer"]),
        ("models.pix2pix_diffusion", ["DSen2CRReconstructor", "PatchGANDiscriminator"]),
        ("models.deeplab_segformer", ["DeepLabV3Plus", "SegFormerFloodNet"]),
        ("models.siamese_transformer", ["SiameseViTChangeDetector"]),
        ("processing.calibration", ["RadiometricCalibrator"]),
        ("processing.cloud_masking", ["CloudShadowMasker"]),
        ("processing.coregistration", ["ImageCoRegisterer"]),
        ("processing.validation", ["ScientificValidator"]),
        ("config", ["settings"]),
        ("services.db", ["verify_postgis_support"]),
        ("services.gemini", ["GeminiReportGenerator"])
    ]
    
    success = True
    for module_name, classes in modules:
        try:
            print(f"Importing {module_name}...", end=" ")
            mod = __import__(module_name, fromlist=classes)
            for cls in classes:
                assert hasattr(mod, cls), f"Class {cls} not found in {module_name}"
            print("OK")
        except Exception as e:
            print("FAILED")
            print(f"Error: {e}")
            success = False

    print("------------------------------------------")
    if success:
        print("SUCCESS: All models, processing modules, and dependencies are structurally valid.")
        sys.exit(0)
    else:
        print("ERROR: One or more import verification checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    verify_imports()
