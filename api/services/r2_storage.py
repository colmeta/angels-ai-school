"""
Cloudflare R2 Storage Handler
Handles file uploads/downloads to R2 (10GB free tier)
"""
import boto3
from botocore.client import Config
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime, timedelta

class R2StorageService:
    """
    Cloudflare R2 storage service (S3-compatible API)
    Free tier: 10GB storage, 1M Class A operations, 10M Class B operations
    """
    
    def __init__(self):
        self.account_id = os.getenv('R2_ACCOUNT_ID')
        self.access_key = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('R2_BUCKET', 'angels-ai-results')
        
        # Initialize S3 client for R2
        self.client = boto3.client(
            's3',
            endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'  # R2 uses 'auto'
        )
    
    async def upload_ai_result(self, school_id: str, user_id: str, result_id: str, data: Dict[str, Any]) -> bool:
        """
        Upload AI result to R2
        Path: schools/{school_id}/users/{user_id}/results/{result_id}.json
        """
        try:
            key = f"schools/{school_id}/users/{user_id}/results/{result_id}.json"
            
            # Add metadata
            data['uploaded_at'] = datetime.utcnow().isoformat()
            data['school_id'] = school_id
            data['user_id'] = user_id
            
            # Upload to R2
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data).encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'school_id': school_id,
                    'user_id': user_id,
                    'result_id': result_id
                }
            )
            
            return True
            
        except Exception as e:
            print(f"[R2] Upload failed: {e}")
            return False
    
    async def download_ai_result(self, school_id: str, user_id: str, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Download AI result from R2
        """
        try:
            key = f"schools/{school_id}/users/{user_id}/results/{result_id}.json"
            
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            data = json.loads(response['Body'].read().decode('utf-8'))
            return data
            
        except Exception as e:
            print(f"[R2] Download failed: {e}")
            return None
    
    async def list_results(self, school_id: str, user_id: str, limit: int = 100) -> list:
        """
        List all AI results for a user
        """
        try:
            prefix = f"schools/{school_id}/users/{user_id}/results/"
            
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            results = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Extract result_id from key
                    result_id = obj['Key'].split('/')[-1].replace('.json', '')
                    results.append({
                        'result_id': result_id,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
            
            return results
            
        except Exception as e:
            print(f"[R2] List failed: {e}")
            return []
    
    async def get_storage_usage(self, school_id: str) -> Dict[str, Any]:
        """
        Get storage usage for a school
        """
        try:
            prefix = f"schools/{school_id}/"
            
            total_size = 0
            total_objects = 0
            
            paginator = self.client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj['Size']
                        total_objects += 1
            
            free_limit = 10 * 1024 * 1024 * 1024  # 10GB
            
            return {
                'used_bytes': total_size,
                'used_mb': round(total_size / (1024 * 1024), 2),
                'used_gb': round(total_size / (1024 * 1024 * 1024), 2),
                'limit_bytes': free_limit,
                'limit_gb': 10,
                'percentage': round((total_size / free_limit) * 100, 2),
                'total_objects': total_objects,
                'is_free': total_size < free_limit
            }
            
        except Exception as e:
            print(f"[R2] Usage check failed: {e}")
            return {
                'used_bytes': 0,
                'limit_bytes': 10 * 1024 * 1024 * 1024,
                'percentage': 0,
                'total_objects': 0,
                'is_free': True
            }
    
    async def delete_old_results(self, school_id: str, days: int = 90) -> int:
        """
        Delete AI results older than X days to free up space
        """
        try:
            prefix = f"schools/{school_id}/"
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted_count = 0
            
            paginator = self.client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                            self.client.delete_object(
                                Bucket=self.bucket_name,
                                Key=obj['Key']
                            )
                            deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"[R2] Cleanup failed: {e}")
            return 0
    
    async def generate_public_url(self, school_id: str, user_id: str, result_id: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate temporary public URL for a result (expires in 1 hour by default)
        """
        try:
            key = f"schools/{school_id}/users/{user_id}/results/{result_id}.json"
            
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
            
            return url
            
        except Exception as e:
            print(f"[R2] URL generation failed: {e}")
            return None


# Singleton instance
_r2_service: Optional[R2StorageService] = None

def get_r2_service() -> R2StorageService:
    global _r2_service
    if _r2_service is None:
        _r2_service = R2StorageService()
    return _r2_service
