"""
YOLO-Based Waste Detection Flask Application
Main application file with all routes and API endpoints
"""

from flask import Flask, render_template, request, jsonify, Response
import cv2
import os
import base64
import numpy as np
from werkzeug.utils import secure_filename
from utils.detector import WasteDetector
import time

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize detector - Global variable
detector = None

def init_detector():
    """Initialize the YOLO detector"""
    global detector
    try:
        detector = WasteDetector('models/best.pt')
        print("✓ Model loaded successfully!")
        return True
    except FileNotFoundError:
        print("✗ Model not found at models/best.pt")
        print("  Please train a model or place your trained model at models/best.pt")
        return False
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False

# Try to load model at startup
init_detector()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Homepage route"""
    return render_template('index.html')


@app.route('/upload')
def upload_page():
    """Upload page route"""
    return render_template('upload.html')


@app.route('/camera')
def camera_page():
    """Camera page route"""
    return render_template('camera.html')


@app.route('/detect', methods=['POST'])
def detect():
    """
    Handle image upload and detection
    
    Request: multipart/form-data with 'file' field
    Response: JSON with detection results
    """
    # Check if model is loaded
    if detector is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please check if models/best.pt exists.'
        }), 500
    
    # Validate request
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file uploaded'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save uploaded file with timestamp
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time() * 1000))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get confidence threshold from request (optional)
        conf_threshold = float(request.form.get('confidence', 0.25))
        
        # Perform detection
        annotated_image, detections = detector.detect_image(filepath, conf_threshold)
        
        # Save annotated image
        output_filename = f"detected_{filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        cv2.imwrite(output_path, annotated_image)
        
        # Get statistics
        stats = detector.get_statistics(detections)
        
        # Prepare response
        response = {
            'success': True,
            'original_image': f'/{app.config["UPLOAD_FOLDER"]}/{filename}',
            'detected_image': f'/{app.config["UPLOAD_FOLDER"]}/{output_filename}',
            'detections': detections,
            'statistics': stats,
            'confidence_threshold': conf_threshold
        }
        
        return jsonify(response)
    
    except Exception as e:
        # Clean up files if they exist
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': f'Detection failed: {str(e)}'
        }), 500


@app.route('/detect_frame', methods=['POST'])
def detect_frame():
    """
    Handle frame detection from camera
    
    Request: JSON with base64 encoded image
    Response: JSON with detection results and annotated base64 image
    """
    # Check if model is loaded
    if detector is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please check if models/best.pt exists.'
        }), 500
    
    try:
        # Get image data from request
        data = request.json
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400
        
        # Remove data URL prefix if present
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Get confidence threshold (optional)
        conf_threshold = float(data.get('confidence', 0.25))
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({
                'success': False,
                'error': 'Failed to decode image'
            }), 400
        
        # Perform detection
        annotated_frame, detections = detector.detect_frame(frame, conf_threshold)
        
        # Encode annotated frame to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Get statistics
        stats = detector.get_statistics(detections)
        
        # Prepare response
        response = {
            'success': True,
            'annotated_image': f'data:image/jpeg;base64,{annotated_base64}',
            'detections': detections,
            'statistics': stats,
            'confidence_threshold': conf_threshold
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Frame detection failed: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector is not None,
        'model_path': 'models/best.pt',
        'upload_folder': app.config['UPLOAD_FOLDER']
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File is too large. Maximum size is 16MB'
    }), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("="*60)
    print("🗑️  YOLO-Based Waste Detection System")
    print("="*60)
    print(f"Model loaded: {'✓ Yes' if detector else '✗ No'}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")
    print("="*60)
    print("Starting Flask server...")
    print("Access the application at: http://localhost:5000")
    print("="*60)
    
    # Run the Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )