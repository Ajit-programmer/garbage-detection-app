"""
YOLO Model Training Script for Waste Detection
Train YOLOv8 on custom waste dataset
"""

from ultralytics import YOLO
import torch
import os

def train_model():
    """
    Train YOLOv8 model on custom waste dataset
    
    Make sure:
    1. Dataset is properly organized in dataset/ folder
    2. data.yaml is configured correctly
    3. Images and labels are in correct format
    """
    
    print("="*70)
    print("🚀 YOLO Waste Detection - Model Training")
    print("="*70)
    
    # Check if CUDA is available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n📍 Device: {device}")
    if device == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("   ⚠️  No GPU detected. Training will be slower on CPU.")
    
    # Check if data.yaml exists
    if not os.path.exists('data.yaml'):
        print("\n❌ ERROR: data.yaml not found!")
        print("   Please create data.yaml with your dataset configuration.")
        return None
    
    print("\n📂 Loading dataset configuration from data.yaml")
    
    # Select model size
    # Options: yolov8n.pt (nano), yolov8s.pt (small), yolov8m.pt (medium), 
    #          yolov8l.pt (large), yolov8x.pt (xlarge)
    model_size = 'yolov8n.pt'  # Change this for different model sizes
    
    print(f"\n🤖 Loading pretrained model: {model_size}")
    model = YOLO(model_size)
    
    print(f"\n🎓 Starting training...")
    print(f"   This may take 1-4 hours depending on dataset size and hardware\n")
    
    # Training configuration
    results = model.train(
        # Dataset
        data='data.yaml',              # Path to dataset config file
        
        # Training duration
        epochs=100,                    # Number of epochs (increase for better results)
        patience=20,                   # Early stopping patience
        
        # Image settings
        imgsz=640,                     # Input image size
        
        # Batch settings
        batch=16,                      # Batch size (reduce if out of memory)
        
        # Hardware
        device=device,                 # cuda or cpu
        workers=4,                     # Number of worker threads
        
        # Saving
        save=True,                     # Save checkpoints
        save_period=10,                # Save every N epochs
        project='runs/detect',         # Project directory
        name='waste_detection',        # Experiment name
        exist_ok=True,                 # Overwrite existing project
        
        # Pretrained weights
        pretrained=True,               # Use pretrained weights
        
        # Optimizer
        optimizer='Adam',              # Optimizer (Adam, SGD, AdamW)
        lr0=0.01,                      # Initial learning rate
        lrf=0.01,                      # Final learning rate
        momentum=0.937,                # Momentum
        weight_decay=0.0005,           # Weight decay
        
        # Warmup
        warmup_epochs=3.0,             # Warmup epochs
        warmup_momentum=0.8,           # Warmup momentum
        warmup_bias_lr=0.1,            # Warmup bias learning rate
        
        # Loss weights
        box=7.5,                       # Box loss gain
        cls=0.5,                       # Class loss gain
        dfl=1.5,                       # DFL loss gain
        
        # Augmentation
        hsv_h=0.015,                   # Hue augmentation
        hsv_s=0.7,                     # Saturation augmentation
        hsv_v=0.4,                     # Value augmentation
        degrees=0.0,                   # Rotation augmentation
        translate=0.1,                 # Translation augmentation
        scale=0.5,                     # Scale augmentation
        shear=0.0,                     # Shear augmentation
        perspective=0.0,               # Perspective augmentation
        flipud=0.0,                    # Vertical flip probability
        fliplr=0.5,                    # Horizontal flip probability
        mosaic=1.0,                    # Mosaic augmentation probability
        mixup=0.0,                     # Mixup augmentation probability
        
        # Validation
        val=True,                      # Validate during training
        plots=True,                    # Save plots
        
        # Output
        verbose=True,                  # Verbose output
    )
    
    print("\n" + "="*70)
    print("✅ Training completed!")
    print("="*70)
    
    # Evaluate on validation set
    print("\n📊 Evaluating model on validation set...")
    metrics = model.val()
    
    # Display results
    print("\n📈 Training Results:")
    print(f"   mAP50:     {metrics.box.map50:.4f}")
    print(f"   mAP50-95:  {metrics.box.map:.4f}")
    print(f"   Precision: {metrics.box.mp:.4f}")
    print(f"   Recall:    {metrics.box.mr:.4f}")
    
    # Best model path
    best_model_path = 'runs/detect/waste_detection/weights/best.pt'
    print(f"\n💾 Best model saved at: {best_model_path}")
    print(f"   Copy this to models/best.pt to use in the web application")
    
    print("\n📝 Next steps:")
    print(f"   1. Copy best model: cp {best_model_path} models/best.pt")
    print(f"   2. Run the web app: python app.py")
    print(f"   3. Open browser: http://localhost:5000")
    
    print("\n" + "="*70)
    
    return model


def export_model(model_path='runs/detect/waste_detection/weights/best.pt'):
    """
    Export trained model to different formats
    
    Args:
        model_path: Path to the trained model
    """
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        return
    
    print(f"\n📦 Exporting model from {model_path}")
    model = YOLO(model_path)
    
    # Export to ONNX (for deployment)
    print("   Exporting to ONNX...")
    model.export(format='onnx')
    
    # Export to TorchScript (for PyTorch deployment)
    print("   Exporting to TorchScript...")
    model.export(format='torchscript')
    
    print("✅ Export complete!")


if __name__ == "__main__":
    # Train the model
    trained_model = train_model()
    
    # Optional: Export to other formats
    # Uncomment the following line to export after training
    # export_model()
    
    print("\n🎉 All done! Happy detecting! 🗑️♻️\n")