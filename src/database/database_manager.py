"""
Database Manager - Central database operations

This module provides a unified interface to all database operations,
ensuring consistent connection handling and query execution.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Central database management class"""
    
    def __init__(self, db_path: str = "data/database/school_timetable.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure database file and directory exist"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create database if it doesn't exist
        if not os.path.exists(self.db_path):
            self.initialize_database()
    
    def initialize_database(self):
        """Initialize database with all required tables"""
        try:
            from .database_setup import setup_database
            setup_database(self.db_path)
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute many queries with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    # Convenience methods for common operations
    
    def get_classes(self) -> List[Dict[str, Any]]:
        """Get all classes"""
        rows = self.execute_query("SELECT * FROM classes ORDER BY name")
        return [dict(row) for row in rows]
    
    def get_teachers(self) -> List[Dict[str, Any]]:
        """Get all teachers"""
        rows = self.execute_query("SELECT * FROM teachers ORDER BY name")
        return [dict(row) for row in rows]
    
    def get_subjects(self) -> List[Dict[str, Any]]:
        """Get all subjects"""
        rows = self.execute_query("SELECT * FROM subjects ORDER BY name")
        return [dict(row) for row in rows]
    
    def get_rooms(self) -> List[Dict[str, Any]]:
        """Get all rooms"""
        rows = self.execute_query("SELECT * FROM rooms ORDER BY name")
        return [dict(row) for row in rows]
    
    def get_time_slots(self) -> List[Dict[str, Any]]:
        """Get all time slots"""
        rows = self.execute_query("""
            SELECT * FROM time_slots 
            ORDER BY day_of_week, start_time
        """)
        return [dict(row) for row in rows]
    
    def get_schedule(self, include_locked: bool = True) -> List[Dict[str, Any]]:
        """
        Get current schedule
        
        Args:
            include_locked: Whether to include locked lessons
            
        Returns:
            List of scheduled lessons
        """
        query = """
            SELECT s.*, c.name as class_name, t.name as teacher_name,
                   sub.name as subject_name, r.name as room_name,
                   ts.day_of_week, ts.start_time, ts.end_time
            FROM schedules s
            JOIN classes c ON s.class_id = c.id
            JOIN teachers t ON s.teacher_id = t.id  
            JOIN subjects sub ON s.subject_id = sub.id
            JOIN rooms r ON s.room_id = r.id
            JOIN time_slots ts ON s.time_slot_id = ts.id
        """
        
        if not include_locked:
            query += " WHERE s.is_locked = 0"
            
        query += " ORDER BY ts.day_of_week, ts.start_time, c.name"
        
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    def clear_unlocked_schedule(self) -> int:
        """Clear all unlocked scheduled lessons"""
        return self.execute_update("DELETE FROM schedules WHERE is_locked = 0")
    
    def clear_all_schedule(self) -> int:
        """Clear all scheduled lessons (including locked)"""
        return self.execute_update("DELETE FROM schedules")
    
    def get_schedule_count(self, include_locked: bool = True) -> int:
        """Get count of scheduled lessons"""
        query = "SELECT COUNT(*) FROM schedules"
        if not include_locked:
            query += " WHERE is_locked = 0"
            
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}
        tables = ['classes', 'teachers', 'subjects', 'rooms', 'time_slots', 'schedules']
        
        for table in tables:
            result = self.execute_query(f"SELECT COUNT(*) FROM {table}")
            stats[table] = result[0][0] if result else 0
            
        return stats
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
    
    def restore_database(self, backup_path: str):
        """Restore database from backup"""
        import shutil
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Database restored from {backup_path}")
        else:
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    def vacuum_database(self):
        """Optimize database (VACUUM)"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            conn.commit()
        logger.info("Database vacuumed")
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get information about a table's structure"""
        rows = self.execute_query(f"PRAGMA table_info({table_name})")
        return [dict(row) for row in rows]