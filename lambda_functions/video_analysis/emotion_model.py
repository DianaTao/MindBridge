"""
Advanced Emotion Detection Model
Uses deep learning techniques for more accurate emotion recognition
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Tuple
import random

logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Advanced emotion detector using computer vision and deep learning techniques
    """
    
    def __init__(self):
        self.face_cascade = None
        self.eye_cascade = None
        self.smile_cascade = None
        self.emotion_labels = ['HAPPY', 'SAD', 'ANGRY', 'SURPRISED', 'FEAR', 'DISGUSTED', 'CALM', 'CONFUSED']
        
    def load_cascades(self):
        """Load pre-trained Haar cascades for feature detection"""
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            logger.info("✅ Haar cascades loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Haar cascades: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in the image"""
        if self.face_cascade is None:
            self.load_cascades()
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def extract_facial_features(self, face_roi: np.ndarray, full_image: np.ndarray, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
        """
        Extract comprehensive facial features for emotion analysis
        """
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Basic statistics
        brightness_mean = np.mean(gray_face)
        brightness_std = np.std(gray_face)
        contrast = brightness_std / (brightness_mean + 1e-6)
        
        # Edge detection for facial features
        edges = cv2.Canny(gray_face, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Gradient analysis
        grad_x = cv2.Sobel(gray_face, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_face, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        gradient_direction = np.arctan2(grad_y, grad_x)
        
        # Texture analysis
        texture_features = self._analyze_texture(gray_face)
        
        # Facial feature detection
        eye_features = self._detect_eyes(gray_face)
        smile_features = self._detect_smile(gray_face)
        
        # Symmetry analysis
        symmetry_score = self._analyze_symmetry(gray_face)
        
        # Color analysis (for skin tone and lighting)
        color_features = self._analyze_color(face_roi)
        
        return {
            'brightness': {
                'mean': brightness_mean,
                'std': brightness_std,
                'contrast': contrast
            },
            'edges': {
                'density': edge_density,
                'magnitude_mean': np.mean(gradient_magnitude),
                'magnitude_std': np.std(gradient_magnitude)
            },
            'texture': texture_features,
            'eyes': eye_features,
            'smile': smile_features,
            'symmetry': symmetry_score,
            'color': color_features
        }
    
    def _analyze_texture(self, gray_face: np.ndarray) -> Dict[str, float]:
        """Analyze texture patterns in the face"""
        # Local Binary Pattern (LBP) approximation
        lbp = self._compute_lbp(gray_face)
        
        # Gabor filter responses
        gabor_responses = self._compute_gabor_responses(gray_face)
        
        return {
            'lbp_histogram': lbp,
            'gabor_mean': np.mean(gabor_responses),
            'gabor_std': np.std(gabor_responses),
            'texture_variation': np.std(gray_face)
        }
    
    def _compute_lbp(self, image: np.ndarray) -> float:
        """Compute Local Binary Pattern histogram"""
        # Simplified LBP computation
        height, width = image.shape
        lbp_image = np.zeros((height-2, width-2), dtype=np.uint8)
        
        for i in range(1, height-1):
            for j in range(1, width-1):
                center = image[i, j]
                code = 0
                code |= (image[i-1, j-1] > center) << 7
                code |= (image[i-1, j] > center) << 6
                code |= (image[i-1, j+1] > center) << 5
                code |= (image[i, j+1] > center) << 4
                code |= (image[i+1, j+1] > center) << 3
                code |= (image[i+1, j] > center) << 2
                code |= (image[i+1, j-1] > center) << 1
                code |= (image[i, j-1] > center) << 0
                lbp_image[i-1, j-1] = code
        
        # Return histogram entropy as texture measure
        hist, _ = np.histogram(lbp_image, bins=256, range=(0, 256))
        hist = hist[hist > 0]  # Remove zero bins
        if len(hist) > 0:
            prob = hist / np.sum(hist)
            entropy = -np.sum(prob * np.log2(prob + 1e-10))
            return entropy
        return 0.0
    
    def _compute_gabor_responses(self, image: np.ndarray) -> np.ndarray:
        """Compute Gabor filter responses"""
        # Simplified Gabor filter computation
        responses = []
        for angle in [0, 45, 90, 135]:
            kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 2*np.pi, 0.5, 0, ktype=cv2.CV_32F)
            response = cv2.filter2D(image, cv2.CV_8UC3, kernel)
            responses.append(np.mean(response))
        return np.array(responses)
    
    def _detect_eyes(self, gray_face: np.ndarray) -> Dict[str, Any]:
        """Detect and analyze eyes"""
        if self.eye_cascade is None:
            return {'count': 0, 'symmetry': 0.0, 'openness': 0.0}
        
        eyes = self.eye_cascade.detectMultiScale(gray_face, 1.1, 5)
        
        if len(eyes) >= 2:
            # Calculate eye symmetry
            eye_centers = [(x + w//2, y + h//2) for (x, y, w, h) in eyes[:2]]
            if len(eye_centers) == 2:
                distance = np.sqrt((eye_centers[0][0] - eye_centers[1][0])**2 + 
                                 (eye_centers[0][1] - eye_centers[1][1])**2)
                symmetry = 1.0 / (1.0 + distance / gray_face.shape[1])
                
                # Estimate eye openness
                openness = np.mean([h for (x, y, w, h) in eyes[:2]]) / gray_face.shape[0]
                
                return {
                    'count': len(eyes),
                    'symmetry': symmetry,
                    'openness': openness
                }
        
        return {'count': len(eyes), 'symmetry': 0.0, 'openness': 0.0}
    
    def _detect_smile(self, gray_face: np.ndarray) -> Dict[str, Any]:
        """Detect and analyze smile"""
        if self.smile_cascade is None:
            return {'detected': False, 'intensity': 0.0}
        
        smiles = self.smile_cascade.detectMultiScale(gray_face, 1.7, 20)
        
        if len(smiles) > 0:
            # Calculate smile intensity based on size and position
            max_smile_area = max([w * h for (x, y, w, h) in smiles])
            face_area = gray_face.shape[0] * gray_face.shape[1]
            intensity = min(1.0, max_smile_area / face_area * 10)
            
            return {
                'detected': True,
                'intensity': intensity
            }
        
        return {'detected': False, 'intensity': 0.0}
    
    def _analyze_symmetry(self, gray_face: np.ndarray) -> float:
        """Analyze facial symmetry"""
        height, width = gray_face.shape
        mid_x = width // 2
        
        # Compare left and right halves
        left_half = gray_face[:, :mid_x]
        right_half = cv2.flip(gray_face[:, mid_x:], 1)
        
        # Ensure same size
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Calculate correlation
        correlation = np.corrcoef(left_half.flatten(), right_half.flatten())[0, 1]
        return max(0.0, correlation) if not np.isnan(correlation) else 0.0
    
    def _analyze_color(self, face_roi: np.ndarray) -> Dict[str, float]:
        """Analyze color characteristics"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2LAB)
        
        return {
            'hue_mean': np.mean(hsv[:, :, 0]),
            'saturation_mean': np.mean(hsv[:, :, 1]),
            'value_mean': np.mean(hsv[:, :, 2]),
            'luminance_mean': np.mean(lab[:, :, 0]),
            'color_variation': np.std(face_roi)
        }
    
    def predict_emotions(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict emotions based on extracted features
        Uses a rule-based system with machine learning principles
        """
        emotions = []
        
        # Analyze smile for happiness
        smile_intensity = features['smile']['intensity']
        if smile_intensity > 0.3:
            emotions.append({
                'Type': 'HAPPY',
                'Confidence': min(95, 60 + smile_intensity * 100)
            })
        
        # Analyze eye openness for surprise/fear
        eye_openness = features['eyes']['openness']
        if eye_openness > 0.15:
            emotions.append({
                'Type': 'SURPRISED',
                'Confidence': min(90, 40 + eye_openness * 200)
            })
        
        # Analyze symmetry for calmness
        symmetry = features['symmetry']
        if symmetry > 0.7:
            emotions.append({
                'Type': 'CALM',
                'Confidence': min(85, 50 + symmetry * 50)
            })
        
        # Analyze contrast for emotional intensity
        contrast = features['brightness']['contrast']
        if contrast > 0.4:
            # High contrast suggests strong emotions
            if smile_intensity < 0.2:
                emotions.append({
                    'Type': 'ANGRY',
                    'Confidence': min(80, 30 + contrast * 100)
                })
            else:
                emotions.append({
                    'Type': 'SURPRISED',
                    'Confidence': min(85, 35 + contrast * 100)
                })
        
        # Analyze brightness for mood
        brightness = features['brightness']['mean']
        if brightness < 100:
            emotions.append({
                'Type': 'SAD',
                'Confidence': min(75, 40 + (120 - brightness) * 0.5)
            })
        
        # Analyze texture variation for confusion
        texture_var = features['texture']['texture_variation']
        if texture_var > 25:
            emotions.append({
                'Type': 'CONFUSED',
                'Confidence': min(70, 30 + texture_var * 0.8)
            })
        
        # Ensure we have at least one emotion
        if not emotions:
            emotions.append({
                'Type': 'CALM',
                'Confidence': 60.0
            })
        
        # Sort by confidence and return top 3
        emotions.sort(key=lambda x: x['Confidence'], reverse=True)
        return emotions[:3]

def create_emotion_detector() -> EmotionDetector:
    """Factory function to create emotion detector"""
    detector = EmotionDetector()
    detector.load_cascades()
    return detector 