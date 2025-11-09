#!/usr/bin/env python3
"""
Database Migration Runner for Angels AI School Platform
Runs all SQL migrations in sequence
"""

import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migrations():
    """Run all database migrations in sequence"""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Migration files in order
    migrations = [
        '001_initial_schema.sql',
        '002_academic_operations.sql',
        '003_financial_operations.sql',
        '004_support_operations.sql',
        '005_communications_and_ai.sql'
    ]
    
    migrations_dir = Path(__file__).parent / 'migrations'
    
    try:
        # Connect to database
        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Run each migration
        for migration_file in migrations:
            migration_path = migrations_dir / migration_file
            
            if not migration_path.exists():
                print(f"⚠️  Migration file not found: {migration_file}")
                continue
            
            print(f"📄 Running migration: {migration_file}")
            
            with open(migration_path, 'r') as f:
                sql = f.read()
                
                try:
                    cur.execute(sql)
                    conn.commit()
                    print(f"✅ Applied {migration_file}")
                except Exception as e:
                    conn.rollback()
                    print(f"❌ Error in {migration_file}: {str(e)}")
                    raise
        
        # Close connection
        cur.close()
        conn.close()
        
        print("\n🎉 All migrations completed successfully!")
        print("\n📊 Database is ready for Angels AI School Platform")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Angels AI School Platform - Database Migration Runner")
    print("=" * 60)
    print()
    
    run_migrations()
