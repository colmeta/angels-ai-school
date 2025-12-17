"""
Universal Import Service - The "Zero Friction" Onboarding Tool

This service intelligently maps ANY Excel/CSV format to our database schema.
It uses fuzzy matching and AI heuristics to handle weird column names.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from difflib import SequenceMatcher

class UniversalImporter:
    """Handles messy Excel imports with intelligent column mapping"""
    
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
    
    def detect_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Intelligently map Excel columns to our schema fields
        Returns: {our_field_name: excel_column_name}
        """
        mapping = {}
        used_columns = set()
        
        for our_field, variants in self.STUDENT_FIELDS.items():
            best_match = None
            best_score = 0.6  # Minimum confidence threshold
            
            for col in df.columns:
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
    
    def parse_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Read Excel/CSV and detect schema
        Returns: (dataframe, column_mapping)
        """
        # Try reading as Excel first
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception:
            # Fallback to CSV
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                raise ValueError(f"Could not parse file. Supported formats: Excel (.xlsx), CSV (.csv). Error: {str(e)}")
        
        # Skip empty rows at the top (common issue)
        for i in range(len(df)):
            if df.iloc[i].notna().sum() > len(df.columns) * 0.5:  # At least 50% filled
                df = df.iloc[i:]
                df.columns = df.iloc[0]  # Use this row as header
                df = df.iloc[1:].reset_index(drop=True)
                break
        
        # Detect mapping
        mapping = self.detect_column_mapping(df)
        
        return df, mapping
    
    def transform_to_students(self, df: pd.DataFrame, mapping: Dict[str, str]) -> List[Dict]:
        """
        Transform the dataframe to our student schema
        """
        students = []
        
        for idx, row in df.iterrows():
            student = {'school_id': self.school_id}
            
            for our_field, excel_col in mapping.items():
                value = row.get(excel_col)
                
                # Clean and validate
                if pd.isna(value):
                    continue
                    
                if our_field == 'date_of_birth':
                    # Try to parse date
                    try:
                        if isinstance(value, datetime):
                            student[our_field] = value.strftime('%Y-%m-%d')
                        else:
                            student[our_field] = pd.to_datetime(value).strftime('%Y-%m-%d')
                    except:
                        pass  # Skip bad dates
                elif our_field == 'gender':
                    # Normalize gender
                    val_lower = str(value).lower()
                    if val_lower in ['m', 'male', 'boy']:
                        student[our_field] = 'male'
                    elif val_lower in ['f', 'female', 'girl']:
                        student[our_field] = 'female'
                else:
                    student[our_field] = str(value).strip()
            
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
        df, mapping = self.parse_file(file_path)
        students = self.transform_to_students(df, mapping)
        
        # Calculate confidence
        confidence = len(mapping) / len(self.STUDENT_FIELDS)
        
        return {
            'detected_mapping': mapping,
            'sample_data': students[:max_rows],
            'total_rows': len(students),
            'confidence': round(confidence, 2),
            'warnings': self._generate_warnings(mapping, df)
        }
    
    def _generate_warnings(self, mapping: Dict, df: pd.DataFrame) -> List[str]:
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
        df, mapping = self.parse_file(file_path)
        students = self.transform_to_students(df, mapping)
        
        # Here you would insert into the database
        # For now, returning the prepared data
        
        return {
            'success': True,
            'imported_count': len(students),
            'students': students,
            'errors': []
        }
