"""
Angels AI - Document Intelligence Agent Service
RAG Master - Automated document processing with intelligent routing
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from database import *
import json
import os
import re


class DocumentIntelligenceService:
    """
    Automated document processing with OCR and intelligent routing
    Handles registration forms, fee receipts, medical forms, etc.
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.document_ops = get_document_ops()
        self.student_ops = get_student_ops()
        self.parent_ops = get_parent_ops()
        self.fee_ops = get_fee_ops()
        self.db = get_db()
    
    # ============================================
    # DOCUMENT CLASSIFICATION
    # ============================================
    
    def classify_document(self, document_text: str, document_metadata: Dict) -> str:
        """
        Classify document type using AI/keywords
        
        Returns: 'registration_form', 'fee_receipt', 'medical_form', 
                'report_card', 'parent_letter', 'staff_document', etc.
        """
        text_lower = document_text.lower()
        
        # Classification rules
        if any(word in text_lower for word in ['registration', 'admission', 'enroll']):
            return 'registration_form'
        
        elif any(word in text_lower for word in ['receipt', 'payment', 'mpesa', 'transaction']):
            return 'fee_receipt'
        
        elif any(word in text_lower for word in ['medical', 'health', 'doctor', 'hospital']):
            return 'medical_form'
        
        elif any(word in text_lower for word in ['report card', 'grades', 'academic performance']):
            return 'report_card'
        
        elif any(word in text_lower for word in ['leave', 'absence', 'sick']):
            return 'absence_letter'
        
        elif any(word in text_lower for word in ['discipline', 'incident', 'behavior']):
            return 'disciplinary_report'
        
        else:
            return 'general_document'
    
    # ============================================
    # DOCUMENT PROCESSING PIPELINE
    # ============================================
    
    def process_document(self, file_path: str, uploaded_by: str,
                        student_id: Optional[str] = None,
                        parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete document processing pipeline:
        1. OCR extraction
        2. Document classification
        3. Data extraction
        4. Intelligent routing
        5. Database updates
        """
        try:
            # Step 1: Perform OCR
            ocr_result = self._perform_ocr(file_path)
            
            if not ocr_result['success']:
                return {
                    'success': False,
                    'error': 'OCR failed',
                    'details': ocr_result.get('error')
                }
            
            # Step 2: Classify document
            doc_type = self.classify_document(
                ocr_result['text'],
                {'filename': os.path.basename(file_path)}
            )
            
            # Step 3: Extract structured data
            extracted_data = self._extract_data_by_type(
                doc_type,
                ocr_result['text']
            )
            
            # Step 4: Create document record
            document_record = self.document_ops.create_document_record({
                'school_id': self.school_id,
                'document_type': doc_type,
                'category': self._get_document_category(doc_type),
                'original_filename': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'mime_type': self._get_mime_type(file_path),
                'storage_url': file_path,  # TODO: Upload to S3/cloud storage
                'processing_status': 'processing',
                'uploaded_by': uploaded_by,
                'student_id': student_id,
                'parent_id': parent_id
            })
            
            # Step 5: Route document to appropriate system
            routing_result = self._route_document(
                doc_type,
                extracted_data,
                document_record['id']
            )
            
            # Step 6: Update document record with processing results
            self.document_ops.update_document_processing(
                document_id=document_record['id'],
                ocr_text=ocr_result['text'],
                extracted_data=extracted_data,
                ocr_confidence=ocr_result['confidence'],
                routed_to=routing_result['routed_to']
            )
            
            return {
                'success': True,
                'document_id': document_record['id'],
                'document_type': doc_type,
                'extracted_data': extracted_data,
                'routing': routing_result,
                'confidence': ocr_result['confidence']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================
    # OCR PROCESSING
    # ============================================
    
    def _perform_ocr(self, file_path: str) -> Dict:
        """
        Perform OCR on document
        TODO: Integrate Google Cloud Vision or AWS Textract
        """
        # Placeholder implementation
        # In production, use actual OCR service
        
        try:
            # Simulate OCR
            # In reality, you would call:
            # - Google Cloud Vision API
            # - AWS Textract
            # - Azure Computer Vision
            
            return {
                'success': True,
                'text': self._mock_ocr_text(file_path),
                'confidence': 0.95,
                'language': 'en'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _mock_ocr_text(self, file_path: str) -> str:
        """Mock OCR text for testing"""
        return """
        STUDENT REGISTRATION FORM
        
        Student Name: John Kamau Mwangi
        Date of Birth: 15/03/2015
        Gender: Male
        Grade: Grade 3
        
        Parent Name: Mary Wanjiru Mwangi
        Phone: +254722345678
        Email: mary.mwangi@email.com
        Address: 123 Ngong Road, Nairobi
        """
    
    # ============================================
    # DATA EXTRACTION BY DOCUMENT TYPE
    # ============================================
    
    def _extract_data_by_type(self, doc_type: str, text: str) -> Dict:
        """Extract structured data based on document type"""
        
        if doc_type == 'registration_form':
            return self._extract_registration_data(text)
        
        elif doc_type == 'fee_receipt':
            return self._extract_fee_receipt_data(text)
        
        elif doc_type == 'medical_form':
            return self._extract_medical_data(text)
        
        elif doc_type == 'report_card':
            return self._extract_report_card_data(text)
        
        else:
            return {'raw_text': text}
    
    def _extract_registration_data(self, text: str) -> Dict:
        """Extract data from registration form"""
        data = {}
        
        # Student name
        name_match = re.search(r'student name:?\s*([^\n]+)', text, re.IGNORECASE)
        if name_match:
            data['student_name'] = name_match.group(1).strip()
        
        # Date of birth
        dob_match = re.search(r'date of birth:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        if dob_match:
            data['date_of_birth'] = dob_match.group(1).strip()
        
        # Gender
        gender_match = re.search(r'gender:?\s*(male|female)', text, re.IGNORECASE)
        if gender_match:
            data['gender'] = gender_match.group(1).strip().lower()
        
        # Grade
        grade_match = re.search(r'grade:?\s*([^\n]+)', text, re.IGNORECASE)
        if grade_match:
            data['grade'] = grade_match.group(1).strip()
        
        # Parent name
        parent_match = re.search(r'parent name:?\s*([^\n]+)', text, re.IGNORECASE)
        if parent_match:
            data['parent_name'] = parent_match.group(1).strip()
        
        # Phone
        phone_match = re.search(r'phone:?\s*(\+?\d[\d\s-]+)', text, re.IGNORECASE)
        if phone_match:
            data['parent_phone'] = phone_match.group(1).strip()
        
        # Email
        email_match = re.search(r'email:?\s*([^\s@]+@[^\s@]+\.[^\s@]+)', text, re.IGNORECASE)
        if email_match:
            data['parent_email'] = email_match.group(1).strip()
        
        # Address
        address_match = re.search(r'address:?\s*([^\n]+)', text, re.IGNORECASE)
        if address_match:
            data['address'] = address_match.group(1).strip()
        
        return data
    
    def _extract_fee_receipt_data(self, text: str) -> Dict:
        """Extract data from fee receipt"""
        data = {}
        
        # Amount
        amount_match = re.search(r'(?:amount|total|paid):?\s*(?:kes|ksh)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
        if amount_match:
            data['amount'] = float(amount_match.group(1).replace(',', ''))
        
        # Transaction ID
        trans_match = re.search(r'(?:transaction|reference|receipt):?\s*([A-Z0-9]+)', text, re.IGNORECASE)
        if trans_match:
            data['transaction_id'] = trans_match.group(1).strip()
        
        # Date
        date_match = re.search(r'date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        if date_match:
            data['payment_date'] = date_match.group(1).strip()
        
        # Admission number
        adm_match = re.search(r'admission:?\s*([A-Z0-9]+)', text, re.IGNORECASE)
        if adm_match:
            data['admission_number'] = adm_match.group(1).strip()
        
        # Payment method
        if 'mpesa' in text.lower():
            data['payment_method'] = 'mpesa'
        elif 'cash' in text.lower():
            data['payment_method'] = 'cash'
        elif 'bank' in text.lower():
            data['payment_method'] = 'bank_transfer'
        
        return data
    
    def _extract_medical_data(self, text: str) -> Dict:
        """Extract medical form data"""
        data = {}
        
        # Blood group
        blood_match = re.search(r'blood\s+(?:group|type):?\s*([ABO]+[+-]?)', text, re.IGNORECASE)
        if blood_match:
            data['blood_group'] = blood_match.group(1).strip()
        
        # Allergies
        allergy_match = re.search(r'allergies:?\s*([^\n]+)', text, re.IGNORECASE)
        if allergy_match:
            data['allergies'] = allergy_match.group(1).strip()
        
        # Medical conditions
        condition_match = re.search(r'medical\s+conditions:?\s*([^\n]+)', text, re.IGNORECASE)
        if condition_match:
            data['medical_conditions'] = condition_match.group(1).strip()
        
        return data
    
    def _extract_report_card_data(self, text: str) -> Dict:
        """Extract report card data"""
        data = {}
        
        # Student name
        name_match = re.search(r'student:?\s*([^\n]+)', text, re.IGNORECASE)
        if name_match:
            data['student_name'] = name_match.group(1).strip()
        
        # Grade/Class
        grade_match = re.search(r'(?:grade|class):?\s*([^\n]+)', text, re.IGNORECASE)
        if grade_match:
            data['grade'] = grade_match.group(1).strip()
        
        # Term
        term_match = re.search(r'term:?\s*(\d+)', text, re.IGNORECASE)
        if term_match:
            data['term'] = term_match.group(1).strip()
        
        # Average score
        avg_match = re.search(r'average:?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if avg_match:
            data['average'] = float(avg_match.group(1))
        
        return data
    
    # ============================================
    # INTELLIGENT DOCUMENT ROUTING
    # ============================================
    
    def _route_document(self, doc_type: str, extracted_data: Dict, 
                       document_id: str) -> Dict:
        """
        Intelligently route document data to appropriate systems
        This is the AUTOMATION magic - no manual intervention!
        """
        routing_results = {
            'routed_to': [],
            'actions_taken': [],
            'success': True
        }
        
        try:
            if doc_type == 'registration_form':
                # Route to Academic Records system
                result = self._route_to_academic_records(extracted_data)
                routing_results['routed_to'].append('academic_records')
                routing_results['actions_taken'].append(result)
            
            elif doc_type == 'fee_receipt':
                # Route to Finance system
                result = self._route_to_finance_system(extracted_data)
                routing_results['routed_to'].append('finance_system')
                routing_results['actions_taken'].append(result)
            
            elif doc_type == 'medical_form':
                # Route to Health Records
                result = self._route_to_health_records(extracted_data)
                routing_results['routed_to'].append('health_records')
                routing_results['actions_taken'].append(result)
            
            elif doc_type == 'report_card':
                # Route to Academic Performance system
                result = self._route_to_academic_performance(extracted_data)
                routing_results['routed_to'].append('academic_performance')
                routing_results['actions_taken'].append(result)
            
            else:
                # Route to general document archive
                routing_results['routed_to'].append('document_archive')
                routing_results['actions_taken'].append('Archived for manual review')
        
        except Exception as e:
            routing_results['success'] = False
            routing_results['error'] = str(e)
        
        return routing_results
    
    def _route_to_academic_records(self, data: Dict) -> str:
        """Route registration data to create/update student record"""
        if 'student_name' in data and 'grade' in data:
            # This would trigger student creation in Executive Assistant
            return f"Student registration queued: {data.get('student_name')}"
        return "Insufficient data for student registration"
    
    def _route_to_finance_system(self, data: Dict) -> str:
        """Route payment data to update fee records"""
        if 'amount' in data and 'admission_number' in data:
            # Find student by admission number
            student = self.student_ops.get_student_by_admission_number(
                data['admission_number'],
                self.school_id
            )
            
            if student:
                # Record payment
                payment_record = self.fee_ops.record_payment({
                    'student_fee_id': None,  # Would need to look up
                    'student_id': student['id'],
                    'school_id': self.school_id,
                    'amount': data['amount'],
                    'payment_method': data.get('payment_method', 'unknown'),
                    'payment_reference': data.get('transaction_id'),
                    'phone_number': None,
                    'transaction_id': data.get('transaction_id'),
                    'notes': 'Auto-processed from receipt document',
                    'received_by': 'ai_agent'
                })
                
                return f"Payment recorded: KES {data['amount']} for {student['first_name']} {student['last_name']}"
            else:
                return f"Student not found: {data['admission_number']}"
        
        return "Insufficient data for payment processing"
    
    def _route_to_health_records(self, data: Dict) -> str:
        """Route medical data to update student health records"""
        # Update student medical information
        update_data = {}
        
        if 'blood_group' in data:
            update_data['blood_group'] = data['blood_group']
        
        if 'allergies' in data:
            update_data['allergies'] = data['allergies']
        
        if 'medical_conditions' in data:
            update_data['medical_conditions'] = data['medical_conditions']
        
        if update_data:
            return f"Health records update queued: {len(update_data)} fields"
        
        return "No health data to update"
    
    def _route_to_academic_performance(self, data: Dict) -> str:
        """Route report card data to academic system"""
        if 'student_name' in data and 'average' in data:
            return f"Academic performance record queued for {data['student_name']}: {data.get('average')}%"
        return "Insufficient data for academic records"
    
    # ============================================
    # BATCH DOCUMENT PROCESSING
    # ============================================
    
    def process_batch_documents(self, file_paths: List[str], 
                                uploaded_by: str) -> Dict:
        """Process multiple documents in batch"""
        results = []
        
        for file_path in file_paths:
            result = self.process_document(file_path, uploaded_by)
            results.append({
                'file': os.path.basename(file_path),
                'result': result
            })
        
        successful = sum(1 for r in results if r['result'].get('success'))
        
        return {
            'total_processed': len(file_paths),
            'successful': successful,
            'failed': len(file_paths) - successful,
            'results': results
        }
    
    # ============================================
    # DOCUMENT SEARCH & RETRIEVAL (RAG)
    # ============================================
    
    def search_documents(self, query: str, document_type: Optional[str] = None,
                        student_id: Optional[str] = None) -> List[Dict]:
        """
        Search through processed documents using RAG
        """
        # Build search query
        sql_query = """
        SELECT * FROM documents
        WHERE school_id = %s
        AND processing_status = 'completed'
        AND (
            ocr_text ILIKE %s
            OR original_filename ILIKE %s
        )
        """
        
        params = [self.school_id, f"%{query}%", f"%{query}%"]
        
        if document_type:
            sql_query += " AND document_type = %s"
            params.append(document_type)
        
        if student_id:
            sql_query += " AND student_id = %s"
            params.append(student_id)
        
        sql_query += " ORDER BY created_at DESC LIMIT 50"
        
        results = self.db.execute_query(sql_query, tuple(params))
        return [dict(r) for r in results]
    
    def get_student_documents(self, student_id: str) -> Dict:
        """Get all documents for a student, organized by type"""
        query = """
        SELECT * FROM documents
        WHERE student_id = %s
        AND school_id = %s
        AND deleted_at IS NULL
        ORDER BY created_at DESC
        """
        
        docs = self.db.execute_query(query, (student_id, self.school_id))
        
        # Organize by type
        organized = {}
        for doc in docs:
            doc_type = doc['document_type']
            if doc_type not in organized:
                organized[doc_type] = []
            organized[doc_type].append(dict(doc))
        
        return organized
    
    # ============================================
    # HELPER FUNCTIONS
    # ============================================
    
    def _get_document_category(self, doc_type: str) -> str:
        """Get document category from type"""
        category_mapping = {
            'registration_form': 'academic',
            'fee_receipt': 'financial',
            'medical_form': 'health',
            'report_card': 'academic',
            'absence_letter': 'administrative',
            'disciplinary_report': 'administrative',
            'general_document': 'general'
        }
        return category_mapping.get(doc_type, 'general')
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        return mime_types.get(ext, 'application/octet-stream')


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def process_document(school_id: str, file_path: str, uploaded_by: str,
                    student_id: Optional[str] = None) -> Dict:
    """Quick function to process a document"""
    service = DocumentIntelligenceService(school_id)
    return service.process_document(file_path, uploaded_by, student_id)

def search_documents(school_id: str, query: str, doc_type: Optional[str] = None) -> List[Dict]:
    """Quick function to search documents"""
    service = DocumentIntelligenceService(school_id)
    return service.search_documents(query, doc_type)

def get_student_documents(school_id: str, student_id: str) -> Dict:
    """Quick function to get all student documents"""
    service = DocumentIntelligenceService(school_id)
    return service.get_student_documents(student_id)
