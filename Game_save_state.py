#Game_save_state.py

import sqlite3

def handle_data(data_name, operation, data_value=None, default=0):
    try:
        with sqlite3.connect('game_data.db') as conn:
            cursor = conn.cursor()

            if operation == 'save':
                cursor.execute(
                    'INSERT OR REPLACE INTO GameData (data_name, data_value) VALUES (?, ?)',
                    (data_name, data_value)
                )
            elif operation == 'get':
                cursor.execute(
                    'SELECT data_value FROM GameData WHERE data_name = ?',
                    (data_name,)
                )
                result = cursor.fetchone()
                return result[0] if result else default
            elif operation == 'update':
                cursor.execute(
                    'UPDATE GameData SET data_value = ? WHERE data_name = ?',
                    (data_value, data_name)
                )

            conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return default
