"""
Memory-Optimized Photo Service for Render 512MB Free Tier
"""
from PIL import Image
import io
from typing import Optional, Tuple
import gc

class OptimizedPhotoService:
    """Memory-optimized photo processing for 512MB RAM environments"""
    
    def __init__(self):
        # Smaller sizes to reduce memory usage
        self.passport_size = (300, 400)  # ~120KB in memory
        self.thumbnail_size = (100, 100)  # ~10KB in memory
        self.max_file_size = 2 * 1024 * 1024  # 2MB (reduced from 5MB)
        self.max_dimension = 2000  # Prevent huge images
    
    def process_passport_photo(
        self,
        image_data: bytes,
        output_format: str = 'JPEG'
    ) -> Tuple[bytes, bytes]:
        """
        Process photo with minimal memory footprint
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(image_data))
            
            # Resize immediately if too large (saves memory)
            if img.size[0] > self.max_dimension or img.size[1] > self.max_dimension:
                img.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
            
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create passport photo
            passport_photo = self._create_passport_photo(img)
            passport_bytes = self._image_to_bytes(passport_photo, output_format, quality=85)
            
            # Clear from memory before creating thumbnail
            del passport_photo
            gc.collect()
            
            # Create thumbnail
            thumbnail = self._create_thumbnail(img)
            thumbnail_bytes = self._image_to_bytes(thumbnail, output_format, quality=80)
            
            # Clean up
            del img, thumbnail
            gc.collect()
            
            return passport_bytes, thumbnail_bytes
            
        except Exception as e:
            # Clean up on error
            gc.collect()
            raise ValueError(f"Failed to process photo: {str(e)}")
    
    def _create_passport_photo(self, img: Image.Image) -> Image.Image:
        """Memory-efficient passport photo creation"""
        width, height = img.size
        target_ratio = 3 / 4
        current_ratio = width / height
        
        if current_ratio > target_ratio:
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            crop_box = (left, 0, left + new_width, height)
        else:
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            crop_box = (0, top, width, top + new_height)
        
        cropped = img.crop(crop_box)
        passport = cropped.resize(self.passport_size, Image.Resampling.LANCZOS)
        
        del cropped
        return passport
    
    def _create_thumbnail(self, img: Image.Image) -> Image.Image:
        """Memory-efficient thumbnail creation"""
        width, height = img.size
        size = min(width, height)
        
        left = (width - size) // 2
        top = (height - size) // 2
        
        square = img.crop((left, top, left + size, top + size))
        thumbnail = square.resize(self.thumbnail_size, Image.Resampling.LANCZOS)
        
        del square
        return thumbnail
    
    def _image_to_bytes(self, img: Image.Image, format: str = 'JPEG', quality: int = 85) -> bytes:
        """Convert to bytes with optimized quality"""
        buffer = io.BytesIO()
        img.save(buffer, format=format, quality=quality, optimize=True)
        return buffer.getvalue()
    
    def validate_photo(self, image_data: bytes) -> bool:
        """Lightweight validation"""
        if len(image_data) > self.max_file_size:
            raise ValueError(f"Photo exceeds {self.max_file_size // (1024*1024)}MB limit")
        
        # Quick validation without full load
        try:
            img = Image.open(io.BytesIO(image_data))
            if img.size[0] < 150 or img.size[1] < 150:
                raise ValueError("Photo too small (minimum 150x150 pixels)")
            del img
            gc.collect()
            return True
        except Exception as e:
            gc.collect()
            raise ValueError(f"Invalid photo: {str(e)}")

# Singleton
_photo_service = None

def get_photo_service():
    global _photo_service
    if _photo_service is None:
        _photo_service = OptimizedPhotoService()
    return _photo_service
