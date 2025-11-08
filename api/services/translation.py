"""
Translation Service
Multi-language support for Luganda, Swahili, and English
Uses Clarity AI for translation (user's API)
"""
from typing import Dict, Any, Optional
import hashlib

from api.services.database import get_db_manager


class TranslationService:
    """Service for multi-language translation"""
    
    # Common translations (hardcoded for speed)
    TRANSLATIONS = {
        # English → Luganda
        'en_lg': {
            'present': 'ali wano',
            'absent': 'tali wano',
            'today': 'leero',
            'welcome': 'tukusanyukidde',
            'student': 'omuyizi',
            'parent': 'omuzadde',
            'teacher': 'omusomesa',
            'school': 'essomero',
            'fees': 'ebisale',
            'balance': 'omusigadde',
            'attendance': 'okubeeraawo',
            'grades': 'obubonero',
            'good': 'kirungi',
            'excellent': 'kisinga obulungi',
            'pass': 'ayise',
            'fail': 'atagenze bulungi',
        },
        
        # English → Swahili
        'en_sw': {
            'present': 'yupo',
            'absent': 'hayupo',
            'today': 'leo',
            'welcome': 'karibu',
            'student': 'mwanafunzi',
            'parent': 'mzazi',
            'teacher': 'mwalimu',
            'school': 'shule',
            'fees': 'ada',
            'balance': 'salio',
            'attendance': 'mahudhurio',
            'grades': 'alama',
            'good': 'nzuri',
            'excellent': 'bora sana',
            'pass': 'amepita',
            'fail': 'ameshindwa',
        }
    }
    
    def __init__(self):
        self.db = get_db_manager()
    
    # ============================================================================
    # TRANSLATION
    # ============================================================================
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = 'en'
    ) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: lg (Luganda), sw (Swahili), en (English)
            source_language: Source language (default: en)
        
        Returns:
            Translated text
        """
        # If same language, return as-is
        if source_language == target_language:
            return text
        
        # If target is English, return as-is
        if target_language == 'en':
            return text
        
        # Check cache first
        cached = self._get_cached_translation(text, source_language, target_language)
        if cached:
            return cached
        
        # Try hardcoded translations first (faster)
        translation_key = f"{source_language}_{target_language}"
        if translation_key in self.TRANSLATIONS:
            # Try word-by-word translation for simple phrases
            words = text.lower().split()
            translated_words = []
            
            for word in words:
                if word in self.TRANSLATIONS[translation_key]:
                    translated_words.append(self.TRANSLATIONS[translation_key][word])
                else:
                    translated_words.append(word)  # Keep untranslated
            
            if len(translated_words) == len(words):
                # All words translated
                result = ' '.join(translated_words)
                self._cache_translation(text, source_language, target_language, result, 'manual', 1.0)
                return result
        
        # If not in hardcoded, use Clarity AI (user's API)
        # TODO: User will provide Clarity API key for translation
        # translated = self._translate_via_clarity_api(text, source_language, target_language)
        
        # For now, return English + note
        return f"{text} (Translation to {target_language} pending)"
    
    def translate_template(
        self,
        template: str,
        values: Dict[str, str],
        target_language: str
    ) -> str:
        """
        Translate a message template with placeholders
        
        Example:
            template = "{student} is {status} today"
            values = {"student": "Mary", "status": "present"}
            target = "lg"
            
            Result: "Mary ali wano leero"
        """
        # First, fill in values
        message = template.format(**values)
        
        # Then translate
        return self.translate(message, target_language)
    
    def get_user_language(
        self,
        user_id: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> str:
        """
        Get user's preferred language
        
        Returns: 'en', 'lg', 'sw', etc.
        """
        query = """
        SELECT preferred_language
        FROM user_language_preferences
        WHERE (user_id = %s OR phone_number = %s)
        LIMIT 1
        """
        
        result = self.db.execute_query(query, (user_id, phone_number), fetch=True)
        
        if result:
            return result[0]['preferred_language']
        
        # Default to English
        return 'en'
    
    def set_user_language(
        self,
        language: str,
        user_id: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set user's preferred language
        """
        if not user_id and not phone_number:
            return {"success": False, "error": "Need user_id or phone_number"}
        
        query = """
        INSERT INTO user_language_preferences (user_id, phone_number, preferred_language)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE
        SET preferred_language = EXCLUDED.preferred_language,
            updated_at = CURRENT_TIMESTAMP
        """
        
        self.db.execute_query(query, (user_id, phone_number, language))
        
        return {
            "success": True,
            "language": language
        }
    
    # ============================================================================
    # CACHE MANAGEMENT
    # ============================================================================
    
    def _get_cached_translation(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """Get translation from cache"""
        text_key = self._generate_key(text, source_lang, target_lang)
        
        query = """
        SELECT translated_text
        FROM translations
        WHERE text_key = %s
        AND source_language = %s
        AND target_language = %s
        LIMIT 1
        """
        
        result = self.db.execute_query(query, (text_key, source_lang, target_lang), fetch=True)
        
        if result:
            return result[0]['translated_text']
        
        return None
    
    def _cache_translation(
        self,
        source_text: str,
        source_lang: str,
        target_lang: str,
        translated_text: str,
        service: str = 'manual',
        confidence: float = 1.0
    ) -> None:
        """Cache translation for future use"""
        text_key = self._generate_key(source_text, source_lang, target_lang)
        
        query = """
        INSERT INTO translations (
            text_key, source_language, target_language,
            source_text, translated_text, translation_service, confidence_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (text_key, source_language, target_language)
        DO UPDATE SET
            translated_text = EXCLUDED.translated_text,
            confidence_score = EXCLUDED.confidence_score
        """
        
        self.db.execute_query(
            query,
            (text_key, source_lang, target_lang, source_text, translated_text, service, confidence)
        )
    
    def _generate_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate unique key for translation"""
        combined = f"{source_lang}_{target_lang}_{text}"
        return hashlib.md5(combined.encode()).hexdigest()[:50]
    
    # ============================================================================
    # COMMON MESSAGES (PRE-TRANSLATED)
    # ============================================================================
    
    def get_attendance_message(self, student_name: str, status: str, language: str) -> str:
        """Get pre-translated attendance message"""
        templates = {
            'en': {
                'present': f"{student_name} is present today",
                'absent': f"{student_name} is absent today"
            },
            'lg': {
                'present': f"{student_name} ali mu ssomero leero",
                'absent': f"{student_name} tali mu ssomero leero"
            },
            'sw': {
                'present': f"{student_name} yupo shuleni leo",
                'absent': f"{student_name} hayupo shuleni leo"
            }
        }
        
        return templates.get(language, templates['en']).get(status, '')
    
    def get_fee_message(self, student_name: str, balance: float, language: str) -> str:
        """Get pre-translated fee message"""
        templates = {
            'en': f"Fee balance for {student_name}: {balance:,.0f} UGX",
            'lg': f"Omusigadde gw'ebbisale bya {student_name}: {balance:,.0f} UGX",
            'sw': f"Salio la ada kwa {student_name}: {balance:,.0f} UGX"
        }
        
        return templates.get(language, templates['en'])


def get_translation_service() -> TranslationService:
    """Helper to get translation service instance"""
    return TranslationService()
