import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash
from flask import session
import datetime
import json
import api
from typing import Any, List, Optional, Dict
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "trinitybot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432))
}

def get_conn():

    return psycopg2.connect(**DB_CONFIG)

def _execute_query(query: str, params: tuple = (), fetch: str = None, use_dict: bool = False):

    factory = RealDictCursor if use_dict else None
    with get_conn() as conn:
        with conn.cursor(cursor_factory=factory) as cur:
            cur.execute(query, params)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()
            if fetch == "scalar":
                res = cur.fetchone()
                return res[0] if res else None
            return None


# --- Инициализация и обновление структуры БД ---

def init_db():

    commands = [
        """
        CREATE TABLE IF NOT EXISTS organizations (
            org_id SERIAL PRIMARY KEY,
            inn BIGINT UNIQUE NOT NULL,
            name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            fetched_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            max_user_id BIGINT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS chats (
            chat_id SERIAL PRIMARY KEY,
            max_chat_id BIGINT UNIQUE NOT NULL,
            report_type INT DEFAULT 4,
            support_requested BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP
        )
        """,
        "CREATE TABLE IF NOT EXISTS usersorg (max_user_id BIGINT, org_id INT, registered_at TIMESTAMP, PRIMARY KEY(max_user_id, org_id))",
        "CREATE TABLE IF NOT EXISTS orgschats (org_id INT, max_chat_id BIGINT, created_at TIMESTAMP, PRIMARY KEY(org_id, max_chat_id))",
        """
        CREATE TABLE IF NOT EXISTS messages (
            message_id SERIAL PRIMARY KEY,
            max_chat_id BIGINT,
            max_user_id BIGINT,
            content TEXT,
            message_type TEXT,
            received_at TIMESTAMP,
            raw_json JSONB
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS construction_objects (
            object_id SERIAL PRIMARY KEY,
            max_chat_id BIGINT,
            name TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS webusers (
            web_user_id SERIAL PRIMARY KEY,
            login TEXT UNIQUE,
            password_hash TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS outgoingmessages (
            id SERIAL PRIMARY KEY,
            max_chat_id BIGINT,
            max_user_id BIGINT,
            web_user_id INT,
            content TEXT,
            sent_at TIMESTAMP
        )
        """
    ]

    with get_conn() as conn:
        with conn.cursor() as cur:

            for cmd in commands:
                cur.execute(cmd)
            

            alter_queries = [
                ("chats", "support_requested", "ALTER TABLE chats ADD COLUMN support_requested BOOLEAN DEFAULT FALSE"),
                ("chats", "report_type", "ALTER TABLE chats ADD COLUMN report_type INT DEFAULT 4"),
                ("messages", "raw_json", "ALTER TABLE messages ADD COLUMN raw_json JSONB")
            ]

            for table, column, alter_cmd in alter_queries:
                cur.execute(f"""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='{table}' AND column_name='{column}'
                """)
                if not cur.fetchone():
                    cur.execute(alter_cmd)
                    print(f"Обновлена структура БД: добавлена колонка {column} в таблицу {table}")

        conn.commit()


init_db()

# ------------ BOT ------------


def register_organization(inn: int, data: Any = None):
    fns_data = api.fetch_org_from_fns(inn)
    if not fns_data:
        return None

    name = fns_data["name"]
    is_active = fns_data["is_active"]

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT org_id, name, is_active FROM organizations WHERE inn = %s", (inn,))
            row = cur.fetchone()

            if row:
                org_id, old_name, old_is_active = row
                if (old_name != name) or (old_is_active != is_active):
                    cur.execute("""
                        UPDATE organizations 
                        SET name = %s, is_active = %s, fetched_at = NOW() 
                        WHERE org_id = %s
                    """, (name, is_active, org_id))
                return org_id

            cur.execute("""
                INSERT INTO organizations (inn, name, is_active, fetched_at)
                VALUES (%s, %s, %s, NOW()) RETURNING org_id
            """, (inn, name, is_active))
            return cur.fetchone()[0]

def create_user(first_name: str, last_name: str, max_user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE max_user_id = %s", (max_user_id,))
            if cur.fetchone():
                return
            cur.execute("""
                INSERT INTO users (first_name, last_name, max_user_id, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (first_name, last_name, max_user_id))

def is_chat_authorized(max_chat_id: int) -> bool:
    res = _execute_query("SELECT 1 FROM orgschats WHERE max_chat_id = %s", (max_chat_id,), fetch="one")
    return res is not None

def get_inn_by_chat(max_chat_id: int):
    return _execute_query("""
        SELECT o.inn FROM organizations o
        JOIN orgschats oc ON o.org_id = oc.org_id
        WHERE oc.max_chat_id = %s LIMIT 1
    """, (max_chat_id,), fetch="scalar")

def create_chat(max_chat_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM chats WHERE max_chat_id = %s", (max_chat_id,))
            if cur.fetchone():
                return
            cur.execute("INSERT INTO chats (created_at, max_chat_id) VALUES (NOW(), %s)", (max_chat_id,))

def get_user_inn(max_user_id: int):
    return _execute_query("""
        SELECT o.inn FROM organizations o
        JOIN usersorg uo ON o.org_id = uo.org_id
        WHERE uo.max_user_id = %s LIMIT 1
    """, (max_user_id,), fetch="scalar")

def link_user_to_org(max_user_id: int, org_id: int):
    _execute_query("""
        INSERT INTO usersorg (max_user_id, org_id, registered_at)
        VALUES (%s, %s, NOW()) ON CONFLICT DO NOTHING
    """, (max_user_id, org_id))

def link_org_to_chat(org_id: int, max_chat_id: int):
    _execute_query("""
        INSERT INTO orgschats (org_id, max_chat_id, created_at)
        VALUES (%s, %s, NOW()) ON CONFLICT DO NOTHING
    """, (org_id, max_chat_id))

def save_incoming_message(data: dict):
    msg = data.get("message", {})
    body = msg.get("body", {})
    sender = msg.get("sender", {})
    recipient = msg.get("recipient", {})

    max_user_id = sender.get("user_id")
    max_chat_id = recipient.get("chat_id")
    text = body.get("text")
    
    attachments = body.get("attachments", [])
    msg_type = attachments[0].get("type", "unknown") if attachments else "text"
    
    received_at = datetime.datetime.fromtimestamp(data.get("timestamp", 0) / 1000.0)

    create_user(sender.get("first_name"), sender.get("last_name"), max_user_id)
    create_chat(max_chat_id)

    _execute_query("""
        INSERT INTO messages (max_chat_id, max_user_id, content, message_type, received_at, raw_json)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (max_chat_id, max_user_id, text, msg_type, received_at, json.dumps(data, ensure_ascii=False)))

def get_organization_name(inn: int):
    return _execute_query("SELECT name FROM organizations WHERE inn = %s", (inn,), fetch="scalar")

def is_user_authorized(max_user_id: int) -> bool:
    print(max_user_id)
    res = _execute_query("SELECT org_id FROM usersorg WHERE max_user_id = %s LIMIT 1", (max_user_id,), fetch="one")
    return res is not None

def add_construction_object(max_chat_id: int, name: str, address: str):
    _execute_query("""
        INSERT INTO construction_objects (max_chat_id, name, address)
        VALUES (%s, %s, %s)
    """, (max_chat_id, name, address))

def get_construction_objects(max_chat_id: int):
    return _execute_query("""
        SELECT object_id, name, address FROM construction_objects 
        WHERE max_chat_id = %s ORDER BY created_at ASC
    """, (max_chat_id,), fetch="all", use_dict=True)

def delete_construction_object(object_id: int):
    _execute_query("DELETE FROM construction_objects WHERE object_id = %s", (object_id,))

def get_construction_object_by_id(object_id: int):
    return _execute_query("SELECT * FROM construction_objects WHERE object_id = %s", (object_id,), fetch="one", use_dict=True)





# ----------- WEB -----------




def mark_support_requested(chat_id):
    _execute_query("UPDATE chats SET support_requested = TRUE WHERE max_chat_id = %s", (chat_id,))

def get_webuser_by_login(login: str):
    return _execute_query("""
        SELECT web_user_id, login, password_hash FROM webusers WHERE login = %s
    """, (login,), fetch="one", use_dict=True)

def authenticate_webuser(login: str, password: str):
    webuser = get_webuser_by_login(login)
    if webuser and check_password_hash(webuser["password_hash"], password):
        return webuser
    return None

def get_messages_log(date_from=None, date_to=None, org_id=None, chat_id=None, 
                     user_query=None, text_query=None, limit=100, offset=0):
    query = """
        SELECT m.message_id, m.content, m.message_type, m.received_at,
               u.user_id, u.first_name, u.last_name, u.max_user_id,
               c.chat_id, o.org_id, o.name AS org_name
        FROM messages m
        JOIN users u ON u.max_user_id = m.max_user_id
        JOIN chats c ON c.max_chat_id = m.max_chat_id
        LEFT JOIN orgschats oc ON oc.max_chat_id = c.max_chat_id
        LEFT JOIN organizations o ON o.org_id = oc.org_id
        WHERE m.message_type != 'bot'
    """
    params = []
    if date_from:
        query += " AND m.received_at >= %s"; params.append(date_from)
    if date_to:
        query += " AND m.received_at <= %s"; params.append(date_to)
    if org_id:
        query += " AND o.org_id = %s"; params.append(org_id)
    if chat_id:
        query += " AND c.chat_id = %s"; params.append(chat_id)
    if user_query:
        query += " AND (u.first_name ILIKE %s OR u.last_name ILIKE %s OR CAST(u.max_user_id AS TEXT) ILIKE %s)"
        params.extend([f"%{user_query}%"] * 3)
    if text_query:
        query += " AND m.content ILIKE %s"; params.append(f"%{text_query}%")

    query += " ORDER BY m.received_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    return _execute_query(query, tuple(params), fetch="all", use_dict=True)

def get_organizations():
    return _execute_query("SELECT org_id, name FROM organizations ORDER BY name", fetch="all", use_dict=True)

def get_chats():
    return _execute_query("""
        SELECT c.chat_id, c.max_chat_id, c.created_at, c.report_type, 
               o.name AS org_name, COUNT(m.message_id) AS messages_count,
               MAX(m.received_at) AS last_message_at
        FROM chats c
        LEFT JOIN orgschats oc ON oc.max_chat_id = c.max_chat_id
        LEFT JOIN organizations o ON o.org_id = oc.org_id
        LEFT JOIN messages m ON m.max_chat_id = c.max_chat_id
        GROUP BY c.chat_id, c.max_chat_id, c.created_at, o.name
        ORDER BY last_message_at DESC NULLS LAST
    """, fetch="all", use_dict=True)

def get_clients(search=None):
    sql = """
        SELECT o.org_id, o.inn, o.name, o.is_active,
               COUNT(DISTINCT uo.max_user_id) AS users_count,
               COUNT(DISTINCT oc.max_chat_id) AS chats_count
        FROM organizations o
        LEFT JOIN usersorg uo ON uo.org_id = o.org_id
        LEFT JOIN orgschats oc ON oc.org_id = o.org_id
    """
    params = []
    if search:
        sql += " WHERE o.name ILIKE %s OR o.inn::text LIKE %s"
        params += [f"%{search}%", f"%{search}%"]
    sql += " GROUP BY o.org_id ORDER BY o.name"
    return _execute_query(sql, tuple(params), fetch="all", use_dict=True)

def get_users(search=None):
    sql = """
        SELECT u.user_id, u.max_user_id, u.first_name, u.last_name, o.name AS org_name,
               COUNT(m.message_id) AS messages_count, MAX(m.received_at) AS last_message_at
        FROM users u
        LEFT JOIN usersorg uo ON uo.max_user_id = u.max_user_id
        LEFT JOIN organizations o ON o.org_id = uo.org_id
        LEFT JOIN messages m ON m.max_user_id = u.max_user_id
    """
    params = []
    if search:
        sql += " WHERE u.first_name ILIKE %s OR u.last_name ILIKE %s"
        params += [f"%{search}%", f"%{search}%"]
    sql += " GROUP BY u.user_id, u.max_user_id, u.first_name, u.last_name, o.name ORDER BY last_message_at DESC NULLS LAST"
    return _execute_query(sql, tuple(params), fetch="all", use_dict=True)

def get_support_chats():
    return _execute_query("""
        SELECT c.max_chat_id, o.name AS org_name, c.support_requested, MAX(c.created_at) AS created_at
        FROM chats c
        LEFT JOIN orgschats oc ON oc.max_chat_id = c.max_chat_id
        LEFT JOIN organizations o ON o.org_id = oc.org_id
        GROUP BY c.max_chat_id, o.name, c.support_requested
        ORDER BY created_at DESC
    """, fetch="all", use_dict=True)

def get_chat_messages(max_chat_id: int):
    return _execute_query("""
        SELECT m.content, m.received_at AS created_at, 'user' AS sender_role, u.first_name, u.last_name
        FROM messages m
        LEFT JOIN users u ON m.max_user_id = u.max_user_id
        WHERE m.max_chat_id = %s
        UNION ALL
        SELECT content, sent_at AS created_at, 'bot' AS sender_role, 'Система' AS first_name, 'Админ' AS last_name
        FROM outgoingmessages
        WHERE max_chat_id = %s
        ORDER BY created_at ASC
    """, (max_chat_id, max_chat_id), fetch="all", use_dict=True)

def save_outgoing_message(max_chat_id: int, text: str):
    max_user_id = get_max_user_id(max_chat_id)
    web_user_id = session.get("web_user_id")
    _execute_query("""
        INSERT INTO outgoingmessages (max_chat_id, max_user_id, web_user_id, content, sent_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (max_chat_id, max_user_id, web_user_id, text))

def get_max_user_id(max_chat_id: int) -> int:
    return _execute_query("""
        SELECT max_user_id FROM messages WHERE max_chat_id = %s 
        ORDER BY received_at LIMIT 1
    """, (max_chat_id,), fetch="scalar")

def get_new_support_requests_count():
    return _execute_query("SELECT COUNT(*) FROM chats WHERE support_requested = TRUE", fetch="scalar")

def mark_support_handled(chat_id):
    _execute_query("UPDATE chats SET support_requested = FALSE WHERE max_chat_id = %s", (chat_id,))

def update_chat_report_type(max_chat_id, report_type):
    _execute_query("UPDATE chats SET report_type = %s WHERE max_chat_id = %s", (report_type, max_chat_id))

def get_chat_report_type(max_chat_id):
    res = _execute_query("SELECT report_type FROM chats WHERE max_chat_id = %s", (max_chat_id,), fetch="scalar")
    return res if res is not None else 4