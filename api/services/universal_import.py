"""
Universal Import Service - The "Zero Friction" Onboarding Tool

This service intelligently maps ANY Excel/CSV format to our database schema.
It uses fuzzy matching and AI heuristics to handle weird column names.
MEMORY OPTIMIZED: Uses built-in csv module instead of pandas (saves 100MB+)
"""

import csv
import io
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import re
from difflib import SequenceMatcher

class UniversalImporter:
    """Handles messy Excel/CSV imports with intelligent column mapping"""
    
    # Standard fields we expect
    STUDENT_FIELDS = {
        'admission_number': ['admission', 'admno', 'student_id', 'reg_no', 'regno', 'id'],
        'first_name': ['first_name', 'fname', 'firstname', 'given_name', 'name'],
        'last_name': ['last_name', 'lname', 'lastname', 'surname', 'family_name'],
        'date_of_birth': ['dob', 'birth_date', 'birthdate', 'date_of_birth', 'birthday'],
        'gender': ['gender', 'sex', 'male_female'],
        'class_name': ['class', 'grade', 'year', 'form', 'level'],
        'stream': ['stream', 'section', 'division', 'class_section']
    }
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def fuzzy_match_column(self, col_name: str, possible_names: List[str]) -> float:
        """Find best match for a column name"""
        col_clean = re.sub(r'[^a-z0-9]', '', col_name.lower())
        best_score = 0.0
        
        for possible in possible_names:
            possible_clean = re.sub(r'[^a-z0-9]', '', possible.lower())
            score = self.similarity(col_clean, possible_clean)
            if score > best_score:
                best_score = score
                
        return best_score
    
    def detect_column_mapping(self, headers: List[str]) -> Dict[str, str]:
        """
        Intelligently map CSV columns to our schema fields
        Returns: {our_field_name: csv_column_name}
        """
        mapping = {}
        used_columns = set()
        
        for our_field, variants in self.STUDENT_FIELDS.items():
            best_match = None
            best_score = 0.6  # Minimum confidence threshold
            
            for col in headers:
                if col in used_columns:
                    continue
                    
                score = self.fuzzy_match_column(col, variants)
                if score > best_score:
                    best_score = score
                    best_match = col
            
            if best_match:
                mapping[our_field] = best_match
                used_columns.add(best_match)
        
        return mapping
    
    def parse_csv_content(self, content: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Parse CSV content and return headers + rows
        Returns: (headers, rows_as_dicts)
        """
        reader = csv.DictReader(io.StringIO(content))
        headers = reader.fieldnames or []
        rows = list(reader)
        return headers, rows
    
    def parse_file(self, file_path: str) -> Tuple[List[str], List[Dict], Dict[str, str]]:
        """
        Read CSV file and detect schema
        Returns: (headers, rows, column_mapping)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        headers, rows = self.parse_csv_content(content)
        
        # Detect mapping
        mapping = self.detect_column_mapping(headers)
        
        return headers, rows, mapping
    
    def transform_to_students(self, rows: List[Dict], mapping: Dict[str, str]) -> List[Dict]:
        """
        Transform the rows to our student schema
        """
        students = []
        
        for row in rows:
            student = {'school_id': self.school_id}
            
            for our_field, csv_col in mapping.items():
                value = row.get(csv_col, '').strip()
                
                # Skip empty values
                if not value:
                    continue
                    
                if our_field == 'date_of_birth':
                    # Try to parse date
                    try:
                        # Try various date formats
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                            try:
                                parsed_date = datetime.strptime(value, fmt)
                                student[our_field] = parsed_date.strftime('%Y-%m-%d')
                                break
                            except ValueError:
                                continue
                    except:
                        pass  # Skip bad dates
                elif our_field == 'gender':
                    # Normalize gender
                    val_lower = value.lower()
                    if val_lower in ['m', 'male', 'boy']:
                        student[our_field] = 'male'
                    elif val_lower in ['f', 'female', 'girl']:
                        student[our_field] = 'female'
                else:
                    student[our_field] = value
            
            # Only add if we have minimum required fields
            if 'admission_number' in student and ('first_name' in student or 'last_name' in student):
                students.append(student)
        
        return students
    
    def preview_import(self, file_path: str, max_rows: int = 5) -> Dict:
        """
        Generate a preview for user confirmation
        Returns: {
            'detected_mapping': {...},
            'sample_data': [...],
            'total_rows': int,
            'confidence': float
        }
        """
        headers, rows, mapping = self.parse_file(file_path)
        students = self.transform_to_students(rows, mapping)
        
        # Calculate confidence
        confidence = len(mapping) / len(self.STUDENT_FIELDS)
        
        return {
            'detected_mapping': mapping,
            'sample_data': students[:max_rows],
            'total_rows': len(students),
            'confidence':round(confidence, 2),
            'warnings': self._generate_warnings(mapping)
        }
    
    def _generate_warnings(self, mapping: Dict) -> List[str]:
        """Generate warnings about missing fields"""
        warnings = []
        
        required = ['admission_number', 'first_name', 'last_name']
        for field in required:
            if field not in mapping:
                warnings.append(f"Missing required field: {field}")
        
        return warnings
    
    def execute_import(self, file_path: str) -> Dict:
        """
        Execute the full import
        Returns: {
            'success': bool,
            'imported_count': int,
            'errors': [...]
        }
        """
        headers, rows, mapping = self.parse_file(file_path)
        students = self.transform_to_students(rows, mapping)
        
        # Here you would insert into the database
        # For now, returning the prepared data
        
        return {
            'success': True,
            'imported_count': len(students),
            'students': students,
            'errors': []
        }
