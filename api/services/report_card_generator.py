"""
Enhanced Report Card Generator with Passport Photos
Generates print-ready report cards with student photos
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import List, Dict, Optional
from datetime import datetime

class ReportCardGenerator:
    """Generate professional report cards with student photos"""
    
    def __init__(self):
        # A4 size at 300 DPI
        self.width = 2480
        self.height = 3508
        
        self.primary_color = (30, 64, 175)
        self.header_color = (30, 64, 175)
        self.grade_a = (21, 128, 61)  # Green
        self.grade_c = (234, 179, 8)  # Yellow
        self.grade_f = (220, 38, 38)  # Red
    
    def generate_report_card(
        self,
        student_name: str,
        student_id: str,
        class_name: str,
        term: str,
        year: str,
        subjects: List[Dict],  # [{"name": "Math", "score": 85, "grade": "A", "remarks": "Excellent"}]
        school_name: str,
        school_address: str,
        photo_bytes: Optional[bytes] = None,
        school_logo: Optional[bytes] = None,
        head_teacher_signature: Optional[bytes] = None,
        class_teacher: Optional[str] = None
    ) -> bytes:
        """Generate full report card with photo"""
        
        card = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(card)
        
        # Header section
        header_height = 400
        draw.rectangle(
            [(0, 0), (self.width, header_height)],
            fill=self.header_color
        )
        
        # School name
        draw.text(
            (self.width // 2, 100),
            school_name,
            fill='white',
            anchor='mm',
            font=self._get_font(72, bold=True)
        )
        
        draw.text(
            (self.width // 2, 180),
            school_address,
            fill='white',
            anchor='mm',
            font=self._get_font(32)
        )
        
        draw.text(
            (self.width // 2, 250),
            "STUDENT REPORT CARD",
            fill='white',
            anchor='mm',
            font=self._get_font(48, bold=True)
        )
        
        draw.text(
            (self.width // 2, 330),
            f"{term} Term {year}",
            fill='white',
            anchor='mm',
            font=self._get_font(36)
        )
        
        # Student information section
        info_y = 500
        
        # Student photo (passport size)
        photo_x = 150
        if photo_bytes:
            photo = Image.open(BytesIO(photo_bytes))
            # Resize to passport photo size
            photo = photo.resize((400, 500))
            card.paste(photo, (photo_x, info_y))
            
            # Add border around photo
            draw.rectangle(
                [(photo_x - 5, info_y - 5), 
                 (photo_x + 405, info_y + 505)],
                outline=self.primary_color,
                width=5
            )
        else:
            # Placeholder
            draw.rectangle(
                [(photo_x, info_y), (photo_x + 400, info_y + 500)],
                fill=(240, 240, 240),
                outline=self.primary_color,
                width=3
            )
        
        # Student details next to photo
        details_x = photo_x + 500
        details_y = info_y
        
        student_details = [
            ("Student Name:", student_name),
            ("Student ID:", student_id),
            ("Class:", class_name),
            ("Term:", term),
            ("Academic Year:", year),
            ("Report Date:", datetime.now().strftime("%d %B %Y"))
        ]
        
        for i, (label, value) in enumerate(student_details):
            y = details_y + (i * 80)
            
            draw.text(
                (details_x, y),
                label,
                fill='black',
                font=self._get_font(28, bold=True)
            )
            
            draw.text(
                (details_x, y + 40),
                str(value),
                fill=self.primary_color,
                font=self._get_font(32)
            )
        
        # Subjects table
        table_y = info_y + 600
        table_x = 100
        
        # Table header
        draw.text(
            (self.width // 2, table_y),
            "ACADEMIC PERFORMANCE",
            fill='black',
            anchor='mm',
            font=self._get_font(40, bold=True)
        )
        
        table_y += 100
        
        # Table headers
        headers = ["Subject", "Score", "Grade", "Remarks"]
        col_widths = [800, 400, 300, 700]
        header_x = table_x
        
        # Header background
        draw.rectangle(
            [(table_x, table_y), (self.width - 100, table_y + 80)],
            fill=self.primary_color
        )
        
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            draw.text(
                (header_x + width // 2, table_y + 40),
                header,
                fill='white',
                anchor='mm',
                font=self._get_font(32, bold=True)
            )
            header_x += width
        
        # Table rows
        row_y = table_y + 80
        row_height = 70
        
        total_score = 0
        for i, subject in enumerate(subjects):
            # Alternate row colors
            if i % 2 == 0:
                draw.rectangle(
                    [(table_x, row_y), (self.width - 100, row_y + row_height)],
                    fill=(249, 250, 251)
                )
            
            # Grade color
            grade = subject.get('grade', 'F')
            grade_color = self._get_grade_color(grade)
            
            # Subject name
            draw.text(
                (table_x + 20, row_y + row_height // 2),
                subject['name'],
                fill='black',
                anchor='lm',
                font=self._get_font(28)
            )
            
            # Score
            score = subject.get('score', 0)
            total_score += score
            draw.text(
                (table_x + col_widths[0] + col_widths[1] // 2, row_y + row_height // 2),
                str(score),
                fill='black',
                anchor='mm',
                font=self._get_font(28, bold=True)
            )
            
            # Grade
            draw.text(
                (table_x + col_widths[0] + col_widths[1] + col_widths[2] // 2, row_y + row_height // 2),
                grade,
                fill=grade_color,
                anchor='mm',
                font=self._get_font(32, bold=True)
            )
            
            # Remarks
            draw.text(
                (table_x + col_widths[0] + col_widths[1] + col_widths[2] + 20, row_y + row_height // 2),
                subject.get('remarks', ''),
                fill='black',
                anchor='lm',
                font=self._get_font(24)
            )
            
            row_y += row_height
        
        # Summary
        summary_y = row_y + 50
        
        # Total/Average
        avg_score = total_score / len(subjects) if subjects else 0
        avg_grade = self._score_to_grade(avg_score)
        
        draw.rectangle(
            [(table_x, summary_y), (self.width - 100, summary_y + 100)],
            fill=(254, 243, 199)
        )
        
        draw.text(
            (table_x + 400, summary_y + 50),
            f"OVERALL AVERAGE: {avg_score:.1f}% ({avg_grade})",
            fill='black',
            anchor='mm',
            font=self._get_font(36, bold=True)
        )
        
        # Teacher's comments
        comments_y = summary_y + 200
        
        draw.text(
            (table_x, comments_y),
            "CLASS TEACHER'S REMARKS:",
            fill='black',
            font=self._get_font(32, bold=True)
        )
        
        # Comment box
        draw.rectangle(
            [(table_x, comments_y + 60), (self.width - 100, comments_y + 260)],
            outline=self.primary_color,
            width=3
        )
        
        # Signature section
        sig_y = self.height - 400
        
        # Border
        draw.rectangle(
            [(100, sig_y - 50), (self.width - 100, sig_y + 250)],
            outline=self.primary_color,
            width=2
        )
        
        # Signatures
        sig_spacing = (self.width - 200) // 2
        
        # Class teacher
        if class_teacher:
            draw.text(
                (300, sig_y),
                class_teacher,
                fill=self.primary_color,
                font=self._get_font(24)
            )
        
        draw.line([(200, sig_y + 80), (sig_spacing - 100, sig_y + 80)], fill='black', width=2)
        draw.text(
            ((200 + sig_spacing - 100) // 2, sig_y + 100),
            "Class Teacher",
            fill='black',
            anchor='mm',
            font=self._get_font(20)
        )
        
        # Head teacher
        draw.line([(sig_spacing + 200, sig_y + 80), (self.width - 300, sig_y + 80)], fill='black', width=2)
        draw.text(
            ((sig_spacing + 200 + self.width - 300) // 2, sig_y + 100),
            "Head Teacher",
            fill='black',
            anchor='mm',
            font=self._get_font(20)
        )
        
        # Footer
        draw.text(
            (self.width // 2, self.height - 80),
            "This is an official document • Any alterations will render it invalid",
            fill=self.primary_color,
            anchor='mm',
            font=self._get_font(24)
        )
        
        # Generate number
        draw.text(
            (self.width // 2, self.height - 40),
            f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')} • Doc#RC{datetime.now().strftime('%Y%m%d%H%M%S')}",
            fill='gray',
            anchor='mm',
            font=self._get_font(18)
        )
        
        # Convert to high-quality, print-ready image
        buffer = BytesIO()
        card.save(buffer, format='PNG', quality=100, dpi=(300, 300))
        return buffer.getvalue()
    
    def _get_grade_color(self, grade: str):
        """Get color for grade"""
        if grade in ['A', 'A+', 'A-']:
            return self.grade_a
        elif grade in ['B', 'B+', 'B-', 'C', 'C+']:
            return self.grade_c
        else:
            return self.grade_f
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _get_font(self, size: int, bold: bool = False):
        """Get font"""
        try:
            font_path = "fonts/Arial-Bold.ttf" if bold else "fonts/Arial.ttf"
            return ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default()


# Singleton
_report_generator = None

def get_report_card_generator() -> ReportCardGenerator:
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportCardGenerator()
    return _report_generator
