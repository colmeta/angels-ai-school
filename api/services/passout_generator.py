"""
Pass-Out Slip Generator
Generates printable pass-out slips for students leaving school premises
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from typing import Optional

class PassOutGenerator:
    """Generate pass-out slips for students"""
    
    def __init__(self):
        # A5 size at 300 DPI (half of A4)
        self.width = 1754
        self.height = 1240
        
        self.primary_color = (30, 64, 175)
        self.danger_color = (220, 38, 38)
        self.success_color = (21, 128, 61)
    
    def generate_pass_out_slip(
        self,
        student_name: str,
        student_id: str,
        class_name: str,
        reason: str,
        departure_time: str,
        expected_return: Optional[str],
        authorized_by: str,
        school_name: str,
        photo_bytes: Optional[bytes] = None,
        parent_phone: Optional[str] = None
    ) -> bytes:
        """Generate pass-out slip"""
        
        slip = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(slip)
        
        # Border
        border_width = 10
        draw.rectangle(
            [(border_width, border_width), 
             (self.width - border_width, self.height - border_width)],
            outline=self.primary_color,
            width=border_width
        )
        
        # Header
        header_height = 200
        draw.rectangle(
            [(border_width, border_width), 
             (self.width - border_width, header_height)],
            fill=self.primary_color
        )
        
        # School name
        draw.text(
            (self.width // 2, 70),
            school_name,
            fill='white',
            anchor='mm',
            font=self._get_font(48, bold=True)
        )
        
        draw.text(
            (self.width // 2, 140),
            "STUDENT PASS-OUT SLIP",
            fill='white',
            anchor='mm',
            font=self._get_font(32, bold=True)
        )
        
        # Student photo (small)
        photo_x = 100
        photo_y = 250
        
        if photo_bytes:
            photo = Image.open(BytesIO(photo_bytes))
            photo = photo.resize((200, 240))
            slip.paste(photo, (photo_x, photo_y))
        else:
            draw.rectangle(
                [(photo_x, photo_y), (photo_x + 200, photo_y + 240)],
                outline=self.primary_color,
                width=3
            )
        
        # Information section
        info_x = 350
        info_y = 250
        line_height = 80
        
        # Date/Time stamp
        now = datetime.now()
        draw.text(
            (self.width - 100, 230),
            f"Issued: {now.strftime('%d/%m/%Y %H:%M')}",
            fill=self.primary_color,
            anchor='rm',
            font=self._get_font(20)
        )
        
        # Student details
        details = [
            ("Student Name:", student_name, self.primary_color),
            ("Student ID:", student_id, self.primary_color),
            ("Class:", class_name, self.primary_color),
            ("Reason:", reason, self.danger_color),
            ("Departure Time:", departure_time, self.success_color),
            ("Expected Return:", expected_return or "Same Day", self.danger_color),
            ("Parent Contact:", parent_phone or "N/A", self.primary_color),
            ("Authorized By:", authorized_by, self.success_color),
        ]
        
        for i, (label, value, color) in enumerate(details):
            y = info_y + (i * line_height)
            
            # Label
            draw.text(
                (info_x, y),
                label,
                fill='black',
                font=self._get_font(24, bold=True)
            )
            
            # Value
            draw.text(
                (info_x, y + 35),
                str(value),
                fill=color,
                font=self._get_font(28)
            )
        
        # Important notice
        notice_y = self.height - 300
        draw.rectangle(
            [(50, notice_y), (self.width - 50, notice_y + 150)],
            fill=(254, 243, 199),  # Yellow background
            outline=self.danger_color,
            width=3
        )
        
        draw.text(
            (self.width // 2, notice_y + 30),
            "⚠️ IMPORTANT",
            fill=self.danger_color,
            anchor='mm',
            font=self._get_font(28, bold=True)
        )
        
        draw.text(
            (self.width // 2, notice_y + 75),
            "This slip must be presented to the gate security upon return",
            fill=self.danger_color,
            anchor='mm',
            font=self._get_font(22)
        )
        
        draw.text(
            (self.width // 2, notice_y + 110),
            "Valid for ONE exit only • Not transferable",
            fill=self.danger_color,
            anchor='mm',
            font=self._get_font(20)
        )
        
        # Signatures section
        sig_y = self.height - 120
        
        draw.line([(100, sig_y), (500, sig_y)], fill='black', width=2)
        draw.text((300, sig_y + 10), "Parent/Guardian", fill='black', anchor='mm', font=self._get_font(18))
        
        draw.line([(self.width - 500, sig_y), (self.width - 100, sig_y)], fill='black', width=2)
        draw.text((self.width - 300, sig_y + 10), "Security/Gate", fill='black', anchor='mm', font=self._get_font(18))
        
        # Barcode/Reference number
        ref_number = f"PO-{now.strftime('%Y%m%d%H%M%S')}"
        draw.text(
            (self.width // 2, self.height - 40),
            f"Reference: {ref_number}",
            fill=self.primary_color,
            anchor='mm',
            font=self._get_font(16, bold=True)
        )
        
        # Convert to high-quality PDF-ready image
        buffer = BytesIO()
        slip.save(buffer, format='PNG', quality=100, dpi=(300, 300))
        return buffer.getvalue()
    
    def _get_font(self, size: int, bold: bool = False):
        """Get font"""
        try:
            font_path = "fonts/Arial-Bold.ttf" if bold else "fonts/Arial.ttf"
            return ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default()


# Singleton
_passout_generator = None

def get_passout_generator() -> PassOutGenerator:
    global _passout_generator
    if _passout_generator is None:
        _passout_generator = PassOutGenerator()
    return _passout_generator
