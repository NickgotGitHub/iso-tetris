"""
Database operations for the Tetris game.
"""

import sqlite3
from typing import Any, Optional

class GameDatabase:
    def __init__(self, db_path: str = 'game_data.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS GameData (
                        data_name TEXT PRIMARY KEY,
                        data_value INTEGER
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")

    def save_data(self, data_name: str, data_value: Any) -> bool:
        """
        Save data to the database.
        
        Args:
            data_name: Name of the data entry
            data_value: Value to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR REPLACE INTO GameData (data_name, data_value) VALUES (?, ?)',
                    (data_name, data_value)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database save error: {e}")
            return False

    def get_data(self, data_name: str, default: Any = 0) -> Any:
        """
        Retrieve data from the database.
        
        Args:
            data_name: Name of the data entry to retrieve
            default: Default value if data not found
            
        Returns:
            The retrieved value or default if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT data_value FROM GameData WHERE data_name = ?',
                    (data_name,)
                )
                result = cursor.fetchone()
                return result[0] if result else default
        except sqlite3.Error as e:
            print(f"Database retrieval error: {e}")
            return default

    def update_data(self, data_name: str, data_value: Any) -> bool:
        """
        Update existing data in the database.
        
        Args:
            data_name: Name of the data entry to update
            data_value: New value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE GameData SET data_value = ? WHERE data_name = ?',
                    (data_value, data_name)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database update error: {e}")
            return False

# Create a global instance for easy access
db = GameDatabase() 