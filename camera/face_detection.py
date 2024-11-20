import cv2
import numpy as np
from typing import List, Dict, Tuple

class FaceDetector:
    def __init__(self):
        # Load pre-trained face detection model
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialize face detection parameters
        self.scale_factor = 1.1
        self.min_neighbors = 5
        self.min_size = (30, 30)

    def detect_faces(self, frame: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect faces in a frame and return their locations
        Returns: (faces_data, annotated_frame)
        """
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )

        # Process detected faces
        faces_data = []
        annotated_frame = frame.copy()

        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(
                annotated_frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            # Extract face region
            face_roi = frame[y:y+h, x:x+w]
            
            # Store face data
            faces_data.append({
                'bbox': (x, y, w, h),
                'confidence': 1.0,  # Placeholder for now
                'size': face_roi.shape[:2]
            })

        return faces_data, annotated_frame

    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a frame and return detection results
        """
        try:
            faces_data, annotated_frame = self.detect_faces(frame)
            
            # Encode processed frame
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            
            return {
                'success': True,
                'faces_detected': len(faces_data),
                'faces_data': faces_data,
                'processed_frame': buffer.tobytes()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 