"""
OCR Service - Real Photo Processing
Handles attendance sheets, exam results, documents, inventory, library records
"""
import base64
import io
import re
from typing import Dict, List, Any, Optional
from PIL import Image
import json

try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

from api.core.config import get_settings
from api.services.clarity import ClarityClient


class OCRService:
    """Production OCR service using Google Cloud Vision + Clarity fallback"""
    
    def __init__(self):
        self.settings = get_settings()
        self.vision_client = None
        if VISION_AVAILABLE:
            try:
                self.vision_client = vision.ImageAnnotatorClient()
            except Exception:
                pass  # Will fall back to Clarity
    
    def process_image(self, image_data: str, image_type: str = "base64") -> Dict[str, Any]:
        """
        Extract text from image using Google Vision API or Clarity fallback
        
        Args:
            image_data: Base64 encoded image or file path
            image_type: "base64" or "file"
            
        Returns:
            Dict with extracted text and confidence
        """
        try:
            if image_type == "base64":
                # Remove data URL prefix if present
                if "base64," in image_data:
                    image_data = image_data.split("base64,")[1]
                image_bytes = base64.b64decode(image_data)
            else:
                with open(image_data, 'rb') as f:
                    image_bytes = f.read()
            
            # Try Google Vision first
            if self.vision_client:
                return self._google_vision_ocr(image_bytes)
            
            # Fallback to Clarity
            return self._clarity_ocr(image_bytes)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def _google_vision_ocr(self, image_bytes: bytes) -> Dict[str, Any]:
        """Use Google Cloud Vision for OCR"""
        image = vision.Image(content=image_bytes)
        response = self.vision_client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(response.error.message)
        
        texts = response.text_annotations
        if not texts:
            return {
                "success": True,
                "text": "",
                "confidence": 0.0,
                "full_text": "",
                "words": []
            }
        
        # First annotation is full text
        full_text = texts[0].description
        confidence = texts[0].bounding_poly.vertices[0].x if texts[0].bounding_poly.vertices else 0.9
        
        # Extract individual words
        words = []
        for text in texts[1:]:  # Skip first (full text)
            words.append({
                "text": text.description,
                "confidence": 0.9,  # Vision API doesn't provide per-word confidence
                "bounds": {
                    "x": text.bounding_poly.vertices[0].x if text.bounding_poly.vertices else 0,
                    "y": text.bounding_poly.vertices[0].y if text.bounding_poly.vertices else 0
                }
            })
        
        return {
            "success": True,
            "text": full_text,
            "full_text": full_text,
            "confidence": 0.9,
            "words": words,
            "engine": "google_vision"
        }
    
    def _clarity_ocr(self, image_bytes: bytes) -> Dict[str, Any]:
        """Use Clarity as OCR fallback"""
        clarity = ClarityClient()
        try:
            # Convert to base64 for Clarity
            b64_image = base64.b64encode(image_bytes).decode()
            
            result = clarity.analyze(
                directive="Extract all text from this image. Return structured data.",
                domain="data-entry",
                files=[{
                    "filename": "document.png",
                    "data": f"data:image/png;base64,{b64_image}"
                }]
            )
            
            # Extract text from Clarity response
            text = ""
            if isinstance(result, dict):
                if "analysis" in result:
                    analysis = result["analysis"]
                    if isinstance(analysis, dict):
                        text = analysis.get("summary", "") or analysis.get("findings", [""])[0]
                    elif isinstance(analysis, str):
                        text = analysis
            
            return {
                "success": True,
                "text": text,
                "full_text": text,
                "confidence": 0.85,
                "words": [],
                "engine": "clarity"
            }
        finally:
            clarity.close()
    
    def process_attendance_sheet(self, image_data: str, class_info: Dict) -> Dict[str, Any]:
        """
        Process attendance sheet photo into structured data
        
        Args:
            image_data: Base64 image
            class_info: Dict with class_name, date, etc.
            
        Returns:
            Dict with student names and attendance status
        """
        ocr_result = self.process_image(image_data)
        
        if not ocr_result["success"]:
            return ocr_result
        
        # Use Clarity to structure the attendance data
        clarity = ClarityClient()
        try:
            structured = clarity.analyze(
                directive=f"""
                You are processing an attendance sheet for {class_info.get('class_name', 'a class')}.
                Extract student names and mark their attendance status (present, absent, late).
                Return JSON array: [{{"name": "John Doe", "status": "present"}}, ...]
                
                Extracted text:
                {ocr_result['text']}
                """,
                domain="education",
            )
            
            # Parse Clarity response into attendance records
            attendance_records = self._parse_attendance_response(structured, class_info)
            
            return {
                "success": True,
                "class_name": class_info.get('class_name'),
                "date": class_info.get('date'),
                "attendance": attendance_records,
                "ocr_confidence": ocr_result["confidence"],
                "raw_text": ocr_result["text"]
            }
        finally:
            clarity.close()
    
    def process_exam_results(self, image_data: str, exam_info: Dict) -> Dict[str, Any]:
        """
        Process exam results photo into structured data
        
        Args:
            image_data: Base64 image
            exam_info: Dict with subject, exam_name, etc.
            
        Returns:
            Dict with student names and marks
        """
        ocr_result = self.process_image(image_data)
        
        if not ocr_result["success"]:
            return ocr_result
        
        clarity = ClarityClient()
        try:
            structured = clarity.analyze(
                directive=f"""
                You are processing exam results for {exam_info.get('subject', 'a subject')}.
                Extract student names and their marks/grades.
                Return JSON array: [{{"name": "John Doe", "marks": 85, "grade": "A"}}, ...]
                
                Extracted text:
                {ocr_result['text']}
                """,
                domain="education",
            )
            
            results = self._parse_exam_results(structured, exam_info)
            
            return {
                "success": True,
                "subject": exam_info.get('subject'),
                "exam_name": exam_info.get('exam_name'),
                "results": results,
                "ocr_confidence": ocr_result["confidence"],
                "raw_text": ocr_result["text"]
            }
        finally:
            clarity.close()
    
    def process_sickbay_register(self, image_data: str, date: str) -> Dict[str, Any]:
        """Process sickbay register photo"""
        ocr_result = self.process_image(image_data)
        
        if not ocr_result["success"]:
            return ocr_result
        
        clarity = ClarityClient()
        try:
            structured = clarity.analyze(
                directive=f"""
                Extract sickbay visit records from this register.
                Return JSON: [{{"student_name": "...", "symptoms": "...", "time": "..."}}, ...]
                
                Text:
                {ocr_result['text']}
                """,
                domain="healthcare",
            )
            
            visits = self._parse_health_visits(structured, date)
            
            return {
                "success": True,
                "date": date,
                "visits": visits,
                "ocr_confidence": ocr_result["confidence"]
            }
        finally:
            clarity.close()
    
    def process_inventory_sheet(self, image_data: str, category: str) -> Dict[str, Any]:
        """Process inventory/stock sheet photo"""
        ocr_result = self.process_image(image_data)
        
        if not ocr_result["success"]:
            return ocr_result
        
        clarity = ClarityClient()
        try:
            structured = clarity.analyze(
                directive=f"""
                Extract inventory items from this sheet.
                Category: {category}
                Return JSON: [{{"item_name": "...", "quantity": 0, "location": "..."}}, ...]
                
                Text:
                {ocr_result['text']}
                """,
                domain="data-entry",
            )
            
            items = self._parse_inventory_items(structured, category)
            
            return {
                "success": True,
                "category": category,
                "items": items,
                "ocr_confidence": ocr_result["confidence"]
            }
        finally:
            clarity.close()
    
    def process_library_register(self, image_data: str) -> Dict[str, Any]:
        """Process library borrow/return register"""
        ocr_result = self.process_image(image_data)
        
        if not ocr_result["success"]:
            return ocr_result
        
        clarity = ClarityClient()
        try:
            structured = clarity.analyze(
                directive=f"""
                Extract library transactions (borrow/return).
                Return JSON: [{{"student_name": "...", "book_title": "...", "action": "borrow/return", "date": "..."}}, ...]
                
                Text:
                {ocr_result['text']}
                """,
                domain="education",
            )
            
            transactions = self._parse_library_transactions(structured)
            
            return {
                "success": True,
                "transactions": transactions,
                "ocr_confidence": ocr_result["confidence"]
            }
        finally:
            clarity.close()
    
    def _parse_attendance_response(self, response: Dict, class_info: Dict) -> List[Dict]:
        """Parse Clarity attendance response into structured records"""
        records = []
        
        # Try to extract JSON from response
        if isinstance(response, dict):
            analysis = response.get("analysis", {})
            if isinstance(analysis, dict):
                findings = analysis.get("findings", [])
                if isinstance(findings, list):
                    for item in findings:
                        if isinstance(item, dict) and "name" in item:
                            records.append({
                                "student_name": item.get("name"),
                                "status": item.get("status", "present").lower(),
                                "notes": item.get("notes", "")
                            })
                        elif isinstance(item, str):
                            # Try to parse from string
                            match = re.search(r'(\w+\s+\w+).*?(present|absent|late)', item, re.IGNORECASE)
                            if match:
                                records.append({
                                    "student_name": match.group(1).strip(),
                                    "status": match.group(2).lower(),
                                    "notes": ""
                                })
        
        return records
    
    def _parse_exam_results(self, response: Dict, exam_info: Dict) -> List[Dict]:
        """Parse exam results from Clarity response"""
        results = []
        
        if isinstance(response, dict):
            analysis = response.get("analysis", {})
            if isinstance(analysis, dict):
                findings = analysis.get("findings", [])
                for item in findings:
                    if isinstance(item, dict):
                        results.append({
                            "student_name": item.get("name", ""),
                            "marks_obtained": item.get("marks", 0),
                            "grade": item.get("grade", ""),
                            "remarks": item.get("remarks", "")
                        })
        
        return results
    
    def _parse_health_visits(self, response: Dict, date: str) -> List[Dict]:
        """Parse health visits from Clarity response"""
        visits = []
        
        if isinstance(response, dict):
            analysis = response.get("analysis", {})
            if isinstance(analysis, dict):
                findings = analysis.get("findings", [])
                for item in findings:
                    if isinstance(item, dict):
                        visits.append({
                            "student_name": item.get("student_name", ""),
                            "symptoms": item.get("symptoms", ""),
                            "visit_time": item.get("time", ""),
                            "treatment": item.get("treatment", "")
                        })
        
        return visits
    
    def _parse_inventory_items(self, response: Dict, category: str) -> List[Dict]:
        """Parse inventory items from Clarity response"""
        items = []
        
        if isinstance(response, dict):
            analysis = response.get("analysis", {})
            if isinstance(analysis, dict):
                findings = analysis.get("findings", [])
                for item in findings:
                    if isinstance(item, dict):
                        items.append({
                            "item_name": item.get("item_name", ""),
                            "quantity": item.get("quantity", 0),
                            "location": item.get("location", ""),
                            "condition": item.get("condition", "good")
                        })
        
        return items
    
    def _parse_library_transactions(self, response: Dict) -> List[Dict]:
        """Parse library transactions from Clarity response"""
        transactions = []
        
        if isinstance(response, dict):
            analysis = response.get("analysis", {})
            if isinstance(analysis, dict):
                findings = analysis.get("findings", [])
                for item in findings:
                    if isinstance(item, dict):
                        transactions.append({
                            "student_name": item.get("student_name", ""),
                            "book_title": item.get("book_title", ""),
                            "action": item.get("action", "borrow"),
                            "transaction_date": item.get("date", "")
                        })
        
        return transactions
