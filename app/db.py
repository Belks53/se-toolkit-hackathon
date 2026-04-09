import asyncpg
import asyncio
from config import *

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        for _ in range(10):
            try:
                self.pool = await asyncpg.create_pool(
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    host=DB_HOST
                )

                async with self.pool.acquire() as conn:
                    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id BIGINT PRIMARY KEY,
                        notification_time TIME DEFAULT TIME '09:00',
                        language TEXT DEFAULT 'ru',
                        timezone TEXT DEFAULT 'UTC'
                    );
                    """)

                    # Migrations
                    await conn.execute("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_time TIME DEFAULT TIME '09:00';
                    """)
                    await conn.execute("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'ru';
                    """)
                    await conn.execute("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'UTC';
                    """)

                    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS busy_slots (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES users(id),
                        day_of_week INTEGER,
                        start_time TIME,
                        end_time TIME
                    );
                    """)

                print("DB connected ✅")
                return

            except Exception:
                print("DB retry...")
                await asyncio.sleep(2)

        raise Exception("DB connection failed")

    async def add_user(self, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users(id) VALUES($1) ON CONFLICT DO NOTHING",
                user_id
            )

    async def set_notification_time(self, user_id, time):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET notification_time=$1 WHERE id=$2",
                time, user_id
            )

    async def get_notification_time(self, user_id):
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT notification_time FROM users WHERE id=$1",
                user_id
            )
            return result

    async def set_language(self, user_id, lang):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET language=$1 WHERE id=$2",
                lang, user_id
            )

    async def get_language(self, user_id):
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT language FROM users WHERE id=$1",
                user_id
            )
            return result or 'ru'

    async def set_timezone(self, user_id, tz):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET timezone=$1 WHERE id=$2",
                tz, user_id
            )

    async def get_timezone(self, user_id):
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT timezone FROM users WHERE id=$1",
                user_id
            )
            return result or 'UTC'

    async def add_busy(self, user_id, day, start, end):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO busy_slots(user_id, day_of_week, start_time, end_time)
                VALUES($1,$2,$3,$4)
                """,
                user_id, day, start, end
            )

    async def get_users(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT id, notification_time, language, timezone FROM users")

    async def get_busy_for_day(self, user_id, day):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT start_time, end_time FROM busy_slots WHERE user_id=$1 AND day_of_week=$2",
                user_id, day
            )

    async def check_conflict(self, user_id, day, start_time, end_time):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id FROM busy_slots
                WHERE user_id=$1 AND day_of_week=$2
                AND start_time < $3 AND end_time > $4
                """,
                user_id, day, end_time, start_time
            )
            return len(rows) > 0

    async def get_all_busy(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT id, day_of_week, start_time, end_time FROM busy_slots WHERE user_id=$1",
                user_id
            )

    async def delete_busy(self, slot_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM busy_slots WHERE id=$1",
                slot_id
            )