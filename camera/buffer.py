from collections import deque
from threading import Lock
import time
from typing import Optional, Dict
import numpy as np
import cv2
from .face_detection import FaceDetector

class FrameBuffer:
    def __init__(self, max_size: int = 30, buffer_timeout: float = 1.0):
        self.buffer = deque(maxlen=max_size)
        self.lock = Lock()
        self.last_frame_time = 0
        self.buffer_timeout = buffer_timeout
        self.processing = False
        self.face_detector = FaceDetector()
        
        # Performance optimizations
        self.skip_frames = 2  # Process every nth frame
        self.frame_counter = 0
        self.last_processed_result = None
        self.processing_resolution = (640, 480)  # Reduced resolution for processing

    def _resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """Resize frame for processing"""
        return cv2.resize(frame, self.processing_resolution)

    def add_frame(self, frame: np.ndarray, session_id: str) -> None:
        """Add a frame to the buffer with optimizations"""
        with self.lock:
            current_time = time.time()
            
            # Skip frames for performance
            self.frame_counter += 1
            if self.frame_counter % self.skip_frames != 0:
                return

            # Resize frame for processing
            processed_frame = self._resize_frame(frame)
            
            self.buffer.append({
                'frame': processed_frame,
                'original_frame': frame,
                'timestamp': current_time,
                'session_id': session_id,
                'processed': False
            })
            self.last_frame_time = current_time

    def process_frames(self) -> Optional[Dict]:
        """Process frames in buffer"""
        with self.lock:
            if not self.buffer:
                return None

            current_time = time.time()
            
            # Remove old frames
            while self.buffer and (current_time - self.buffer[0]['timestamp']) > self.buffer_timeout:
                self.buffer.popleft()

            # Get next unprocessed frame
            for frame_data in self.buffer:
                if not frame_data['processed']:
                    frame_data['processed'] = True
                    
                    # Process frame with face detection
                    result = self.face_detector.process_frame(frame_data['frame'])
                    if result['success']:
                        self.last_processed_result = result
                        return {
                            **result,
                            'session_id': frame_data['session_id'],
                            'timestamp': frame_data['timestamp']
                        }

        return None

    def clear_buffer(self, session_id: Optional[str] = None) -> None:
        """Clear the buffer, optionally only for a specific session"""
        with self.lock:
            if session_id:
                self.buffer = deque(
                    [f for f in self.buffer if f['session_id'] != session_id],
                    maxlen=self.buffer.maxlen
                )
            else:
                self.buffer.clear()

    def get_buffer_status(self) -> Dict:
        """Get current buffer status"""
        with self.lock:
            return {
                'buffer_size': len(self.buffer),
                'max_size': self.buffer.maxlen,
                'last_frame_age': time.time() - self.last_frame_time if self.last_frame_time else None,
                'is_processing': self.processing
            }

class FrameBufferManager:
    _instance = None
    _buffers: Dict[str, FrameBuffer] = {}
    _lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_buffer(self, buffer_id: str, create_if_missing: bool = True) -> Optional[FrameBuffer]:
        """Get or create a buffer for a specific ID"""
        with self._lock:
            if buffer_id not in self._buffers and create_if_missing:
                self._buffers[buffer_id] = FrameBuffer()
            return self._buffers.get(buffer_id)

    def remove_buffer(self, buffer_id: str) -> None:
        """Remove a buffer"""
        with self._lock:
            if buffer_id in self._buffers:
                self._buffers[buffer_id].clear_buffer()
                del self._buffers[buffer_id]

    def get_all_buffer_statuses(self) -> Dict[str, Dict]:
        """Get status of all buffers"""
        with self._lock:
            return {
                buffer_id: buffer.get_buffer_status()
                for buffer_id, buffer in self._buffers.items()
            } 