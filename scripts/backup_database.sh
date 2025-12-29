#!/bin/bash

# ============================================================================
# DATABASE BACKUP SCRIPT FOR PRODUCTION
# Run this daily via cron job or Render's cron service
# ============================================================================

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="angels_ai_backup_${DATE}.sql.gz"
RETENTION_DAYS=7  # Keep backups for 7 days

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Starting database backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ ERROR: DATABASE_URL environment variable not set${NC}"
    exit 1
fi

# Start backup
START_TIME=$(date +%s)

# Perform backup using pg_dump
echo -e "${YELLOW}📦 Creating backup: $BACKUP_FILE${NC}"

if pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/$BACKUP_FILE"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    SIZE=$(du -m "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    
    echo -e "${GREEN}✅ Backup completed successfully!${NC}"
    echo -e "${GREEN}   File: $BACKUP_FILE${NC}"
    echo -e "${GREEN}   Size: ${SIZE}MB${NC}"
    echo -e "${GREEN}   Duration: ${DURATION}s${NC}"
    
    # Log successful backup
    psql "$DATABASE_URL" -c "SELECT log_backup('automated', 'success', $SIZE, $DURATION, '$BACKUP_FILE', NULL);" > /dev/null 2>&1
    
else
    echo -e "${RED}❌ Backup failed!${NC}"
    
    # Log failed backup
    psql "$DATABASE_URL" -c "SELECT log_backup('automated', 'failed', NULL, NULL, '$BACKUP_FILE', 'pg_dump failed');" > /dev/null 2>&1
    
    exit 1
fi

# Clean up old backups (keep only last 7 days)
echo -e "${YELLOW}🧹 Cleaning up old backups (keeping last $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "angels_ai_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

REMAINING=$(ls -1 "$BACKUP_DIR"/angels_ai_backup_*.sql.gz 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Cleanup complete. $REMAINING backups remaining.${NC}"

# Optional: Upload to cloud storage (S3, GCS, etc.)
if [ ! -z "$S3_BACKUP_BUCKET" ]; then
    echo -e "${YELLOW}☁️  Uploading to S3...${NC}"
    aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$S3_BACKUP_BUCKET/backups/$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Uploaded to S3 successfully${NC}"
    else
        echo -e "${RED}⚠️  S3 upload failed (backup still saved locally)${NC}"
    fi
fi

echo -e "${GREEN}🎉 Backup process complete!${NC}"
