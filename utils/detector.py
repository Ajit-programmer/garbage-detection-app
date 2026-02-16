"""
Waste Detection Utility Module
Handles YOLO model loading and inference for waste detection
"""

from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import os

class WasteDetector:
    """
    Wrapper class for YOLO-based waste detection
    Provides methods for image and video frame detection
    """
    
    def __init__(self, model_path='models/best.pt'):
        """
        Initialize the detector with a trained YOLO model
        
        Args:
            model_path (str): Path to the trained YOLO model (.pt file)
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model fails to load
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        try:
            self.model = YOLO(model_path)
            self.class_names = self.model.names
            print(f"Model loaded from {model_path}")
            print(f"Classes: {self.class_names}")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
        
        # Define colors for each waste category (BGR format for OpenCV)
        self.colors = {
            'plastic': (0, 255, 255),      # Yellow
            'paper': (255, 255, 255),      # White
            'metal': (192, 192, 192),      # Silver/Gray
            'glass': (255, 0, 255),        # Magenta
            'organic': (0, 255, 0),        # Green
            'cardboard': (19, 69, 139),    # Brown
        }
        
        # Default color for unknown classes
        self.default_color = (0, 255, 0)  # Green
    
    def detect_image(self, image_path, conf_threshold=0.25):
        """
        Perform detection on a single image file
        
        Args:
            image_path (str): Path to the input image
            conf_threshold (float): Confidence threshold (0.0 to 1.0)
            
        Returns:
            tuple: (annotated_image, detections_list)
                - annotated_image: numpy array with drawn bounding boxes
                - detections_list: list of detection dictionaries
                
        Raises:
            ValueError: If image cannot be read
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image at {image_path}")
        
        # Run inference
        results = self.model.predict(
            source=image,
            conf=conf_threshold,
            save=False,
            verbose=False
        )
        
        # Process results
        detections = []
        annotated_image = image.copy()
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Get class and confidence
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.class_names[cls]
                
                # Get color for this class
                color = self.colors.get(class_name.lower(), self.default_color)
                
                # Draw bounding box
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
                
                # Prepare label
                label = f"{class_name}: {conf:.2f}"
                
                # Get label size
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    2
                )
                
                # Draw label background
                cv2.rectangle(
                    annotated_image,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width + 10, y1),
                    color,
                    -1  # Filled rectangle
                )
                
                # Draw label text
                cv2.putText(
                    annotated_image,
                    label,
                    (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),  # Black text
                    2
                )
                
                # Store detection info
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 4),
                    'bbox': [x1, y1, x2, y2]
                })
        
        return annotated_image, detections
    
    def detect_frame(self, frame, conf_threshold=0.25):
        """
        Perform detection on a video frame (for live camera)
        
        Args:
            frame (numpy.ndarray): Input frame from camera (BGR format)
            conf_threshold (float): Confidence threshold (0.0 to 1.0)
            
        Returns:
            tuple: (annotated_frame, detections_list)
                - annotated_frame: numpy array with drawn bounding boxes
                - detections_list: list of detection dictionaries
        """
        # Run inference
        results = self.model.predict(
            source=frame,
            conf=conf_threshold,
            save=False,
            verbose=False
        )
        
        # Process results
        detections = []
        annotated_frame = frame.copy()
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Get class and confidence
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.class_names[cls]
                
                # Get color for this class
                color = self.colors.get(class_name.lower(), self.default_color)
                
                # Draw bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Prepare label
                label = f"{class_name}: {conf:.2f}"
                
                # Get label size
                (label_width, label_height), baseline = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    2
                )
                
                # Draw label background
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width + 10, y1),
                    color,
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    2
                )
                
                # Store detection info
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 4),
                    'bbox': [x1, y1, x2, y2]
                })
        
        return annotated_frame, detections
    
    def get_statistics(self, detections):
        """
        Calculate statistics from detections
        
        Args:
            detections (list): List of detection dictionaries
            
        Returns:
            dict: Statistics including total count and per-category counts
        """
        stats = {
            'total_items': len(detections),
            'categories': {}
        }
        
        for detection in detections:
            class_name = detection['class']
            if class_name not in stats['categories']:
                stats['categories'][class_name] = 0
            stats['categories'][class_name] += 1
        
        return stats
    
    def update_confidence_threshold(self, new_threshold):
        """
        Update the confidence threshold for detections
        
        Args:
            new_threshold (float): New confidence threshold (0.0 to 1.0)
        """
        if 0.0 <= new_threshold <= 1.0:
            self.conf_threshold = new_threshold
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")