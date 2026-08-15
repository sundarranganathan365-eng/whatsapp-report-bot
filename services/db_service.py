import os
import logging
import pymysql
from urllib.parse import urlparse, parse_qs
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.reload_config()

    def reload_config(self):
        mysql_url = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL")
        
        if mysql_url:
            if mysql_url.startswith("mysql+pymysql://"):
                mysql_url = mysql_url.replace("mysql+pymysql://", "mysql://")
            
            parsed = urlparse(mysql_url)
            self.host = parsed.hostname or "localhost"
            self.port = parsed.port or 3306
            self.user = parsed.username or "root"
            self.password = parsed.password or ""
            self.database = parsed.path.lstrip("/") or "student_report_db"
            
            query_params = parse_qs(parsed.query)
            ssl_mode = os.getenv("MYSQL_SSL_MODE") or query_params.get("ssl_mode", [None])[0] or query_params.get("ssl", [None])[0]
            self.ssl_config = {"ssl": True} if ssl_mode and str(ssl_mode).lower() not in ["disabled", "false", "0"] else None
        else:
            self.host = os.getenv("MYSQL_HOST", "localhost")
            self.port = int(os.getenv("MYSQL_PORT", "3306"))
            self.user = os.getenv("MYSQL_USER", "root")
            self.password = os.getenv("MYSQL_PASSWORD", "rootpassword")
            self.database = os.getenv("MYSQL_DATABASE", "student_report_db")
            
            ssl_mode = os.getenv("MYSQL_SSL_MODE") or os.getenv("MYSQL_SSL")
            self.ssl_config = {"ssl": True} if ssl_mode and str(ssl_mode).lower() not in ["disabled", "false", "0"] else None

    def get_connection(self, create_db_if_missing: bool = False):
        self.reload_config()
        kwargs = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "autocommit": True,
            "cursorclass": DictCursor,
            "connect_timeout": 10,
        }

        if self.ssl_config:
            kwargs["ssl"] = self.ssl_config

        if not create_db_if_missing:
            kwargs["database"] = self.database

        return pymysql.connect(**kwargs)

    def init_db(self):
        try:
            try:
                conn = self.get_connection(create_db_if_missing=True)
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn.close()
            except Exception as e:
                logger.info(f"Note on DB creation: {e}")

            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    roll_no VARCHAR(50) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY idx_student_roll_class (roll_no, class_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    roll_no VARCHAR(50) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_att_roll_class (roll_no, class_name),
                    INDEX idx_att_date (date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS tests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    roll_no VARCHAR(50) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    marks DECIMAL(5,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_tests_roll_class (roll_no, class_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS exams (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    roll_no VARCHAR(50) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    marks DECIMAL(5,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_exams_roll_class (roll_no, class_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS whatsapp_sessions (
                    sender_phone VARCHAR(100) PRIMARY KEY,
                    roll_no VARCHAR(50) NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

            conn.close()
            logger.info("✅ MySQL database and tables initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MySQL database: {e}")
            raise

    def execute_query(self, query: str, args=None, fetchall: bool = True, fetchone: bool = False):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, args or ())
                if fetchone:
                    return cursor.fetchone()
                if fetchall:
                    return cursor.fetchall()
                return cursor.rowcount
        finally:
            conn.close()

    def execute_many(self, query: str, args_list: list):
        if not args_list:
            return 0
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                count = cursor.executemany(query, args_list)
                return count
        finally:
            conn.close()

    def save_session(self, sender_phone: str, roll_no: str, class_name: str, name: str):
        q = """
        INSERT INTO whatsapp_sessions (sender_phone, roll_no, class_name, name)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE roll_no = VALUES(roll_no), class_name = VALUES(class_name), name = VALUES(name);
        """
        try:
            self.execute_query(q, (sender_phone, roll_no, class_name, name), fetchall=False)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def get_session(self, sender_phone: str) -> dict | None:
        q = "SELECT roll_no, class_name, name FROM whatsapp_sessions WHERE sender_phone = %s"
        try:
            return self.execute_query(q, (sender_phone,), fetchone=True)
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

    def delete_session(self, sender_phone: str):
        q = "DELETE FROM whatsapp_sessions WHERE sender_phone = %s"
        try:
            self.execute_query(q, (sender_phone,), fetchall=False)
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")

db_service = DatabaseService()
