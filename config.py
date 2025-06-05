# Configuration settings for the Face Recognition Attendance System

import os

# Application settings
APP_NAME = 'Face Recognition Attendance System'
DEBUG = True
SECRET_KEY = 'your_secret_key_here'  # Change this in production!

# Database settings
DATABASE_PATH = os.path.join('database', 'attendance.db')

# Upload settings
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# Face recognition settings
FACE_DETECTION_CONFIDENCE = 0.5
FACE_RECOGNITION_THRESHOLD = 0.6