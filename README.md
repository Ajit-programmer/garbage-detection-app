🗑️ Garbage Detection System
An intelligent waste classification application that uses YOLOv8 computer vision to detect and categorize garbage items in real-time. Built with Flask, OpenCV, and MySQL.

🎯 Features
✅ Real-time Detection - Detect garbage using webcam or uploaded images
✅ 6 Waste Categories - Cardboard, Glass, Metal, Paper, Plastic, Background
✅ 93% Accuracy - High precision detection with YOLOv8
✅ Image Upload - Upload photos for instant analysis
✅ Live Camera Detection - Use your device camera for real-time detection
✅ Detection History - Track all detections with timestamps
✅ Statistics Dashboard - View detection analytics and trends
✅ Secure Database - MySQL storage with environment variables

📊 Project Statistics
Model Accuracy: 93% (mAP50)
Training Dataset: 7,500+ images
Detection Classes: 6 waste types
Average Confidence: 90%+
🚀 Quick Start
Prerequisites
Python 3.8+
MySQL Server
Webcam (for live detection)
Installation
Clone the repository
bash
git clone https://github.com/Ajit-programmer/garbage-detection-app.git
cd garbage-detection-app
Create virtual environment
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies
bash
pip install -r requirements.txt
Create .env file
bash
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=garbage_detection
UPLOAD_FOLDER=uploads
MODEL_PATH=best.pt
FLASK_DEBUG=True
FLASK_ENV=development
Create MySQL database
sql
CREATE DATABASE garbage_detection;
Run the application
bash
python app.py
Open in browser
http://localhost:5000
📁 Project Structure
garbage_detection_app/
├── app.py                      # Main Flask application
├── best.pt                     # Trained YOLOv8 model
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore file
├── README.md                   # This file
├── templates/
│   ├── index.html             # Home page (upload & camera)
│   └── history.html           # Detection history page
└── uploads/                   # Detected image storage
🔧 Technology Stack
Component	Technology
Backend	Flask 2.3.0
Database	MySQL
Machine Learning	YOLOv8
Computer Vision	OpenCV
Frontend	HTML5, CSS3, JavaScript
Image Processing	Pillow
📖 Usage
1. Upload Image for Detection
Go to Home page
Click upload area or drag & drop image
View detected objects with confidence scores
Results automatically saved to database
2. Live Camera Detection
Click "Start Camera"
Allow camera access
Click "Capture & Detect" to analyze frame
Results saved with timestamp
3. View Detection History
Click "Detection History"
See all past detections
Filter by waste type
View statistics (total detections, accuracy, common items)
Delete old records
🗄️ Database Schema
sql
CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_path VARCHAR(255),
    detected_objects JSON,
    detection_count INT,
    detection_accuracy FLOAT,
    detection_time DATETIME,
    user_ip VARCHAR(50)
);
🎓 Model Performance
Metric	Value
mAP50	93%
mAP50-95	90%
Precision	95%+
Recall	92%+
Training Epochs	80
Detection Classes:
Cardboard - Paper-based packaging
Glass - Glass bottles and containers
Metal - Aluminum and metal items
Paper - Paper documents and products
Plastic - Plastic bottles and packaging
Background - Non-waste items
🔐 Security
✅ Passwords stored in .env file (not in code)
✅ Input validation on file uploads
✅ Secure file naming with timestamps
✅ SQL injection protection with parameterized queries
✅ .env file excluded from Git

Important Security Notes:
Never commit .env file to GitHub
Use strong MySQL passwords
Add .env to .gitignore
For production, use environment variables on deployment platform
🌐 Deployment
Deploy on Render (FREE)
Push code to GitHub
Go to https://render.com
Create new Web Service
Connect GitHub repository
Add environment variables:
   MYSQL_HOST = database_host
   MYSQL_USER = root
   MYSQL_PASSWORD = your_password
   MYSQL_DB = garbage_detection
Deploy! 🚀
Deploy on PythonAnywhere
Sign up at https://www.pythonanywhere.com
Upload files via web interface
Configure web app
Your app lives at username.pythonanywhere.com
Deploy on AWS
See detailed AWS deployment guide in documentation.

📊 API Endpoints
POST /detect
Upload image for detection

bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/detect
POST /camera-detect
Detect from camera frame

json
{
  "image": "data:image/jpeg;base64,..."
}
GET /api/history
Get detection history

bash
curl http://localhost:5000/api/history
GET /history
View history page (HTML)

POST /delete/<id>
Delete detection record

🐛 Troubleshooting
Error: ModuleNotFoundError: No module named 'dotenv'
bash
pip install python-dotenv
Error: MySQL connection refused
Check MySQL is running
Verify credentials in .env
Ensure database exists
Error: YOLO model not found
Check best.pt exists in project folder
Verify MODEL_PATH in .env
Camera not working
Grant browser permission for camera
Try different browser
Check webcam is connected
📝 Environment Variables Reference
bash
# Database Configuration
MYSQL_HOST          # MySQL server address (default: localhost)
MYSQL_USER          # MySQL username (default: root)
MYSQL_PASSWORD      # MySQL password (KEEP SECRET!)
MYSQL_DB            # Database name (default: garbage_detection)

# Application
UPLOAD_FOLDER       # Folder for uploaded images (default: uploads)
MODEL_PATH          # Path to YOLOv8 model (default: best.pt)
FLASK_DEBUG         # Debug mode (True/False)
FLASK_ENV           # Environment (development/production)
📈 Future Enhancements
 Real-time video stream detection
 Mobile app version
 Advanced analytics dashboard
 Email notifications for high-volume detections
 Multi-language support
 Export reports as PDF
 REST API for third-party integration
 Batch processing
 Model retraining pipeline
🤝 Contributing
Contributions are welcome! Feel free to:

Report bugs
Suggest features
Submit pull requests
Improve documentation
📄 License
This project is open source and available under the MIT License.

👤 Author
Ajit Gupta

Email: ajit12sci324@gmail.com
GitHub: @Ajit-programmer
LinkedIn: Ajit Gupta
🎓 Educational Value
This project demonstrates:

✅ YOLOv8 object detection
✅ Flask web application development
✅ MySQL database integration
✅ Real-time computer vision processing
✅ RESTful API design
✅ Frontend-backend integration
✅ Secure credential management
✅ Web deployment practices
📞 Support
For issues and questions:

Check the Troubleshooting section
Open an issue on GitHub
Contact via email
🙏 Acknowledgments
YOLOv8 by Ultralytics
Flask framework
OpenCV library
All contributors and testers
⭐ If you find this project useful, please give it a star on GitHub!

Made with ❤️ by Ajit Gupta

