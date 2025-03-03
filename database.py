import sqlite3
import aiosqlite

DB_NAME = 'db.db'


def create_db():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tokens
                      (token TEXT,
                       group_id TEXT,
                       active BOOLEAN,
                       params TEXT)''')

    connect.commit()
    cursor.close()
    return


async def add_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        data = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        row = await data.fetchone()

        if row is None:
            await db.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            await db.commit()
            return True
        else:
            return False


async def add_token(token, group_id, active=True, params=None):
    async with aiosqlite.connect(DB_NAME) as db:
        # Проверяем, существует ли группа с таким group_id
        data = await db.execute('SELECT group_id FROM tokens WHERE group_id = ?', (group_id,))
        row = await data.fetchone()

        if row is None:
            # Если группа не существует, добавляем новый токен
            await db.execute('INSERT INTO tokens (token, group_id, active, params) VALUES (?, ?, ?, ?)', (token, group_id, active, params))
            await db.commit()
            return True
        else:
            # Если группа существует, обновляем токен для этой группы
            await db.execute('''
                UPDATE tokens 
                SET token = ?, active = ?, params = ? 
                WHERE group_id = ?
            ''', (token, active, params, group_id))
            await db.commit()
            return True


async def update_toggle_status(group_id, active):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE tokens SET active = ? WHERE group_id = ?', (active, group_id))
        await db.commit()
        return True


async def get_chat_info(group_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT token, active, params 
            FROM tokens 
            WHERE group_id = ?
        ''', (group_id,))
        row = await cursor.fetchone()

        if row:
            token, active, params = row
            return {
                'token': token,
                'active': active,
                'params': params
            }
        else:
            return None


async def get_active_tokens():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT token, group_id, params FROM tokens WHERE active != ?', (False,))
        rows = await cursor.fetchall()
        return rows
