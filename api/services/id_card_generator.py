"""
ID Card Generator
Generates professional student and staff ID cards
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Optional
from datetime import datetime

class IDCardGenerator:
    """Generate professional ID cards for students and staff"""
    
    def __init__(self):
        # Standard ID card size (CR80 - credit card size: 85.6mm x 53.98mm at 300 DPI)
        self.card_width = 1011  # pixels at 300 DPI
        self.card_height = 638
        
        # Colors
        self.primary_color = (30, 64, 175)  # Blue
        self.secondary_color = (249, 250, 251)  # Light gray
        self.text_color = (17, 24, 39)  # Dark gray
    
    def generate_student_id(
        self,
        student_name: str,
        student_id: str,
        class_name: str,
        school_name: str,
        photo_bytes: Optional[bytes] = None,
        school_logo: Optional[bytes] = None,
        valid_until: Optional[str] = None
    ) -> bytes:
        """Generate student ID card"""
        
        # Create card background
        card = Image.new('RGB', (self.card_width, self.card_height), 'white')
        draw = ImageDraw.Draw(card)
        
        # Header bar (school branding)
        draw.rectangle(
            [(0, 0), (self.card_width, 120)],
            fill=self.primary_color
        )
        
        # School name (would use custom font in production)
        school_name_pos = (self.card_width // 2, 30)
        draw.text(
            school_name_pos,
            school_name,
            fill='white',
            anchor='mm',
            font=self._get_font(32, bold=True)
        )
        
        draw.text(
            (self.card_width // 2, 75),
            "STUDENT ID CARD",
            fill='white',
            anchor='mm',
            font=self._get_font(20)
        )
        
        # Photo section
        if photo_bytes:
            photo = Image.open(BytesIO(photo_bytes))
            photo = photo.resize((250, 300))
            card.paste(photo, (50, 150))
        else:
            # Placeholder
            draw.rectangle(
                [(50, 150), (300, 450)],
                fill=self.secondary_color,
                outline=self.text_color,
                width=2
            )
            draw.text(
                (175, 300),
                "No Photo",
                fill=self.text_color,
                anchor='mm',
                font=self._get_font(16)
            )
        
        # Student information
        info_x = 350
        info_start_y = 180
        line_height = 60
        
        info_fields = [
            ("Name:", student_name),
            ("ID:", student_id),
            ("Class:", class_name),
            ("Valid Until:", valid_until or datetime.now().year + 1)
        ]
        
        for i, (label, value) in enumerate(info_fields):
            y = info_start_y + (i * line_height)
            
            # Label
            draw.text(
                (info_x, y),
                label,
                fill=self.text_color,
                font=self._get_font(18, bold=True)
            )
            
            # Value
            draw.text(
                (info_x, y + 25),
                str(value),
                fill=self.primary_color,
                font=self._get_font(20)
            )
        
        # QR Code placeholder (would use actual QR code library)
        qr_size = 120
        qr_x = self.card_width - qr_size - 50
        qr_y = self.card_height - qr_size - 30
        
        draw.rectangle(
            [(qr_x, qr_y), (qr_x + qr_size, qr_y + qr_size)],
            fill=self.secondary_color,
            outline=self.text_color,
            width=2
        )
        
        draw.text(
            (qr_x + qr_size//2, qr_y + qr_size//2),
            "QR\nCODE",
            fill=self. text_color,
            anchor='mm',
            align='center',
            font=self._get_font(14)
        )
        
        # Footer
        draw.text(
            (self.card_width // 2, self.card_height - 20),
            "This card remains property of the school",
            fill=self.text_color,
            anchor='mm',
            font=self._get_font(12)
        )
        
        # Convert to bytes
        buffer = BytesIO()
        card.save(buffer, format='PNG', quality=100, dpi=(300, 300))
        return buffer.getvalue()
    
    def generate_staff_id(
        self,
        staff_name: str,
        staff_id: str,
        position: str,
        department: str,
        school_name: str,
        photo_bytes: Optional[bytes] = None,
        valid_until: Optional[str] = None
    ) -> bytes:
        """Generate staff ID card (similar to student but different color scheme)"""
        
        # Use green color for staff
        staff_color = (21, 128, 61)
        
        card = Image.new('RGB', (self.card_width, self.card_height), 'white')
        draw = ImageDraw.Draw(card)
        
        # Header
        draw.rectangle([(0, 0), (self.card_width, 120)], fill=staff_color)
        
        draw.text(
            (self.card_width // 2, 30),
            school_name,
            fill='white',
            anchor='mm',
            font=self._get_font(32, bold=True)
        )
        
        draw.text(
            (self.card_width // 2, 75),
            "STAFF ID CARD",
            fill='white',
            anchor='mm',
            font=self._get_font(20)
        )
        
        # Photo
        if photo_bytes:
            photo = Image.open(BytesIO(photo_bytes))
            photo = photo.resize((250, 300))
            card.paste(photo, (50, 150))
        else:
            draw.rectangle(
                [(50, 150), (300, 450)],
                fill=self.secondary_color,
                outline=self.text_color,
                width=2
            )
        
        # Staff info
        info_x = 350
        info_start_y = 180
        line_height = 60
        
        info_fields = [
            ("Name:", staff_name),
            ("ID:", staff_id),
            ("Position:", position),
            ("Department:", department),
            ("Valid Until:", valid_until or datetime.now().year + 1)
        ]
        
        for i, (label, value) in enumerate(info_fields):
            y = info_start_y + (i * line_height)
            draw.text((info_x, y), label, fill=self.text_color, font=self._get_font(18, bold=True))
            draw.text((info_x, y + 25), str(value), fill=staff_color, font=self._get_font(20))
        
        # Footer
        draw.text(
            (self.card_width // 2, self.card_height - 20),
            "This card remains property of the school  •  Not transferable",
            fill=self.text_color,
            anchor='mm',
            font=self._get_font(12)
        )
        
        buffer = BytesIO()
        card.save(buffer, format='PNG', quality=100, dpi=(300, 300))
        return buffer.getvalue()
    
    def _get_font(self, size: int, bold: bool = False):
        """Get font (uses default for now, can be customized)"""
        try:
            # Try to load custom font
            font_path = "fonts/Arial-Bold.ttf" if bold else "fonts/Arial.ttf"
            return ImageFont.truetype(font_path, size)
        except:
            # Fallback to default
            return ImageFont.load_default()


# Singleton
_id_generator = None

def get_id_card_generator() -> IDCardGenerator:
    global _id_generator
    if _id_generator is None:
        _id_generator = IDCardGenerator()
    return _id_generator
