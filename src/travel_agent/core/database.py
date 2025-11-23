"""Database module for user authentication using SQLite."""
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import os


class Database:
    """SQLite database handler for user authentication."""
    
    def __init__(self, db_path: str = "travel_agent.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Create user_sessions table for tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create chat_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                conversation_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Migrate existing chat_history table to add conversation_id if it doesn't exist
        try:
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'conversation_id' not in columns:
                cursor.execute("""
                    ALTER TABLE chat_history ADD COLUMN conversation_id TEXT
                """)
                # For existing messages without conversation_id, assign them to a default conversation
                cursor.execute("""
                    UPDATE chat_history 
                    SET conversation_id = 'conv_legacy_' || strftime('%Y%m%d_%H%M%S', created_at)
                    WHERE conversation_id IS NULL
                """)
        except Exception as e:
            print(f"Migration note: {str(e)}")
        
        # Create conversations table to track conversation metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id TEXT UNIQUE NOT NULL,
                title TEXT,
                first_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_history(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_history(created_at)
        """)
        # Only create conversation_id index if the column exists
        try:
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'conversation_id' in columns:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_chat_conversation_id ON chat_history(conversation_id)
                """)
        except Exception:
            pass
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at)
        """)
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + password_hash.hex()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt = bytes.fromhex(password_hash[:64])
            stored_hash = password_hash[64:]
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return password_hash_check.hex() == stored_hash
        except Exception:
            return False
    
    def create_user(self, username: str, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Create a new user account."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self._hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, full_name, datetime.now()))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "User created successfully"
            }
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return {"success": False, "message": "Username already exists"}
            elif "email" in str(e):
                return {"success": False, "message": "Email already exists"}
            return {"success": False, "message": "Database error"}
        except Exception as e:
            return {"success": False, "message": f"Error creating user: {str(e)}"}
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data if successful."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, password_hash, full_name, is_active
                FROM users
                WHERE username = ? OR email = ?
            """, (username, username))
            
            user = cursor.fetchone()
            
            if not user:
                return None
            
            if not user['is_active']:
                return {"success": False, "message": "Account is deactivated"}
            
            if not self._verify_password(password, user['password_hash']):
                return None
            
            # Update last login
            cursor.execute("""
                UPDATE users
                SET last_login = ?
                WHERE id = ?
            """, (datetime.now(), user['id']))
            conn.commit()
            
            return {
                "success": True,
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user['full_name']
            }
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, full_name, created_at, last_login
                FROM users
                WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    "user_id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "created_at": user['created_at'],
                    "last_login": user['last_login']
                }
            return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def user_exists(self, username: str = None, email: str = None) -> bool:
        """Check if user exists by username or email."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if username:
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            elif email:
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            else:
                return False
            
            return cursor.fetchone() is not None
        except Exception:
            return False
        finally:
            conn.close()
    
    def save_chat_message(self, user_id: int, role: str, content: str, session_id: str = None, conversation_id: str = None) -> bool:
        """Save a chat message to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # If no conversation_id, create one from timestamp
            if not conversation_id:
                conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor.execute("""
                INSERT INTO chat_history (user_id, role, content, created_at, session_id, conversation_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, role, content, datetime.now(), session_id, conversation_id))
            
            # Update or create conversation record
            if role == "user":
                # Extract first few words as title
                title = content[:50] + "..." if len(content) > 50 else content
                first_message = content[:200] if len(content) > 200 else content
                
                # Check if conversation exists
                cursor.execute("""
                    SELECT id FROM conversations WHERE conversation_id = ?
                """, (conversation_id,))
                
                if cursor.fetchone():
                    # Update existing conversation
                    cursor.execute("""
                        UPDATE conversations
                        SET updated_at = ?, message_count = message_count + 1
                        WHERE conversation_id = ?
                    """, (datetime.now(), conversation_id))
                else:
                    # Create new conversation
                    cursor.execute("""
                        INSERT INTO conversations (user_id, conversation_id, title, first_message, created_at, updated_at, message_count)
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                    """, (user_id, conversation_id, title, first_message, datetime.now(), datetime.now()))
            else:
                # Increment message count for assistant messages
                cursor.execute("""
                    UPDATE conversations
                    SET updated_at = ?, message_count = message_count + 1
                    WHERE conversation_id = ?
                """, (datetime.now(), conversation_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving chat message: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_chat_history(self, user_id: int, limit: int = None, conversation_id: str = None) -> list:
        """Get chat history for a user, optionally filtered by conversation_id."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if conversation_id:
                query = """
                    SELECT role, content, created_at, session_id, conversation_id
                    FROM chat_history
                    WHERE user_id = ? AND conversation_id = ?
                    ORDER BY created_at ASC
                """
                params = (user_id, conversation_id)
            else:
                query = """
                    SELECT role, content, created_at, session_id, conversation_id
                    FROM chat_history
                    WHERE user_id = ?
                    ORDER BY created_at ASC
                """
                params = (user_id,)
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append({
                    "role": row['role'],
                    "content": row['content'],
                    "created_at": row['created_at'],
                    "session_id": row['session_id'],
                    "conversation_id": row['conversation_id']
                })
            
            return messages
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return []
        finally:
            conn.close()
    
    def get_conversations(self, user_id: int, limit: int = 10) -> list:
        """Get list of conversations for a user, ordered by most recent."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT conversation_id, title, first_message, created_at, updated_at, message_count
                FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "conversation_id": row['conversation_id'],
                    "title": row['title'],
                    "first_message": row['first_message'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at'],
                    "message_count": row['message_count']
                })
            
            return conversations
        except Exception as e:
            print(f"Error getting conversations: {str(e)}")
            return []
        finally:
            conn.close()
    
    def get_conversation_by_id(self, user_id: int, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific conversation by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT conversation_id, title, first_message, created_at, updated_at, message_count
                FROM conversations
                WHERE user_id = ? AND conversation_id = ?
            """, (user_id, conversation_id))
            
            row = cursor.fetchone()
            if row:
                return {
                    "conversation_id": row['conversation_id'],
                    "title": row['title'],
                    "first_message": row['first_message'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at'],
                    "message_count": row['message_count']
                }
            return None
        except Exception as e:
            print(f"Error getting conversation: {str(e)}")
            return None
        finally:
            conn.close()
    
    def clear_chat_history(self, user_id: int, conversation_id: str = None) -> bool:
        """Clear chat history for a user, optionally for a specific conversation."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if conversation_id:
                cursor.execute("""
                    DELETE FROM chat_history
                    WHERE user_id = ? AND conversation_id = ?
                """, (user_id, conversation_id))
                
                cursor.execute("""
                    DELETE FROM conversations
                    WHERE user_id = ? AND conversation_id = ?
                """, (user_id, conversation_id))
            else:
                cursor.execute("""
                    DELETE FROM chat_history
                    WHERE user_id = ?
                """, (user_id,))
                
                cursor.execute("""
                    DELETE FROM conversations
                    WHERE user_id = ?
                """, (user_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error clearing chat history: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_chat_count(self, user_id: int) -> int:
        """Get total number of chat messages for a user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM chat_history
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception:
            return 0
        finally:
            conn.close()

