"""
Dynamic Branding Service
Loads school-specific branding (colors, logo, domain) dynamically
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import get_db

router = APIRouter(prefix="/api/branding", tags=["branding"])

@router.get("/{school_id}")
async def get_school_branding(school_id: str):
    """
    Get school branding configuration
    Used by frontend to dynamically apply school colors, logo, etc.
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                sb.brand_name,
                sb.primary_color,
                sb.secondary_color,
                sb.logo_url,
                sb.favicon_url,
                sb.custom_domain,
                sb.tagline,
                s.name as school_name
            FROM school_branding sb
            JOIN schools s ON s.id = sb.school_id
            WHERE sb.school_id = %s
        """, (school_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            # Return defaults if no branding set
            return {
                "school_id": school_id,
                "brand_name": "Angels AI School",
                "primary_color": "#2563eb",
                "secondary_color": "#1e40af",
                "logo_url": "https://cdn.angels-ai.com/default-logo.png",
                "favicon_url": "https://cdn.angels-ai.com/favicon.ico",
                "custom_domain": None,
                "tagline": "Empowering Education"
            }
        
        return {
            "school_id": school_id,
            "brand_name": result[0],
            "primary_color": result[1],
            "secondary_color": result[2],
            "logo_url": result[3],
            "favicon_url": result[4],
            "custom_domain": result[5],
            "tagline": result[6]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{school_id}")
async def update_school_branding(
    school_id: str,
    brand_name: Optional[str] = None,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    logo_url: Optional[str] = None,
    tagline: Optional[str] = None
):
    """
    Update school branding
    Allows schools to customize their look & feel
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Build dynamic UPDATE query
        updates = []
        params = []
        
        if brand_name:
            updates.append("brand_name = %s")
            params.append(brand_name)
        if primary_color:
            updates.append("primary_color = %s")
            params.append(primary_color)
        if secondary_color:
            updates.append("secondary_color = %s")
            params.append(secondary_color)
        if logo_url:
            updates.append("logo_url = %s")
            params.append(logo_url)
        if tagline:
            updates.append("tagline = %s")
            params.append(tagline)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        params.append(school_id)
        
        cursor.execute(f"""
            UPDATE school_branding
            SET {', '.join(updates)}
            WHERE school_id = %s
        """, params)
        
        db.commit()
        cursor.close()
        
        return {"success": True, "message": "Branding updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-domain/{domain}")
async def get_branding_by_domain(domain: str):
    """
    Get school branding by custom domain
    Used for white-label routing
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT school_id
            FROM school_branding
            WHERE custom_domain = %s
        """, (domain,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get full branding
        return await get_school_branding(result[0])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
