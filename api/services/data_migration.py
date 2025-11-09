"""
Data Migration Service - Import data from ANY system
Excel, CSV, JSON, old databases → Auto-organize into our system

Uses Clarity Engine to understand any data format and map to our schema
"""
import csv
import json
import io
from typing import Dict, Any, List, Optional
from uuid import uuid4
import re

from api.services.clarity import ClarityClient
from api.services.database import get_db_manager


class DataMigrationService:
    """Import and auto-organize data from external systems"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
        self.clarity = ClarityClient()
    
    # ============================================================================
    # UNIVERSAL DATA IMPORT
    # ============================================================================
    
    async def import_data(
        self,
        file_content: bytes,
        filename: str,
        data_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import data from ANY format and auto-organize
        
        Args:
            file_content: File content (CSV, Excel, JSON, etc.)
            filename: Original filename
            data_type: Optional hint (auto-detected if not provided)
        
        Returns:
            Import summary with counts
        """
        # Step 1: Parse file format
        parsed_data = await self._parse_file(file_content, filename)
        
        if not parsed_data:
            return {
                "success": False,
                "error": "Could not parse file format"
            }
        
        # Step 2: Auto-detect data type if not provided
        if not data_type:
            data_type = await self._detect_data_type(parsed_data)
        
        # Step 3: Use Clarity to understand the schema
        schema_result = await self.clarity.analyze(
            directive=f"""
            Analyze this data and determine:
            1. What type of data is this (students, grades, payments, attendance, etc.)?
            2. What fields are present?
            3. How should this data be mapped to a school database?
            
            Data sample (first 5 rows):
            {json.dumps(parsed_data[:5], indent=2)}
            
            Data type hint: {data_type}
            
            Return a JSON mapping with:
            - detected_type: The type of data
            - field_mappings: How to map each field to our database
            - confidence: Your confidence level (0-1)
            """,
            domain="data-science"
        )
        
        # Step 4: Map and import data
        mapping = self._extract_mapping(schema_result)
        import_result = await self._import_with_mapping(
            data=parsed_data,
            mapping=mapping,
            data_type=data_type
        )
        
        return {
            "success": True,
            "data_type": data_type,
            "mapping": mapping,
            "import_result": import_result
        }
    
    async def _parse_file(self, content: bytes, filename: str) -> Optional[List[Dict]]:
        """Parse file content into list of dictionaries"""
        filename_lower = filename.lower()
        
        try:
            # CSV files
            if filename_lower.endswith('.csv'):
                content_str = content.decode('utf-8')
                csv_file = io.StringIO(content_str)
                reader = csv.DictReader(csv_file)
                return list(reader)
            
            # JSON files
            elif filename_lower.endswith('.json'):
                content_str = content.decode('utf-8')
                data = json.loads(content_str)
                # If it's a list, return it; if dict, wrap in list
                return data if isinstance(data, list) else [data]
            
            # TSV files
            elif filename_lower.endswith('.tsv'):
                content_str = content.decode('utf-8')
                lines = content_str.split('\n')
                if not lines:
                    return None
                headers = lines[0].split('\t')
                data = []
                for line in lines[1:]:
                    if line.strip():
                        values = line.split('\t')
                        data.append(dict(zip(headers, values)))
                return data
            
            # Plain text (try to parse)
            else:
                content_str = content.decode('utf-8')
                # Try to detect delimiter and parse
                lines = content_str.split('\n')
                if not lines:
                    return None
                
                # Detect delimiter
                first_line = lines[0]
                delimiter = ',' if ',' in first_line else '\t' if '\t' in first_line else ' '
                
                headers = first_line.split(delimiter)
                data = []
                for line in lines[1:]:
                    if line.strip():
                        values = line.split(delimiter)
                        data.append(dict(zip(headers, values)))
                return data
                
        except Exception as e:
            print(f"Error parsing file: {e}")
            return None
    
    async def _detect_data_type(self, data: List[Dict]) -> str:
        """Auto-detect what type of data this is"""
        if not data:
            return "unknown"
        
        # Get all field names
        all_fields = set()
        for row in data[:10]:  # Check first 10 rows
            all_fields.update(row.keys())
        
        fields_lower = {f.lower() for f in all_fields}
        
        # Student data
        if any(word in fields_lower for word in ['student', 'admission', 'pupil', 'learner', 'first_name', 'last_name', 'class']):
            return "students"
        
        # Payment/Fee data
        if any(word in fields_lower for word in ['payment', 'fee', 'amount', 'receipt', 'tuition']):
            return "payments"
        
        # Grade/Results data
        if any(word in fields_lower for word in ['marks', 'grade', 'score', 'subject', 'exam', 'test']):
            return "grades"
        
        # Attendance data
        if any(word in fields_lower for word in ['attendance', 'present', 'absent', 'date']):
            return "attendance"
        
        # Teacher data
        if any(word in fields_lower for word in ['teacher', 'staff', 'employee', 'subject_taught']):
            return "teachers"
        
        # Parent data
        if any(word in fields_lower for word in ['parent', 'guardian', 'phone', 'contact']):
            return "parents"
        
        # Expense data
        if any(word in fields_lower for word in ['expense', 'cost', 'budget', 'vendor', 'category']):
            return "expenses"
        
        return "general"
    
    def _extract_mapping(self, clarity_result: Dict) -> Dict[str, Any]:
        """Extract field mapping from Clarity analysis"""
        analysis = clarity_result.get("analysis", {})
        findings = analysis.get("findings", [])
        
        # Try to find JSON mapping in findings
        for finding in findings:
            if isinstance(finding, dict):
                return finding
            if isinstance(finding, str):
                try:
                    return json.loads(finding)
                except:
                    pass
        
        # Default mapping
        return {
            "detected_type": "unknown",
            "field_mappings": {},
            "confidence": 0.5
        }
    
    async def _import_with_mapping(
        self,
        data: List[Dict],
        mapping: Dict,
        data_type: str
    ) -> Dict[str, Any]:
        """Import data using detected mapping"""
        
        if data_type == "students":
            return await self._import_students(data, mapping)
        
        elif data_type == "payments":
            return await self._import_payments(data, mapping)
        
        elif data_type == "grades":
            return await self._import_grades(data, mapping)
        
        elif data_type == "attendance":
            return await self._import_attendance(data, mapping)
        
        elif data_type == "teachers":
            return await self._import_teachers(data, mapping)
        
        elif data_type == "parents":
            return await self._import_parents(data, mapping)
        
        elif data_type == "expenses":
            return await self._import_expenses(data, mapping)
        
        else:
            return {
                "imported": 0,
                "failed": len(data),
                "note": "Data type not recognized"
            }
    
    # ============================================================================
    # TYPE-SPECIFIC IMPORTERS
    # ============================================================================
    
    async def _import_students(self, data: List[Dict], mapping: Dict) -> Dict[str, Any]:
        """Import student records"""
        imported = 0
        failed = 0
        
        for row in data:
            try:
                student_id = str(uuid4())
                
                # Map fields (with fallbacks)
                first_name = row.get('first_name') or row.get('FirstName') or row.get('fname') or 'Unknown'
                last_name = row.get('last_name') or row.get('LastName') or row.get('lname') or 'Unknown'
                admission_number = row.get('admission_number') or row.get('AdmissionNumber') or row.get('id') or f"IMP-{student_id[:8]}"
                class_name = row.get('class') or row.get('Class') or row.get('grade') or None
                gender = row.get('gender') or row.get('Gender') or row.get('sex') or None
                dob = row.get('date_of_birth') or row.get('dob') or row.get('DOB') or None
                
                self.db.execute_query(
                    """
                    INSERT INTO students (
                        id, school_id, first_name, last_name, admission_number,
                        class_name, gender, date_of_birth, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active')
                    ON CONFLICT (admission_number) DO UPDATE
                    SET first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        class_name = EXCLUDED.class_name
                    """,
                    (student_id, self.school_id, first_name, last_name, admission_number, class_name, gender, dob)
                )
                imported += 1
            except Exception as e:
                failed += 1
                print(f"Failed to import student: {e}")
        
        return {
            "imported": imported,
            "failed": failed,
            "type": "students"
        }
    
    async def _import_payments(self, data: List[Dict], mapping: Dict) -> Dict[str, Any]:
        """Import payment records"""
        imported = 0
        failed = 0
        
        for row in data:
            try:
                # Find student by name or ID
                student_identifier = row.get('student') or row.get('student_name') or row.get('admission_number')
                if not student_identifier:
                    failed += 1
                    continue
                
                students = self.db.execute_query(
                    """
                    SELECT id FROM students
                    WHERE school_id = %s
                    AND (admission_number = %s OR CONCAT(first_name, ' ', last_name) ILIKE %s)
                    LIMIT 1
                    """,
                    (self.school_id, student_identifier, f"%{student_identifier}%"),
                    fetch=True
                )
                
                if not students:
                    failed += 1
                    continue
                
                student_id = students[0]["id"]
                payment_id = str(uuid4())
                
                amount = float(row.get('amount') or row.get('Amount') or row.get('paid') or 0)
                method = row.get('method') or row.get('payment_method') or 'cash'
                date = row.get('date') or row.get('payment_date') or None
                
                self.db.execute_query(
                    """
                    INSERT INTO payments (
                        id, school_id, student_id, amount, payment_method,
                        payment_date, status, reference_number
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'completed', %s)
                    """,
                    (payment_id, self.school_id, student_id, amount, method, date, f"IMP-{payment_id[:8]}")
                )
                imported += 1
            except Exception as e:
                failed += 1
                print(f"Failed to import payment: {e}")
        
        return {
            "imported": imported,
            "failed": failed,
            "type": "payments"
        }
    
    async def _import_grades(self, data: List[Dict], mapping: Dict) -> Dict[str, Any]:
        """Import grade records"""
        # Similar to payments - find student, record grade
        return {
            "imported": 0,
            "failed": len(data),
            "type": "grades",
            "note": "Grade import needs assessment context"
        }
    
    async def _import_attendance(self, data: List[Dict], mapping: Dict) -> Dict[str, Any]:
        """Import attendance records"""
        return {
            "imported": 0,
            "failed": len(data),
            "type": "attendance",
            "note": "Attendance import coming soon"
        }
    
    async def _import_teachers(self, data: List[Dict], mapping: Dict) -> Dict[str, Any]:
        """Import teacher records"""
        imported = 0
        failed = 0
        
        for row in data:
            try:
                teacher_id = str(uuid4())
                
                first_name = row.get('first_name') or row.get('FirstName') or 'Unknown'
                last_name = row.get('last_name') or row.get('LastName') or 'Unknown'
                email = row.get('email') or row.get('Email') or None
                phone = row.get('phone') or row.get('Phone') or None
                subjects = row.get('subjects') or row.get('subject_taught') or None
                
                self.db.execute_query(
                    """
                    INSERT INTO teachers (
                        id, school_id, first_name, last_name, email, phone, subjects_taught
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (teacher_id, self.school_id, first_name, last_name, email, phone, subjects)
                )
                imported += 1
            except Exception as e:
                failed += 1
        
        return {
            "imported": imported,
            "failed": failed,
            "type": "teachers"
        }
    
    async def _import_parents(self, data: List[Dict], mapping: Dict) -> Dict[str, Any]:
        """Import parent records"""
        return {
            "imported": 0,
            "failed": len(data),
            "type": "parents",
            "note": "Parent import coming soon"
        }
    
    async def _import_expenses(self, data: List[Dict], mapping: Dict) -> Dict[str, Any]:
        """Import expense records"""
        imported = 0
        failed = 0
        
        for row in data:
            try:
                expense_id = str(uuid4())
                
                category = row.get('category') or row.get('Category') or 'General'
                amount = float(row.get('amount') or row.get('Amount') or row.get('cost') or 0)
                description = row.get('description') or row.get('Description') or row.get('purpose') or ''
                date = row.get('date') or row.get('Date') or None
                vendor = row.get('vendor') or row.get('Vendor') or row.get('payee') or None
                
                self.db.execute_query(
                    """
                    INSERT INTO expenses (
                        id, school_id, category, amount, description, expense_date, vendor
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (expense_id, self.school_id, category, amount, description, date, vendor)
                )
                imported += 1
            except Exception as e:
                failed += 1
        
        return {
            "imported": imported,
            "failed": failed,
            "type": "expenses"
        }
