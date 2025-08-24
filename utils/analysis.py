import os
import base64
from typing import Dict, Tuple, Optional, Any
import google.generativeai as genai
from PIL import Image
import io
from config import Config

class PollutionAnalyzer:
    """Utility class for analyzing pollution in images using Gemini AI."""
    
    def __init__(self):
        """Initialize Gemini AI client."""
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.confidence_threshold = Config.ANALYSIS_CONFIDENCE_THRESHOLD
        
        # Check if API key is properly set
        if self.api_key and self.api_key != "AIzaSyC...your-actual-api-key-here..." and len(self.api_key) > 20:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.is_available = True
                print(f"✅ Gemini AI initialized successfully with model: {self.model_name}")
            except Exception as e:
                print(f"❌ Warning: Gemini AI initialization failed: {e}")
                self.is_available = False
        else:
            self.is_available = False
            print("⚠️ Warning: No valid Gemini API key provided. Using fallback analysis.")
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image for pollution detection using Gemini AI.
        Falls back to mock analysis if API is unavailable.
        """
        if not self.is_available:
            return self._fallback_analysis()
        
        try:
            # Load and prepare image
            image = self._load_image(image_path)
            if not image:
                return self._fallback_analysis()
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt()
            
            # Get AI analysis
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            analysis_result = self._parse_ai_response(response.text)
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Error in Gemini AI analysis: {e}")
            return self._fallback_analysis()
    
    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load and prepare image for Gemini AI."""
        try:
            # Load image using PIL
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (Gemini has size limits)
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return None
    
    def _create_analysis_prompt(self) -> str:
        """Create a detailed prompt for pollution analysis."""
        return """
        Analyze this beach image for pollution and waste. Provide a detailed assessment including:

        1. Pollution Severity Score (0-100):
           - 0-20: Minimal/No pollution
           - 21-40: Low pollution
           - 41-60: Moderate pollution
           - 61-80: High pollution
           - 81-100: Severe pollution

        2. Detailed Analysis:
           - Types of waste visible
           - Pollution density and distribution
           - Environmental impact assessment
           - Cleanup priority level

        3. Specific Observations:
           - Plastic items, bottles, wrappers
           - Organic waste, seaweed, driftwood
           - Industrial waste, fishing gear
           - Water quality indicators

        Format your response as:
        SCORE: [number]
        ANALYSIS: [detailed description]
        OBSERVATIONS: [specific items found]
        PRIORITY: [low/medium/high/critical]
        """
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response into structured data."""
        try:
            # Extract score
            score = 50  # Default score
            if "SCORE:" in response_text:
                score_line = [line for line in response_text.split('\n') if 'SCORE:' in line]
                if score_line:
                    score_text = score_line[0].split('SCORE:')[1].strip()
                    try:
                        score = int(score_text)
                        score = max(0, min(100, score))  # Clamp between 0-100
                    except ValueError:
                        pass
            
            # Extract analysis
            analysis = "AI analysis completed successfully."
            if "ANALYSIS:" in response_text:
                analysis_lines = []
                in_analysis = False
                for line in response_text.split('\n'):
                    if 'ANALYSIS:' in line:
                        in_analysis = True
                        analysis_lines.append(line.split('ANALYSIS:')[1].strip())
                    elif in_analysis and line.strip() and not line.startswith(('OBSERVATIONS:', 'PRIORITY:')):
                        analysis_lines.append(line.strip())
                    elif line.startswith(('OBSERVATIONS:', 'PRIORITY:')):
                        break
                if analysis_lines:
                    analysis = ' '.join(analysis_lines)
            
            # Calculate confidence based on response quality
            confidence = min(0.95, max(0.7, len(response_text) / 1000))
            
            return {
                "score": score,
                "analysis": analysis,
                "confidence": confidence,
                "source": "Gemini AI"
            }
            
        except Exception as e:
            print(f"❌ Error parsing AI response: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when AI is unavailable."""
        return {
            "score": Config.DEFAULT_ANALYSIS_SCORE,
            "analysis": Config.DEFAULT_ANALYSIS_TEXT,
            "confidence": 0.5,
            "source": "Fallback System"
        }
    
    @staticmethod
    def calculate_points(score: int) -> int:
        """
        Calculate points based on pollution severity score.
        Higher scores (more pollution) = more points (more urgent)
        """
        if score < 30:
            return 5
        elif score < 50:
            return 10
        elif score < 70:
            return 15
        elif score < 90:
            return 20
        else:
            return 25
    
    @staticmethod
    def get_severity_level(score: int) -> str:
        """Get human-readable severity level."""
        if score < 30:
            return "Low"
        elif score < 50:
            return "Moderate"
        elif score < 70:
            return "High"
        elif score < 90:
            return "Very High"
        else:
            return "Critical"
    
    @staticmethod
    def get_color_class(score: int) -> str:
        """Get CSS color class for severity display."""
        if score < 30:
            return "success"
        elif score < 50:
            return "warning"
        elif score < 70:
            return "danger"
        elif score < 90:
            return "danger"
        else:
            return "critical"

class LocationUtils:
    """Utility class for location-related operations."""
    
    @staticmethod
    def reverse_geocode(lat: str, lon: str) -> str:
        """
        Mock reverse geocoding function.
        Replace with actual geocoding API (Google Maps, OpenStreetMap, etc.)
        """
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            
            # Mock location names based on coordinates
            # In production, use a real geocoding service
            if 12.5 <= lat_float <= 13.0 and 74.5 <= lon_float <= 75.5:
                return "Mangalore Coastal Area"
            elif 12.9 <= lat_float <= 13.1 and 74.8 <= lon_float <= 75.0:
                return "Panambur Beach"
            else:
                return f"Location near ({lat}, {lon})"
        except ValueError:
            return "Unknown Location"
    
    @staticmethod
    def validate_coordinates(lat: str, lon: str) -> Tuple[bool, str]:
        """Validate latitude and longitude coordinates."""
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            
            if not (-90 <= lat_float <= 90):
                return False, "Latitude must be between -90 and 90"
            
            if not (-180 <= lon_float <= 180):
                return False, "Longitude must be between -180 and 180"
            
            return True, "Valid coordinates"
        except ValueError:
            return False, "Invalid coordinate format"

def analyze_cleanup_verification(image_path: str) -> Dict[str, Any]:
    """
    Analyze cleanup verification images to determine if area is properly cleaned.
    Returns a score where lower scores indicate better cleanup.
    """
    try:
        # Initialize the analyzer
        analyzer = PollutionAnalyzer()
        
        if not analyzer.is_available:
            return _fallback_cleanup_analysis()
        
        # Load and prepare image
        image = analyzer._load_image(image_path)
        if not image:
            return _fallback_cleanup_analysis()
        
        # Create cleanup verification prompt
        prompt = """
        Analyze this image to assess if a beach/coastal area has been properly cleaned up.
        Focus on detecting any remaining pollution, waste, or debris.
        
        Provide a CLEANUP SCORE (0-100) where:
        - 0-20: Excellent cleanup - area is very clean
        - 21-40: Good cleanup - minor debris remaining
        - 41-60: Fair cleanup - some pollution still visible
        - 61-80: Poor cleanup - significant pollution remains
        - 81-100: Failed cleanup - area still heavily polluted
        
        Also provide:
        1. Detailed assessment of remaining pollution
        2. Types of waste still visible
        3. Cleanup quality rating
        4. Recommendations for further action
        
        Format your response as JSON with these fields:
        {
            "score": <cleanup_score>,
            "analysis": "<detailed_analysis>",
            "cleanup_quality": "<excellent/good/fair/poor/failed>",
            "remaining_pollution": "<description>",
            "recommendations": "<what_to_do_next>"
        }
        """
        
        # Get AI analysis
        response = analyzer.model.generate_content([prompt, image])
        
        # Parse response
        try:
            import json
            # Try to extract JSON from response
            response_text = response.text
            # Look for JSON content between curly braces
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Ensure required fields exist
                if 'score' not in result:
                    result['score'] = 50  # Default score
                if 'analysis' not in result:
                    result['analysis'] = "Analysis completed but details unavailable"
                
                return result
            else:
                # Fallback parsing
                return _parse_cleanup_response(response_text)
                
        except json.JSONDecodeError:
            # Fallback parsing if JSON parsing fails
            return _parse_cleanup_response(response.text)
            
    except Exception as e:
        print(f"❌ Error in cleanup verification analysis: {e}")
        return _fallback_cleanup_analysis()

def _fallback_cleanup_analysis() -> Dict[str, Any]:
    """Fallback analysis when AI is unavailable for cleanup verification."""
    return {
        "score": 45,  # Moderate score indicating some cleanup needed
        "analysis": "Fallback analysis: Unable to determine cleanup quality. Manual verification recommended.",
        "cleanup_quality": "fair",
        "remaining_pollution": "Unknown - manual verification required",
        "recommendations": "Submit photos for manual review or retry AI analysis"
    }

def _parse_cleanup_response(response_text: str) -> Dict[str, Any]:
    """Parse cleanup verification response when JSON parsing fails."""
    # Extract score if present
    score = 50  # Default score
    
    # Look for score patterns in text
    import re
    score_match = re.search(r'(\d+)(?:\s*[-/]\s*100)?', response_text)
    if score_match:
        try:
            score = int(score_match.group(1))
            if score > 100:
                score = 100
        except ValueError:
            pass
    
    # Determine cleanup quality based on score
    if score <= 20:
        quality = "excellent"
    elif score <= 40:
        quality = "good"
    elif score <= 60:
        quality = "fair"
    elif score <= 80:
        quality = "poor"
    else:
        quality = "failed"
    
    return {
        "score": score,
        "analysis": response_text[:500] + "..." if len(response_text) > 500 else response_text,
        "cleanup_quality": quality,
        "remaining_pollution": "Analysis completed but specific details unavailable",
        "recommendations": "Review the analysis text for detailed recommendations"
    } 