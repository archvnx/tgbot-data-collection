import aiosqlite
import asyncio
from datetime import datetime, timezone, timedelta
MSK = timezone(timedelta(hours=3))
def now_msk():
    return datetime.now(MSK).strftime("%d-%m-%Y %H:%M:%S")

u_db="database/users_data_base.db"
async def init_db():
    async with aiosqlite.connect(u_db) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.commit()
        await db.execute("""CREATE TABLE IF NOT EXISTS users 
                         (id INTEGER PRIMARY KEY, 
                         user_id INTEGER UNIQUE, 
                         is_banned INTEGER DEFAULT 0, 
                         created_at TIMESTAMP)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS stories 
                         (id INTEGER PRIMARY KEY, 
                         user_id INTEGER, 
                         text_start TEXT,
                         text_finish TEXT,
                         photo_id_start TEXT,
                         photo_id_finish TEXT,
                         status TEXT DEFAULT 'на рассмотрении',
                         moderation_admin_id INTEGER,
                         moderation_time TIMESTAMP,
                         created_at TIMESTAMP,
                         FOREIGN KEY (user_id) REFERENCES users (user_id))""")
        await db.commit()

async def add_users(user_id):
    async with aiosqlite.connect(u_db) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, created_at) VALUES (?, ?)", (user_id, now_msk()))
        await db.commit()


async def add_discussion(user_id,text_created,photo_created):
    async with aiosqlite.connect(u_db) as db:
        await db.execute("INSERT INTO stories (user_id, text_start, photo_id_start, created_at) VALUES (?,?,?,?)", (user_id, text_created, photo_created, now_msk()))
        await db.commit()

            


                
