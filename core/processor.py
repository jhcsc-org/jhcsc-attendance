import face_recognition as fr
import numpy as np
from typing import List, Tuple, Optional, Union
import io

from config import Settings

class FaceRecognitionProcessor:
    def __init__(self, tolerance: float = Settings.FACE_RECOGNITION_TOLERANCE):
        """
        Initialize the FaceRecognitionProcessor with a tolerance value.
        
        Args:
            tolerance: Threshold for face comparison (0-1). Lower means more strict.
        """
        self.tolerance = tolerance
        self._known_face_encodings = []
        self._known_face_labels = []

    def load_image(self, image_data: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Load an image from various input formats.
        
        Args:
            image_data: Can be file path, bytes, or numpy array
            
        Returns:
            numpy.ndarray: Loaded image
        """
        if isinstance(image_data, str):
            return fr.load_image_file(image_data)
        elif isinstance(image_data, bytes):
            return fr.load_image_file(io.BytesIO(image_data))
        return image_data

    def detect_and_encode_faces(self, 
                              image: np.ndarray,
                              return_locations: bool = False
                              ) -> Union[List[np.ndarray], Tuple[List[np.ndarray], List[Tuple]]]:
        """
        Detect and encode all faces in an image.
        
        Args:
            image: Input image
            return_locations: Whether to return face locations
            
        Returns:
            Face encodings and optionally face locations
        """
        locations = fr.face_locations(image, model="cnn")
        encodings = fr.face_encodings(image, locations)
        
        return (encodings, locations) if return_locations else encodings

    def register_known_face(self, face_encoding: np.ndarray, label: str) -> None:
        """
        Register a known face with a label for later comparison.
        
        Args:
            face_encoding: Face encoding to store
            label: Label to associate with the face
        """
        self._known_face_encodings.append(face_encoding)
        self._known_face_labels.append(label)

    def identify_face(self, 
                     face_encoding: np.ndarray, 
                     min_confidence: float = None
                     ) -> Optional[Tuple[str, float]]:
        """
        Identify a face against registered known faces.
        
        Args:
            face_encoding: Face encoding to check
            min_confidence: Minimum confidence threshold (optional)
            
        Returns:
            Tuple of (label, confidence) if match found, None otherwise
        """
        if not self._known_face_encodings:
            return None

        distances = fr.face_distance(self._known_face_encodings, face_encoding)
        min_distance_idx = np.argmin(distances)
        confidence = 1 - distances[min_distance_idx]

        if min_confidence and confidence < min_confidence:
            return None

        if confidence >= self.tolerance:
            return (self._known_face_labels[min_distance_idx], confidence)
        
        return None

    def process_image(self, 
                     image_data: Union[str, bytes, np.ndarray],
                     min_confidence: float = None
                     ) -> List[dict]:
        """
        Process an image and return all face detections with identifications.
        
        Args:
            image_data: Input image
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of dictionaries containing face information
        """
        image = self.load_image(image_data)
        encodings, locations = self.detect_and_encode_faces(image, return_locations=True)
        
        results = []
        for encoding, location in zip(encodings, locations):
            identification = self.identify_face(encoding, min_confidence)
            
            result = {
                "location": {
                    "top": location[0],
                    "right": location[1],
                    "bottom": location[2],
                    "left": location[3]
                }
            }
            
            if identification:
                result["identity"] = {
                    "label": identification[0],
                    "confidence": float(identification[1])
                }
            
            results.append(result)
            
        return results

    def compare_faces(self, 
                     face1: np.ndarray, 
                     face2: np.ndarray
                     ) -> Tuple[bool, float]:
        """
        Compare two face encodings.
        
        Args:
            face1: First face encoding
            face2: Second face encoding
            
        Returns:
            Tuple of (is_match, confidence)
        """
        distance = fr.face_distance([face1], face2)[0]
        confidence = 1 - distance
        return confidence >= self.tolerance, confidence