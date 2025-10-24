"""
Angels AI - Database Utilities
Handles all database connections and common operations
"""

import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime
import json


class DatabaseManager:
    """
    Manages PostgreSQL connections using connection pooling
    Think of this as your database 'bouncer' - manages who gets in/out efficiently
    """
    
    def __init__(self, database_url: Optional[str] = None, min_conn: int = 1, max_conn: int = 10):
        """
        Initialize database connection pool
        
        Args:
            database_url: PostgreSQL connection string
            min_conn: Minimum connections to keep open
            max_conn: Maximum connections allowed
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_
