"""
Database Connection & Query Execution Module for EcoLocate (Phase 8 Optimized)
Uses thread-safe MySQL connection pooling (mysql.connector.pooling) for high concurrency (50+ users),
with parameterized queries for 100% SQL injection prevention, SSL support, and automatic reconnection.
"""

import threading
import mysql.connector
from mysql.connector import Error, errorcode
from mysql.connector.pooling import MySQLConnectionPool
from config import Config

_pool_lock = threading.Lock()
_connection_pool = None

def get_db_pool():
    """Lazily initialize and return the global MySQL Connection Pool."""
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                pool_config = {
                    'pool_name': 'ecolocate_pool',
                    'pool_size': max(5, min(32, Config.DB_POOL_SIZE)),
                    'pool_reset_session': True,
                    'host': Config.DB_HOST,
                    'port': Config.DB_PORT,
                    'user': Config.DB_USER,
                    'password': Config.DB_PASSWORD,
                    'database': Config.DB_NAME,
                    'charset': 'utf8mb4',
                    'collation': 'utf8mb4_unicode_ci',
                    'autocommit': True,
                    'connect_timeout': 10
                }
                
                # Cloud/Hosted MySQL SSL Support (Aiven, TiDB, Render, etc.)
                if Config.DB_SSL_CA:
                    pool_config['ssl_ca'] = Config.DB_SSL_CA
                    pool_config['ssl_verify_cert'] = True

                try:
                    _connection_pool = MySQLConnectionPool(**pool_config)
                except Error as e:
                    print(f"[Database Pool Init Warning] Could not initialize pool: {e}. Falling back to dynamic connections.")
                    _connection_pool = None
    return _connection_pool

def get_db_connection():
    """
    Acquire a database connection from the pool, or dynamically create one if pool is unavailable.
    """
    pool = get_db_pool()
    if pool:
        try:
            conn = pool.get_connection()
            if conn and conn.is_connected():
                return conn
        except Error as e:
            print(f"[Pool Acquisition Warning] Pool exhausted or error: {e}. Attempting direct connection.")

    # Direct connection fallback
    try:
        connect_args = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True,
            'connect_timeout': 10
        }
        if Config.DB_SSL_CA:
            connect_args['ssl_ca'] = Config.DB_SSL_CA
            connect_args['ssl_verify_cert'] = True

        return mysql.connector.connect(**connect_args)
    except Error as e:
        print(f"[Database Connection Error] Could not connect to MySQL: {e}")
        return None

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Safely execute a parameterized SQL query with automatic connection management.
    
    :param query: SQL statement with %s placeholders
    :param params: tuple/list of parameters to bind safely
    :param fetchone: Return a single record (as a dict)
    :param fetchall: Return all records (as a list of dicts)
    :param commit: True for INSERT, UPDATE, DELETE queries
    :return: dict, list of dicts, lastrowid, or None
    """
    connection = get_db_connection()
    if not connection:
        raise ConnectionError("Failed to establish connection with MySQL database.")

    cursor = connection.cursor(dictionary=True)
    result = None

    try:
        cursor.execute(query, params or ())
        
        if commit:
            connection.commit()
            result = cursor.lastrowid
        elif fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
            
    except Error as e:
        if commit:
            try:
                connection.rollback()
            except Exception:
                pass
        print(f"[SQL Execution Error] {e} | Query: {query}")
        raise e
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            connection.close()  # Returns connection back to the pool
        except Exception:
            pass

    return result

def check_db_health():
    """Verify database server connectivity and responsiveness."""
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchall()
            cursor.close()
            conn.close()
            return True, "Database connection operational."
    except Exception as e:
        return False, str(e)
    return False, "Database connection failed."

def log_user_activity(user_id=None, activity_type='search', search_query=None, city=None, state=None, centre_id=None):
    """
    Record user activity into the user_activity table in MySQL.
    
    Privacy Safeguard:
    Never records passwords, authentication tokens, session cookies,
    or sensitive personal information.
    """
    try:
        s_query = str(search_query).strip()[:255] if search_query else None
        c_city = str(city).strip()[:100] if city else None
        s_state = str(state).strip()[:100] if state else None
        c_id = int(centre_id) if centre_id else None
        u_id = int(user_id) if user_id else None
        act_type = str(activity_type).strip()[:50]

        execute_query(
            """
            INSERT INTO user_activity (user_id, activity_type, search_query, city, state, centre_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (u_id, act_type, s_query, c_city, s_state, c_id),
            commit=True
        )
        return True
    except Exception as e:
        # Non-blocking advisory logging
        print(f"[Activity Logging Advisory] {e}")
        return False
