#!/bin/bash

# ============================================================================
# DATABASE RESTORE SCRIPT
# Use this to restore from backup
# ============================================================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ ERROR: No backup file specified${NC}"
    echo ""
    echo "Usage: ./restore_database.sh <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/angels_ai_backup_*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ ERROR: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ ERROR: DATABASE_URL environment variable not set${NC}"
    exit 1
fi

# Confirmation prompt
echo -e "${RED}⚠️  WARNING: This will OVERWRITE your current database!${NC}"
echo -e "${YELLOW}Are you sure you want to restore from: $BACKUP_FILE?${NC}"
read -p "Type 'YES' to continue: " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo -e "${YELLOW}❌ Restore cancelled${NC}"
    exit 0
fi

# Start restore
echo -e "${YELLOW}🔄 Starting database restore...${NC}"
START_TIME=$(date +%s)

# Drop existing connections
echo -e "${YELLOW}Terminating existing connections...${NC}"
psql "$DATABASE_URL" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();" > /dev/null 2>&1

# Restore backup
echo -e "${YELLOW}📦 Restoring from: $BACKUP_FILE${NC}"

if gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo -e "${GREEN}✅ Restore completed successfully!${NC}"
    echo -e "${GREEN}   Duration: ${DURATION}s${NC}"
    
    # Log restore
    psql "$DATABASE_URL" -c "SELECT log_backup('restore', 'success', NULL, $DURATION, '$BACKUP_FILE', NULL);" > /dev/null 2>&1
    
else
    echo -e "${RED}❌ Restore failed!${NC}"
    
    # Log failed restore
    psql "$DATABASE_URL" -c "SELECT log_backup('restore', 'failed', NULL, NULL, '$BACKUP_FILE', 'psql restore failed');" > /dev/null 2>&1
    
    exit 1
fi

echo -e "${GREEN}🎉 Restore process complete!${NC}"
echo -e "${YELLOW}⚠️  Remember to restart your application${NC}"
