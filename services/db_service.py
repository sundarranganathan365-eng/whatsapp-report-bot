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
            # Parse connection URL if provided by Cloud provider (e.g., mysql://user:pass@host:port/dbname)
            if mysql_url.startswith("mysql+pymysql://"):
                mysql_url = mysql_url.replace("mysql+pymysql://", "mysql://")
            
            parsed = urlparse(mysql_url)
            self.host = parsed.hostname or "localhost"
            self.port = parsed.port or 3306
            self.user = parsed.username or "root"
            self.password = parsed.password or ""
            self.database = parsed.path.lstrip("/") or "student_report_db"
            
            # Check for SSL options in URL query params or ENV
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
        """
        Creates and returns a PyMySQL database connection.
        """
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
        """
        Ensures the database and required tables exist on Cloud/Local MySQL.
        """
        try:
            # 1. Attempt to create database if permitted (ignore if already exists or permission denied on managed DBs)
            try:
                conn = self.get_connection(create_db_if_missing=True)
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn.close()
            except Exception as e:
                logger.info(f"Note on DB creation (normal for managed Cloud DBs): {e}")

            # 2. Ensure Tables Exist
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # Students table
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

                # Attendance table
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

                # Tests table
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

                # Exams table
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

            conn.close()
            logger.info("✅ MySQL database and tables initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MySQL database: {e}")
            raise

    def execute_query(self, query: str, args=None, fetchall: bool = True, fetchone: bool = False):
        """
        Executes a SQL query and returns dictionary records or rowcount.
        """
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
        """
        Executes batch insert/update queries.
        """
        if not args_list:
            return 0
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                count = cursor.executemany(query, args_list)
                return count
        finally:
            conn.close()

db_service = DatabaseService()
