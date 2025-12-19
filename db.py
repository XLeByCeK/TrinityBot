import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash

from flask import session

import datetime
import json

import api

#------------BOT---------

def get_conn():
    return psycopg2.connect(
        dbname="trinitybot",
        user="postgres",
        password="",
        host="localhost",
        port=5432
    )




def register_organization(inn: int, data):
    
    fns_data = api.fetch_org_from_fns(inn)

    if fns_data:
        name = fns_data["name"]
        is_active = fns_data["is_active"]

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT org_id, name, is_active
                    FROM organizations
                    WHERE inn = %s
                """, (inn,))
                
                row = cur.fetchone()

                if row:
                    org_id, old_name, old_is_active = row

                    if (old_name != name) or (old_is_active != is_active):
                        cur.execute("""
                            UPDATE organizations
                            SET name = %s,
                                is_active = %s,
                                fetched_at = NOW()
                            WHERE org_id = %s
                        """, (name, is_active, org_id))

                    return org_id

                cur.execute("""
                    INSERT INTO organizations (inn, name, is_active, fetched_at)
                    VALUES (%s, %s, %s, NOW())
                    RETURNING org_id
                """, (inn, name, is_active))

                return cur.fetchone()[0]
    else:

        return None


def create_user(first_name: str, last_name: str, max_user_id: int,):

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT max_user_id FROM users WHERE max_user_id = %s", (max_user_id,))
            if cur.fetchone():
                return

            cur.execute("""
                INSERT INTO users (first_name, last_name, max_user_id, created_at)
                VALUES (%s, %s, %s, NOW())
            """, ( first_name, last_name, max_user_id))



def create_chat(max_chat_id: int):

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT max_chat_id FROM chats WHERE max_chat_id = %s", (max_chat_id,))
            if cur.fetchone():
                return

            cur.execute("""
                INSERT INTO chats (created_at, max_chat_id)
                VALUES (NOW(), %s)
            """, (max_chat_id,))




def link_user_to_org(max_user_id: int, org_id: int):

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO usersorg (max_user_id, org_id, registered_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT DO NOTHING
            """, (max_user_id, org_id))


def link_org_to_chat(org_id: int, max_chat_id: int):

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO orgschats (org_id, max_chat_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT DO NOTHING
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
    if attachments:

        msg_type = attachments[0].get("type", "unknown")
    else:

        msg_type = "text"

    timestamp_ms = data.get("timestamp")
    received_at = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0)

    create_user(sender.get("first_name"), sender.get("last_name"), max_user_id)
    create_chat(max_chat_id)


    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO messages (max_chat_id, max_user_id, content, message_type, received_at, raw_json)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (

                max_chat_id,
                max_user_id,
                text,
                msg_type,
                received_at,
                json.dumps(data, ensure_ascii=False)

            ))



def get_organization_name(inn: int):

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT name FROM organizations WHERE inn = %s",
                (inn,)
            )

            result = cur.fetchone()
            return result[0] if result else None
        
def is_user_authorized(max_user_id: int):

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT org_id 
                FROM usersorg
                WHERE max_user_id = %s
                LIMIT 1
            """, (max_user_id,))

            row = cur.fetchone()

            if row:
                return True
              
            else:
                return False

def mark_support_requested(chat_id):

    with get_conn() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                UPDATE chats SET support_requested = TRUE WHERE max_chat_id = %s
            """, (
                chat_id
            ))

#-----------WEB---------

def get_webuser_by_login(login: str):

    with get_conn() as conn:

        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("""
                SELECT web_user_id, login, password_hash
                FROM webusers
                WHERE login = %s
            """, (login,))

            return cur.fetchone()

def authenticate_webuser(login: str, password: str):

    webuser = get_webuser_by_login(login)

    if not webuser:
        return None

    if check_password_hash(webuser["password_hash"], password):
        return webuser

    return None

def get_messages_log(
    date_from=None,
    date_to=None,
    org_id=None,
    chat_id=None,
    user_query=None,
    text_query=None,
    limit=100,
    offset=0
):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            query = """
                SELECT
                    m.message_id,
                    m.content,
                    m.message_type,
                    m.received_at,

                    u.user_id,
                    u.first_name,
                    u.last_name,
                    u.max_user_id,

                    c.chat_id,

                    o.org_id,
                    o.name AS org_name

                FROM messages m
                JOIN users u ON u.max_user_id = m.max_user_id
                JOIN chats c ON c.max_chat_id = m.max_chat_id
                LEFT JOIN orgschats oc ON oc.max_chat_id = c.max_chat_id
                LEFT JOIN organizations o ON o.org_id = oc.org_id

                WHERE m.message_type != 'bot'
            """

            params = []

            if date_from:
                query += " AND m.received_at >= %s"
                params.append(date_from)

            if date_to:
                query += " AND m.received_at <= %s"
                params.append(date_to)

            if org_id:
                query += " AND o.org_id = %s"
                params.append(org_id)

            if chat_id:
                query += " AND c.chat_id = %s"
                params.append(chat_id)

            if user_query:
                query += """
                    AND (
                        u.first_name ILIKE %s
                        OR u.last_name ILIKE %s
                        OR CAST(u.max_user_id AS TEXT) ILIKE %s
                    )
                """
                params.extend([f"%{user_query}%"] * 3)

            if text_query:
                query += " AND m.content ILIKE %s"
                params.append(f"%{text_query}%")

            query += """
                ORDER BY m.received_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])

            cur.execute(query, params)

            return cur.fetchall()

def get_organizations():
    with get_conn() as conn:

        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("""
                SELECT org_id, name
                FROM organizations
                ORDER BY name
            """)

            return cur.fetchall()


def get_chats():
    with get_conn() as conn:

        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("""
                SELECT
                    c.chat_id,
                    c.max_chat_id,
                    c.created_at,
                    o.name AS org_name,
                    COUNT(m.message_id) AS messages_count,
                    MAX(m.received_at) AS last_message_at
                FROM chats c
                LEFT JOIN orgschats oc ON oc.max_chat_id = c.max_chat_id
                LEFT JOIN organizations o ON o.org_id = oc.org_id
                LEFT JOIN messages m ON m.max_chat_id = c.max_chat_id
                GROUP BY
                    c.chat_id,
                    c.max_chat_id,
                    c.created_at,
                    o.name
                ORDER BY last_message_at DESC NULLS LAST
            """)

            return cur.fetchall()

def get_clients(search=None):
    with get_conn() as conn:

        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            sql = """
                SELECT
                    o.org_id,
                    o.inn,
                    o.name,
                    o.is_active,
                    COUNT(DISTINCT uo.max_user_id) AS users_count,
                    COUNT(DISTINCT oc.max_chat_id) AS chats_count
                FROM organizations o
                LEFT JOIN usersorg uo ON uo.org_id = o.org_id
                LEFT JOIN orgschats oc ON oc.org_id = o.org_id
            """

            params = []

            if search:

                sql += " WHERE o.name ILIKE %s OR o.inn::text LIKE %s "
                params += [f"%{search}%", f"%{search}%"]

            sql += " GROUP BY o.org_id ORDER BY o.name"

            cur.execute(sql, params)

            return cur.fetchall()

def get_users(search=None):

    with get_conn() as conn:

        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            sql = """
                SELECT
                    u.user_id,
                    u.max_user_id,
                    u.first_name,
                    u.last_name,
                    o.name AS org_name,
                    COUNT(m.message_id) AS messages_count,
                    MAX(m.received_at) AS last_message_at
                FROM users u
                LEFT JOIN usersorg uo ON uo.max_user_id = u.max_user_id
                LEFT JOIN organizations o ON o.org_id = uo.org_id
                LEFT JOIN messages m ON m.max_user_id = u.max_user_id
            """

            params = []
            if search:
                sql += " WHERE u.first_name ILIKE %s OR u.last_name ILIKE %s "
                params += [f"%{search}%", f"%{search}%"]

            sql += """
                GROUP BY
                    u.user_id,
                    u.max_user_id,
                    u.first_name,
                    u.last_name,
                    o.name
                ORDER BY last_message_at DESC NULLS LAST
            """

            cur.execute(sql, params)

            return cur.fetchall()

def get_support_chats():
    with get_conn() as conn:

        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("""
                SELECT
                    c.max_chat_id,
                    o.name AS org_name,
                    c.support_requested,
                    MAX(c.created_at) AS created_at
                FROM chats c
                LEFT JOIN orgschats oc ON oc.max_chat_id = c.max_chat_id
                LEFT JOIN organizations o ON o.org_id = oc.org_id
                GROUP BY c.max_chat_id, o.name, c.support_requested
                ORDER BY created_at DESC
            """)

            return cur.fetchall()
        
def get_chat_messages(max_chat_id: int):

    with get_conn() as conn:

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    content,
                    received_at AS created_at,
                    'user' AS sender
                FROM messages
                WHERE max_chat_id = %s

                UNION ALL

                SELECT
                    content,
                    sent_at AS created_at,
                    'bot' AS sender
                FROM outgoingmessages
                WHERE max_chat_id = %s

                ORDER BY created_at
            """, (max_chat_id, max_chat_id))

            return cur.fetchall()

def save_outgoing_message(max_chat_id: int, text: str):
    
    max_user_id = get_max_user_id(max_chat_id)

    with get_conn() as conn:
        with conn.cursor() as cur:

            web_user_id = session["web_user_id"]


            cur.execute("""
                INSERT INTO outgoingmessages
                (max_chat_id, max_user_id, web_user_id, content, sent_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (
                max_chat_id,
                max_user_id,
                web_user_id,
                text
            ))

def get_max_user_id(max_chat_id: int) -> int:

    with get_conn() as conn:

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT max_user_id
                FROM messages
                WHERE max_chat_id = %s
                ORDER BY received_at
                LIMIT 1
            """, (max_chat_id,))

            row = cur.fetchone()
            return row["max_user_id"] if row else None
        
def get_new_support_requests_count():

    with get_conn() as conn:
        
        with conn.cursor() as cur:

            cur.execute(
                "SELECT COUNT(*) FROM chats WHERE support_requested = TRUE"
            )

            result = cur.fetchone()
            return result[0] if result else None


def mark_support_handled(chat_id):

    with get_conn() as conn:

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

            cur.execute("""
                UPDATE chats SET support_requested = FALSE WHERE max_chat_id = %s
            """, (chat_id,))
