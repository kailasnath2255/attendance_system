import cv2
import numpy as np
import os
import time
from datetime import datetime

def compare_faces(captured_img, reference_img_path, threshold=0.6):
    """
    Compare two faces using OpenCV's LBPH Face Recognizer
    
    Args:
        captured_img: Image captured from the webcam
        reference_img_path: Path to the reference image
        threshold: Confidence threshold (lower = more strict)
        
    Returns:
        Boolean: True if faces match, False otherwise
    """
    # Create debug directory if it doesn't exist
    debug_dir = "static/debug_images"
    os.makedirs(debug_dir, exist_ok=True)
    
    # Generate timestamp for debug images
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save captured image for debugging
    debug_captured_path = os.path.join(debug_dir, f"captured_{timestamp}.jpg")
    cv2.imwrite(debug_captured_path, captured_img)
    
    # Check if reference image exists
    if not os.path.exists(reference_img_path):
        print(f"Reference image not found: {reference_img_path}")
        return False
    
    # Load the reference image
    reference_img = cv2.imread(reference_img_path)
    if reference_img is None:
        print("Failed to load reference image")
        return False
    
    # Save a copy of reference image for debugging
    debug_reference_path = os.path.join(debug_dir, f"reference_{timestamp}.jpg")
    cv2.imwrite(debug_reference_path, reference_img)
    
    # Initialize face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert images to grayscale
    gray_captured = cv2.cvtColor(captured_img, cv2.COLOR_BGR2GRAY)
    gray_reference = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in both images
    captured_faces = face_cascade.detectMultiScale(gray_captured, 1.3, 5, minSize=(30, 30))
    reference_faces = face_cascade.detectMultiScale(gray_reference, 1.3, 5, minSize=(30, 30))
    
    # If no face detected in either image
    if len(captured_faces) == 0:
        print("No face detected in captured image")
        return False
    
    if len(reference_faces) == 0:
        print("No face detected in reference image")
        return False
    
    # Extract face regions
    (x1, y1, w1, h1) = captured_faces[0]
    (x2, y2, w2, h2) = reference_faces[0]
    
    face_captured = gray_captured[y1:y1+h1, x1:x1+w1]
    face_reference = gray_reference[y2:y2+h2, x2:x2+w2]
    
    # Save extracted faces for debugging
    debug_face_captured = os.path.join(debug_dir, f"face_captured_{timestamp}.jpg")
    debug_face_reference = os.path.join(debug_dir, f"face_reference_{timestamp}.jpg")
    cv2.imwrite(debug_face_captured, face_captured)
    cv2.imwrite(debug_face_reference, face_reference)
    
    # Resize both faces to the same size
    face_captured = cv2.resize(face_captured, (100, 100))
    face_reference = cv2.resize(face_reference, (100, 100))
    
    # Try multiple approaches for face recognition
    
    # Approach 1: LBPH Face Recognizer
    try:
        # Initialize LBPH Face Recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Train the recognizer with reference face
        recognizer.train([face_reference], np.array([0]))
        
        # Predict the captured face
        label, confidence = recognizer.predict(face_captured)
        
        # Convert confidence to similarity score (0-100%)
        # Higher confidence in LBPH means less similarity
        similarity = max(0, 100 - confidence)
        
        print(f"LBPH Face similarity: {similarity:.2f}% (threshold: {threshold*100:.0f}%)")
        
        if similarity/100 >= threshold:
            return True
    except Exception as e:
        print(f"LBPH error: {str(e)}")
    
    # Approach 2: Simple structural similarity index
    try:
        from skimage.metrics import structural_similarity as ssim
        
        # Calculate structural similarity index
        score = ssim(face_captured, face_reference, data_range=face_reference.max() - face_reference.min())
        print(f"SSIM similarity score: {score:.4f}")
        
        if score >= threshold:
            return True
    except ImportError:
        print("scikit-image not available, skipping SSIM check")
    
    # Approach 3: Normalized cross-correlation
    try:
        result = cv2.matchTemplate(face_captured, face_reference, cv2.TM_CCORR_NORMED)
        correlation = np.max(result)
        print(f"Template matching correlation: {correlation:.4f}")
        
        if correlation >= 0.8:  # Higher threshold for correlation
            return True
    except Exception as e:
        print(f"Template matching error: {str(e)}")
    
    # If all approaches failed
    return False

def capture_and_verify(camera_index=0, reference_img_path="reference.jpg"):
    """
    Capture an image from webcam and verify against reference
    
    Args:
        camera_index: Index of the camera to use
        reference_img_path: Path to the reference image
        
    Returns:
        Boolean: True if verification successful
    """
    # Initialize camera
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return False
    
    print("Camera opened successfully. Preparing to capture...")
    
    # Give camera time to adjust
    for _ in range(5):
        cap.read()
    
    # Capture frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Failed to capture image")
        return False
    
    # Compare faces
    match = compare_faces(frame, reference_img_path)
    
    if match:
        print("Face verification successful!")
    else:
        print("Face verification failed.")
    
    return match

if __name__ == "__main__":
    import time
    
    # You can adjust these parameters
    camera_idx = 0  # Change if you have multiple cameras
    reference_path = "reference.jpg"  # Path to your reference image
    max_attempts = 3
    
    print("Face verification system")
    print(f"Using reference image: {reference_path}")
    
    # Allow multiple attempts
    for attempt in range(1, max_attempts + 1):
        print(f"\nAttempt {attempt} of {max_attempts}")
        print("Please position your face clearly in front of the camera")
        print("Capturing in 3 seconds...")
        time.sleep(3)
        
        if capture_and_verify(camera_idx, reference_path):
            print("Verification successful!")
            break
        
        if attempt < max_attempts:
            print("Please try again. Make sure:")
            print("- Your face is clearly visible")
            print("- There is adequate lighting")
            print("- You're looking directly at the camera")
            time.sleep(2)
    else:
        print("Maximum verification attempts reached. Authentication failed.")