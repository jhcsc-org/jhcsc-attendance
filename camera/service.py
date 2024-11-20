import cv2
from typing import Generator, Optional
from fastapi import HTTPException, status
import platform
import subprocess

class VideoStream:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.default_settings = {
            'brightness': 50,
            'contrast': 50,
            'saturation': 50,
            'exposure': -5,
            'zoom': 100
        }

    def _check_camera_available(self) -> bool:
        """Check if camera is available"""
        system = platform.system()
        
        if system == "Linux":
            try:
                # Check if video device exists
                result = subprocess.run(['ls', '/dev/video0'], capture_output=True)
                return result.returncode == 0
            except:
                return False
        elif system == "Windows":
            try:
                temp_cap = cv2.VideoCapture(self.camera_id)
                is_opened = temp_cap.isOpened()
                temp_cap.release()
                return is_opened
            except:
                return False
        return False

    def __enter__(self):
        try:
            if not self._check_camera_available():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No camera device found"
                )

            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to open camera"
                )
            
            # Set camera resolution to a lower value for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_running = True
            self._apply_default_settings()
            return self
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Camera initialization error: {str(e)}"
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            self.is_running = False
            self.cap.release()

    def _apply_default_settings(self):
        """Apply default camera settings"""
        try:
            # Only try to set settings if camera supports it
            if self.cap.get(cv2.CAP_PROP_BRIGHTNESS) >= 0:
                self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.default_settings['brightness'])
            if self.cap.get(cv2.CAP_PROP_CONTRAST) >= 0:
                self.cap.set(cv2.CAP_PROP_CONTRAST, self.default_settings['contrast'])
            if self.cap.get(cv2.CAP_PROP_SATURATION) >= 0:
                self.cap.set(cv2.CAP_PROP_SATURATION, self.default_settings['saturation'])
            if self.cap.get(cv2.CAP_PROP_EXPOSURE) >= 0:
                self.cap.set(cv2.CAP_PROP_EXPOSURE, self.default_settings['exposure'])
        except Exception as e:
            print(f"Warning: Could not apply default settings: {e}")

    def update_setting(self, setting: str, value: int) -> bool:
        """Update a camera setting"""
        if not self.is_running:
            return False

        prop_map = {
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION,
            'exposure': cv2.CAP_PROP_EXPOSURE,
        }

        if setting in prop_map:
            try:
                # Check if camera supports this property
                if self.cap.get(prop_map[setting]) >= 0:
                    return self.cap.set(prop_map[setting], value)
                return False
            except Exception as e:
                print(f"Warning: Could not update {setting}: {e}")
                return False
        return False

    def get_frame(self, flip: bool = True) -> bytes:
        """Capture a frame from the camera and return it as JPEG bytes"""
        if not self.is_running:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Camera is not running"
            )

        try:
            success, frame = self.cap.read()
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to capture frame"
                )

            if flip:
                frame = cv2.flip(frame, 1)  # Mirror effect for better UX

            # Convert frame to JPEG format with reduced quality for better performance
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to encode frame"
                )

            return buffer.tobytes()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Frame capture error: {str(e)}"
            )

def generate_frames() -> Generator[bytes, None, None]:
    """Generate a stream of camera frames"""
    try:
        with VideoStream() as camera:
            while camera.is_running:
                try:
                    frame = camera.get_frame()
                    yield (b'--frame\r\n'
                          b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except Exception as e:
                    print(f"Frame generation error: {e}")
                    break
    except HTTPException as e:
        print(f"Camera error: {e.detail}")
        # Return an error frame or placeholder image
        with open("static/no_camera.jpg", "rb") as f:
            error_frame = f.read()
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')