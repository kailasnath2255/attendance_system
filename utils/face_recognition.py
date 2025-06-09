import cv2
import numpy as np
import os
import time
from datetime import datetime

def compare_faces(captured_img, reference_img_path):
    """
    Simple but effective face comparison for webcams
    """
    # Create debug directory
    debug_dir = "static/debug_images"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save captured image for debugging
    cv2.imwrite(os.path.join(debug_dir, f"captured_{timestamp}.jpg"), captured_img)
    
    # Check reference image
    if not os.path.exists(reference_img_path):
        print(f"Reference image not found: {reference_img_path}")
        return False
    
    reference_img = cv2.imread(reference_img_path)
    if reference_img is None:
        print("Failed to load reference image")
        return False
    
    # Initialize face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert to grayscale
    gray_captured = cv2.cvtColor(captured_img, cv2.COLOR_BGR2GRAY)
    gray_reference = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces with relaxed parameters
    captured_faces = face_cascade.detectMultiScale(gray_captured, 1.1, 3, minSize=(30, 30))
    reference_faces = face_cascade.detectMultiScale(gray_reference, 1.1, 3, minSize=(30, 30))
    
    if len(captured_faces) == 0:
        print("No face detected in captured image")
        return False
    
    if len(reference_faces) == 0:
        print("No face detected in reference image")  
        return False
    
    # Get largest faces
    captured_face = max(captured_faces, key=lambda x: x[2]*x[3])
    reference_face = max(reference_faces, key=lambda x: x[2]*x[3])
    
    # Extract face regions
    (x1, y1, w1, h1) = captured_face
    (x2, y2, w2, h2) = reference_face
    
    face_cap = gray_captured[y1:y1+h1, x1:x1+w1]
    face_ref = gray_reference[y2:y2+h2, x2:x2+w2]
    
    # Resize to same size
    size = (100, 100)
    face_cap = cv2.resize(face_cap, size)
    face_ref = cv2.resize(face_ref, size)
    
    # Save extracted faces
    cv2.imwrite(os.path.join(debug_dir, f"face_captured_{timestamp}.jpg"), face_cap)
    cv2.imwrite(os.path.join(debug_dir, f"face_reference_{timestamp}.jpg"), face_ref)
    
    # Method 1: Simple pixel difference
    diff = cv2.absdiff(face_cap, face_ref)
    diff_score = np.mean(diff)
    print(f"Pixel difference: {diff_score:.2f}")
    
    # Method 2: Correlation coefficient
    correlation = cv2.matchTemplate(face_cap, face_ref, cv2.TM_CCOEFF_NORMED)[0][0]
    print(f"Correlation: {correlation:.4f}")
    
    # Method 3: Histogram comparison
    hist1 = cv2.calcHist([face_cap], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([face_ref], [0], None, [256], [0, 256])
    hist_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    print(f"Histogram correlation: {hist_corr:.4f}")
    
    # Simple scoring system
    score = 0
    
    # Pixel difference check (lower is better)
    if diff_score < 50:  # Very lenient
        score += 1
        print("✓ Pixel difference check passed")
    
    # Correlation check
    if correlation > 0.5:  # Very lenient
        score += 1
        print("✓ Correlation check passed")
    
    # Histogram check
    if hist_corr > 0.2:  # Very lenient
        score += 1
        print("✓ Histogram check passed")
    
    print(f"Total score: {score}/3")
    
    # Need at least 2 out of 3 methods to pass
    return score >= 2

def capture_and_verify(camera_index=0, reference_img_path="reference.jpg"):
    """
    Simple capture and verify function
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return False
    
    print("Camera ready. Capturing in 3 seconds...")
    
    # Let camera adjust
    for i in range(10):
        ret, frame = cap.read()
        time.sleep(0.1)
    
    # Capture image
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Failed to capture image")
        return False
    
    print("Image captured. Comparing faces...")
    return compare_faces(frame, reference_img_path)

if __name__ == "__main__":
    camera_idx = 0
    reference_path = "reference.jpg"
    max_attempts = 3
    
    print("Simple Face Verification System")
    print(f"Reference image: {reference_path}")
    
    if not os.path.exists(reference_path):
        print(f"ERROR: {reference_path} not found!")
        exit(1)
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Attempt {attempt}/{max_attempts} ---")
        print("Look at the camera and stay still...")
        
        time.sleep(3)
        
        if capture_and_verify(camera_idx, reference_path):
            print("\n🎉 MATCH FOUND! Verification successful!")
            break
        else:
            print("\n❌ No match. Try again.")
            if attempt < max_attempts:
                print("Tips: Ensure good lighting and look directly at camera")
                time.sleep(2)
    else:
        print(f"\n❌ Failed after {max_attempts} attempts")