import psycopg2
from psycopg2.extras import RealDictCursor

import datetime
import json

import api



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
