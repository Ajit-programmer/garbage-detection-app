from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import json

app = Flask(__name__)
mysql = MySQL(app)

# Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ajit@1234'
app.config['MYSQL_DB'] = 'garbage_detection'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load YOLO model
model = YOLO('best.pt')  # Use your trained model path

# Create MySQL table (moved inside app context)
def create_table():
    """Create detection table if it doesn't exist"""
    try:
        with app.app_context():
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    image_path VARCHAR(255),
                    detected_objects JSON,
                    detection_count INT,
                    detection_accuracy FLOAT,
                    detection_time DATETIME,
                    user_ip VARCHAR(50)
                )
            ''')
            mysql.connection.commit()
            cursor.close()
            print("✅ Database table created successfully!")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

def detect_garbage(image_path):
    """Detect garbage in image using YOLO"""
    img = cv2.imread(image_path)
    if img is None:
        return []
    
    results = model(img)
    
    detections = []
    for r in results:
        for box in r.boxes:
            cls_name = r.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            detections.append({
                'class': cls_name,
                'confidence': round(confidence, 2)
            })
    
    return detections

def save_detection_to_db(image_path, detections, user_ip):
    """Save detection results to MySQL database"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        detected_objects = json.dumps(detections)
        detection_count = len(detections)
        avg_accuracy = round(sum([d['confidence'] for d in detections]) / len(detections), 2) if detections else 0
        
        cursor.execute('''
            INSERT INTO detections (image_path, detected_objects, detection_count, detection_accuracy, detection_time, user_ip)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (image_path, detected_objects, detection_count, avg_accuracy, datetime.now(), user_ip))
        
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"❌ Error saving to database: {e}")

@app.route('/')
def home():
    """Home page with upload and camera options"""
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    """Handle file upload and detection"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Detect garbage
        detections = detect_garbage(filepath)
        
        # Save to database
        user_ip = request.remote_addr
        save_detection_to_db(filepath, detections, user_ip)
        
        return jsonify({
            'success': True,
            'detections': detections,
            'image_path': filepath,
            'detection_count': len(detections)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/camera-detect', methods=['POST'])
def camera_detect():
    """Handle camera frame detection"""
    try:
        data = request.json
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Save image
        filename = f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filepath, image_cv)
        
        # Detect garbage
        detections = detect_garbage(filepath)
        
        # Save to database
        user_ip = request.remote_addr
        save_detection_to_db(filepath, detections, user_ip)
        
        return jsonify({
            'success': True,
            'detections': detections,
            'image_path': filepath,
            'detection_count': len(detections)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    """Display detection history"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM detections ORDER BY detection_time DESC')
        detections = cursor.fetchall()
        cursor.close()
        
        # Parse JSON objects
        for detection in detections:
            detection['detected_objects'] = json.loads(detection['detected_objects'])
        
        return render_template('history.html', detections=detections)
    except Exception as e:
        return f"Error loading history: {e}", 500

@app.route('/api/history', methods=['GET'])
def api_history():
    """API endpoint to get detection history"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM detections ORDER BY detection_time DESC LIMIT 50')
        detections = cursor.fetchall()
        cursor.close()
        
        for detection in detections:
            detection['detected_objects'] = json.loads(detection['detected_objects'])
            detection['detection_time'] = str(detection['detection_time'])
        
        return jsonify(detections)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<int:id>', methods=['POST'])
def delete_detection(id):
    """Delete a detection record"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM detections WHERE id = %s', (id,))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"❌ Error deleting record: {e}")
    
    return redirect(url_for('history'))

if __name__ == '__main__':
    # Create table when app starts
    create_table()
    print("🚀 Starting Flask app...")
    app.run(debug=True)