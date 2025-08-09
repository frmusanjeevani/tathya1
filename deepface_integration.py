"""
DeepFace Integration Module for Face Verification
Provides advanced facial recognition capabilities using multiple deep learning models
"""

import os
import tempfile
import streamlit as st
from PIL import Image
import io

# DeepFace imports
try:
    from deepface import DeepFace
    import cv2
    import numpy as np
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

class DeepFaceVerification:
    """DeepFace-based face verification system"""
    
    def __init__(self):
        self.models = ['VGG-Face', 'Facenet', 'OpenFace', 'DeepFace', 'DeepID', 'ArcFace', 'Dlib', 'SFace']
        self.default_model = 'VGG-Face'  # Most reliable model
        self.detector_backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe']
        self.default_detector = 'opencv'
    
    def verify_faces(self, reference_image, comparison_image, model_name=None, detector_backend=None):
        """
        Verify if two face images belong to the same person
        
        Args:
            reference_image: PIL Image or file upload object
            comparison_image: PIL Image or file upload object
            model_name: DeepFace model to use (default: VGG-Face)
            detector_backend: Face detection backend (default: opencv)
        
        Returns:
            dict: Verification results with confidence scores and details
        """
        if not DEEPFACE_AVAILABLE:
            return {
                'success': False,
                'error': 'DeepFace library not available. Please install deepface, tensorflow, and opencv-python.'
            }
        
        try:
            model = model_name or self.default_model
            detector = detector_backend or self.default_detector
            
            # Save images to temporary files for DeepFace processing
            ref_path = self._save_temp_image(reference_image)
            comp_path = self._save_temp_image(comparison_image)
            
            if not ref_path or not comp_path:
                return {
                    'success': False,
                    'error': 'Failed to process uploaded images'
                }
            
            # Perform face verification using DeepFace
            result = DeepFace.verify(
                img1_path=ref_path,
                img2_path=comp_path,
                model_name=model,
                detector_backend=detector,
                distance_metric='cosine',
                enforce_detection=False
            )
            
            # Clean up temporary files
            self._cleanup_temp_files([ref_path, comp_path])
            
            # Process results
            verified = result.get('verified', False)
            distance = result.get('distance', 1.0)
            threshold = result.get('threshold', 0.4)
            
            # Calculate match percentage (higher is better match)
            match_percentage = max(0, (1 - (distance / threshold)) * 100)
            match_percentage = min(100, match_percentage)
            
            # Determine verification status
            if verified:
                if match_percentage >= 90:
                    status = 'PASSED'
                elif match_percentage >= 70:
                    status = 'REVIEW REQUIRED'
                else:
                    status = 'PASSED'  # DeepFace says verified
            else:
                status = 'FAILED'
            
            return {
                'success': True,
                'verified': verified,
                'match_percentage': round(match_percentage, 2),
                'confidence_score': round(1 - distance, 3),
                'verification_status': status,
                'model_used': model,
                'detector_used': detector,
                'distance': round(distance, 4),
                'threshold': round(threshold, 4),
                'details': {
                    'face_detection': 'DeepFace detection completed',
                    'quality_score': round(1 - distance, 3),
                    'landmark_match': f'Model: {model}',
                    'processing_method': 'DeepFace Deep Learning'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'DeepFace verification failed: {str(e)}',
                'fallback_required': True
            }
    
    def analyze_face(self, image, actions=['age', 'gender', 'race', 'emotion']):
        """
        Analyze facial attributes using DeepFace
        
        Args:
            image: PIL Image or file upload object
            actions: List of analysis actions to perform
        
        Returns:
            dict: Analysis results with demographic information
        """
        if not DEEPFACE_AVAILABLE:
            return {
                'success': False,
                'error': 'DeepFace library not available'
            }
        
        try:
            image_path = self._save_temp_image(image)
            if not image_path:
                return {'success': False, 'error': 'Failed to process image'}
            
            # Perform face analysis
            analysis = DeepFace.analyze(
                img_path=image_path,
                actions=actions,
                detector_backend=self.default_detector,
                enforce_detection=False
            )
            
            # Clean up
            self._cleanup_temp_files([image_path])
            
            # Process results (handle both single face and multiple faces)
            if isinstance(analysis, list):
                analysis = analysis[0]  # Use first face if multiple detected
            
            return {
                'success': True,
                'age': analysis.get('age', 'Unknown'),
                'gender': analysis.get('dominant_gender', 'Unknown'),
                'race': analysis.get('dominant_race', 'Unknown'),
                'emotion': analysis.get('dominant_emotion', 'Unknown'),
                'region': analysis.get('region', {}),
                'face_confidence': analysis.get('face_confidence', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Face analysis failed: {str(e)}'
            }
    
    def find_similar_faces(self, target_image, database_path, model_name=None):
        """
        Find similar faces in a database of images
        
        Args:
            target_image: PIL Image or file upload object
            database_path: Path to directory containing face images
            model_name: DeepFace model to use
        
        Returns:
            dict: Results with similar faces found
        """
        if not DEEPFACE_AVAILABLE:
            return {'success': False, 'error': 'DeepFace library not available'}
        
        try:
            model = model_name or self.default_model
            target_path = self._save_temp_image(target_image)
            
            if not target_path:
                return {'success': False, 'error': 'Failed to process target image'}
            
            # Find similar faces
            results = DeepFace.find(
                img_path=target_path,
                db_path=database_path,
                model_name=model,
                detector_backend=self.default_detector,
                enforce_detection=False
            )
            
            self._cleanup_temp_files([target_path])
            
            return {
                'success': True,
                'matches_found': len(results) if isinstance(results, list) else 0,
                'results': results,
                'model_used': model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Face search failed: {str(e)}'
            }
    
    def _save_temp_image(self, image):
        """Save uploaded image to temporary file for DeepFace processing"""
        try:
            if hasattr(image, 'read'):
                # File upload object
                image_bytes = image.read()
                image.seek(0)  # Reset file pointer
                pil_image = Image.open(io.BytesIO(image_bytes))
            elif isinstance(image, Image.Image):
                # PIL Image
                pil_image = image
            else:
                return None
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Save to temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(temp_fd)
            pil_image.save(temp_path, 'JPEG', quality=95)
            
            return temp_path
            
        except Exception as e:
            st.error(f"Error saving temporary image: {str(e)}")
            return None
    
    def _cleanup_temp_files(self, file_paths):
        """Clean up temporary files"""
        for path in file_paths:
            try:
                if path and os.path.exists(path):
                    os.unlink(path)
            except Exception:
                pass  # Ignore cleanup errors
    
    def get_available_models(self):
        """Get list of available DeepFace models"""
        return self.models
    
    def get_available_detectors(self):
        """Get list of available face detection backends"""
        return self.detector_backends

# Global instance for easy access
deepface_verifier = DeepFaceVerification()

def perform_deepface_verification(reference_image, comparison_image, model_name=None):
    """
    Convenience function for face verification using DeepFace
    
    Args:
        reference_image: Reference face image
        comparison_image: Comparison face image
        model_name: Optional model name to use
    
    Returns:
        dict: Verification results
    """
    return deepface_verifier.verify_faces(reference_image, comparison_image, model_name)

def analyze_face_attributes(image):
    """
    Convenience function for face analysis using DeepFace
    
    Args:
        image: Face image to analyze
    
    Returns:
        dict: Analysis results with age, gender, race, emotion
    """
    return deepface_verifier.analyze_face(image)