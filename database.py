import sqlite3
import os
"""
users (1) —— (∞) chat_sessions —— (∞) chat_messages
   |
   └── (∞) game_high_scores

users:id,username,email,password
      索引idx_username,idx_email：提升查询速度
chat_sessions:session_id,user_id,model_name,started_at
chat_messages:message_id,session_id,role,content,created_at
game_high_scores:score_id,user_id,game_name,score,played_at

"""
DATABASE_NAME = 'ai_app.db'

def create_connection():
    """创建并返回一个到 SQLite 数据库的连接对象。"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables():
    """Create the users and chat_history tables if they don't exist."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # 用户表：保存账号、邮箱、密码
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                );
            ''')
            # 为 username 和 email 创建唯一索引，加快查询速度
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_username ON users (username);')
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_email ON users (email);')
            # 聊天会话表：记录用户一次完整会话
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    model_name TEXT NOT NULL,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
            ''')
            # 聊天消息表：保存每条聊天消息
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,          -- 'user' 或 'assistant'
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id) ON DELETE CASCADE
                );
            ''')

            # 游戏成绩表：保存用户在游戏中的高分
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_high_scores (
                    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    game_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
            ''')
            #提交到数据库
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

def add_user(username, email, password): # password will now be stored as plain text
    """Add a new user to the users table."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                           (username, email, password))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            #用户名或邮箱重复
            if "UNIQUE constraint failed: users.username" in str(e):
                return "username_exists"
            elif "UNIQUE constraint failed: users.email" in str(e):
                return "email_exists"
            print(f"Database error during add_user: {e}")
            return False
        except sqlite3.Error as e:
            print(f"Database error during add_user: {e}")
            return False
        finally:
            conn.close()
    return False

def get_user_by_username(username):
    """Retrieve a user's details by username."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email, password FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user:
                return {"id": user[0], "username": user[1], "email": user[2], "password": user[3]}
            return None
        except sqlite3.Error as e:
            print(f"Database error during get_user_by_username: {e}")
            return None
        finally:
            conn.close()
    return None

def get_all_users():
    """Retrieve all users' details (excluding password for security when listing)."""
    conn = create_connection()
    users = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email FROM users ORDER BY username ASC')
            for row in cursor.fetchall():
                users.append({"id": row[0], "username": row[1], "email": row[2]})
            return users
        except sqlite3.Error as e:
            print(f"Database error during get_all_users: {e}")
            return []
        finally:
            conn.close()
    return []

def update_user_password(user_id, new_password): # new_password will now be stored as plain text
    """Update a user's password."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
            conn.commit()
            return cursor.rowcount > 0 # Returns True if a row was updated
        except sqlite3.Error as e:
            print(f"Database error during update_user_password: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_user(user_id):
    """Delete a user and their associated chat history."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            #由cascade，同时也删除了会话及游戏记录
            conn.commit()
            return cursor.rowcount > 0 # Returns True if a row was deleted
        except sqlite3.Error as e:
            print(f"Database error during delete_user: {e}")
            return False
        finally:
            conn.close()
    return False

def save_chat_session(user_id, model_name, messages):
    """Save an entire chat session with its messages to the database."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Start a new session
            cursor.execute('INSERT INTO chat_sessions (user_id, model_name) VALUES (?, ?)', (user_id, model_name))
            session_id = cursor.lastrowid

            # Save each message in the session
            for i, msg_content in enumerate(messages):
                role = "user" if i % 2 == 0 else "assistant"
                cursor.execute('INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)',
                               (session_id, role, msg_content))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error during save_chat_session: {e}")
            return False
        finally:
            conn.close()
    return False

def save_game_score(user_id, game_name, score):
    """Save a user's game score to the database."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO game_high_scores (user_id, game_name, score) VALUES (?, ?, ?)',
                           (user_id, game_name, score))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error during save_game_score: {e}")
            return False
        finally:
            conn.close()
    return False

def get_leaderboard(game_name, limit=10):
    """Retrieve the top scores for a specific game."""
    conn = create_connection()
    leaderboard = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.username, g.score, g.played_at
                FROM game_high_scores g
                JOIN users u ON g.user_id = u.id
                WHERE g.game_name = ?
                ORDER BY g.score DESC, g.played_at ASC
                LIMIT ?
            ''', (game_name, limit))
            for row in cursor.fetchall():
                leaderboard.append({"username": row[0], "score": row[1], "played_at": row[2]})
            return leaderboard
        except sqlite3.Error as e:
            print(f"Database error during get_leaderboard: {e}")
            return []
        finally:
            conn.close()
    return []

# Ensure tables are created when this module is imported
create_tables()