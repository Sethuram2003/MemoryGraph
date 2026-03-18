import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any
import os

class MySQLManager:
    """
    Manager class for MySQL database operations related to chat history.
    Handles database creation, table setup, and CRUD for sessions/messages.
    """

    def __init__(self, host: str, user: str, password: str, default_database: Optional[str] = None):
        """
        Initialize the connection to MySQL server (without a default database).
        :param host: MySQL server host
        :param user: MySQL username
        :param password: MySQL password
        :param default_database: Optional default database name to use when not specified in methods
        """
        self.host = host
        self.user = user
        self.password = password
        self.default_database = default_database
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the MySQL server (no database selected)."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=None  
            )
            print("MySQL connection established.")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")



    def create_database(self, db_name: str):
        """
        Create a new database with the given name if it does not exist.
        Uses utf8mb4 character set for full Unicode support.
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} "
                           f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            self.connection.commit()
            print(f"Database '{db_name}' created or already exists.")
        except Error as e:
            print(f"Error creating database '{db_name}': {e}")
        finally:
            cursor.close()

    def delete_database(self, db_name: str):
        """Drop the specified database if it exists."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            self.connection.commit()
            print(f"Database '{db_name}' deleted successfully.")
        except Error as e:
            print(f"Error deleting database '{db_name}': {e}")
        finally:
            cursor.close()

    def clear_database(self, db_name: str):
        """
        Remove all data from the database by truncating both tables.
        The database itself is not deleted.
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {db_name}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("TRUNCATE TABLE messages")
            cursor.execute("TRUNCATE TABLE sessions")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            print(f"Database '{db_name}' cleared successfully.")
        except Error as e:
            print(f"Error clearing database '{db_name}': {e}")
        finally:
            cursor.close()


    def create_tables_if_not_exist(self, db_name: Optional[str] = None):
        """
        Create the `sessions` and `messages` tables in the specified database.
        If db_name is omitted, self.default_database is used.
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to create tables.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {target_db}")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                    session_identifier VARCHAR(255) NOT NULL COMMENT 'External unique session ID',
                    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                    status ENUM('active', 'closed') NOT NULL DEFAULT 'active',
                    PRIMARY KEY (id),
                    UNIQUE INDEX idx_session_identifier (session_identifier),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                    session_id INT UNSIGNED NOT NULL,
                    sender_type ENUM('user', 'agent') NOT NULL,
                    message TEXT NOT NULL,
                    sent_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    INDEX idx_session_sent (session_id, sent_at),
                    CONSTRAINT fk_messages_session
                        FOREIGN KEY (session_id)
                        REFERENCES sessions (id)
                        ON DELETE CASCADE
                        ON UPDATE RESTRICT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            self.connection.commit()
            print(f"Tables created successfully in database '{target_db}'.")
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()

    def _ensure_session(self, db_name: str, session_identifier: str) -> int:
        """
        Internal helper: ensure a session exists in the given database.
        Returns the internal session id (sessions.id).
        """
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {db_name}")

            cursor.execute(
                "SELECT id FROM sessions WHERE session_identifier = %s",
                (session_identifier,)
            )
            row = cursor.fetchone()
            if row:
                return row['id']

            cursor.execute(
                "INSERT INTO sessions (session_identifier) VALUES (%s)",
                (session_identifier,)
            )
            self.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    def store_message(self, session_identifier: str, sender_type: str, message: str,
                      db_name: Optional[str] = None):
        """
        Store a single message in the specified session.
        :param session_identifier: external session identifier (e.g., UUID)
        :param sender_type: 'user' or 'agent'
        :param message: message content
        :param db_name: target database; if None, self.default_database is used
        """
        if sender_type not in ('user', 'agent'):
            raise ValueError("sender_type must be 'user' or 'agent'")

        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to store message.")

        session_id = self._ensure_session(target_db, session_identifier)

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {target_db}")
            cursor.execute(
                "INSERT INTO messages (session_id, sender_type, message) VALUES (%s, %s, %s)",
                (session_id, sender_type, message)
            )
            self.connection.commit()
            print(f"Message stored in session '{session_identifier}'.")
        finally:
            cursor.close()

    def get_session_history(self, session_identifier: str,
                            limit: Optional[int] = None,
                            order: str = 'asc',
                            db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve messages from a session in chronological order.
        :param session_identifier: external session ID
        :param limit: maximum number of messages to return (most recent if descending order)
        :param order: 'asc' (oldest first) or 'desc' (newest first)
        :param db_name: target database; if None, self.default_database is used
        :return: list of dicts with keys: sender_type, message, sent_at
        """
        if order.lower() not in ('asc', 'desc'):
            raise ValueError("order must be 'asc' or 'desc'")

        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to retrieve history.")

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {target_db}")

            cursor.execute(
                "SELECT id FROM sessions WHERE session_identifier = %s",
                (session_identifier,)
            )
            session_row = cursor.fetchone()
            if not session_row:
                return []

            session_id = session_row['id']

            base_query = """
                SELECT sender_type, message, sent_at
                FROM messages
                WHERE session_id = %s
                ORDER BY sent_at {order}, id {order}
            """
            query = base_query.format(order=order.upper())

            if limit is not None:
                query += " LIMIT %s"
                cursor.execute(query, (session_id, limit))
            else:
                cursor.execute(query, (session_id,))

            return cursor.fetchall()
        finally:
            cursor.close()

    def list_sessions(self, include_stats: bool = False,
                      db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all sessions in the database.
        :param include_stats: if True, include message count and last message timestamp
        :param db_name: target database; if None, self.default_database is used
        :return: list of session records
        """
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to list sessions.")

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {target_db}")

            if include_stats:
                cursor.execute("""
                    SELECT
                        s.session_identifier,
                        s.created_at,
                        s.updated_at,
                        s.status,
                        COUNT(m.id) AS message_count,
                        MAX(m.sent_at) AS last_message_at
                    FROM sessions s
                    LEFT JOIN messages m ON s.id = m.session_id
                    GROUP BY s.id
                    ORDER BY s.updated_at DESC
                """)
            else:
                cursor.execute("""
                    SELECT session_identifier, created_at, updated_at, status
                    FROM sessions
                    ORDER BY updated_at DESC
                """)

            return cursor.fetchall()
        finally:
            cursor.close()

    def delete_session(self, session_identifier: str, db_name: Optional[str] = None):
        """Delete a session and all its messages (cascade via foreign key)."""
        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to delete session.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {target_db}")
            cursor.execute(
                "DELETE FROM sessions WHERE session_identifier = %s",
                (session_identifier,)
            )
            self.connection.commit()
            print(f"Session '{session_identifier}' deleted.")
        finally:
            cursor.close()

    def update_session_status(self, session_identifier: str, status: str,
                              db_name: Optional[str] = None):
        """Update the status of a session ('active' or 'closed')."""
        if status not in ('active', 'closed'):
            raise ValueError("status must be 'active' or 'closed'")

        target_db = db_name or self.default_database
        if not target_db:
            raise ValueError("No database specified to update session status.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {target_db}")
            cursor.execute(
                "UPDATE sessions SET status = %s WHERE session_identifier = %s",
                (status, session_identifier)
            )
            self.connection.commit()
            print(f"Session '{session_identifier}' status updated to '{status}'.")
        finally:
            cursor.close()



if __name__ == "__main__":
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "chat_history_db")

    manager = MySQLManager(host, user, password, default_database=database)

    manager.create_database(database)
    manager.create_tables_if_not_exist()

    manager.store_message("session-123", "user", "Hello, I need help with my order.")
    manager.store_message("session-123", "agent", "Sure, I can help. What's your order number?")
    manager.store_message("session-456", "user", "Hi, I'd like to return an item.")

    history = manager.get_session_history("session-123", order="asc")
    print("History for session-123:")
    for msg in history:
        print(f"[{msg['sent_at']}] {msg['sender_type']}: {msg['message']}")

    sessions = manager.list_sessions(include_stats=True)
    print("\nAll sessions:")
    for sess in sessions:
        print(sess)

    manager.close()