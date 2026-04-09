"""
Database Module
===============
PostgreSQL database operations using asyncpg connection pooling.

Schema:
- users: Stores Telegram user ID, notification time, language, timezone
- busy_slots: Stores recurring busy time periods per user per day of week

The module handles automatic table creation and schema migrations on connect.
"""

import asyncpg
import asyncio
from config import *


class Database:
    """
    Asyncpg-based database wrapper with connection pooling.

    Manages user preferences (language, timezone, notification time)
    and busy time slots for the weekly schedule. Connects with automatic
    retry logic (10 attempts, 2-second interval) on startup.
    """

    def __init__(self):
        self.pool = None

    async def connect(self):
        """
        Establish connection pool and initialize/upgrade database schema.

        Retries up to 10 times with 2-second delays on connection failure.
        Creates tables if they don't exist and runs schema migrations
        to add columns that may be missing in older database versions.
        """
        for _ in range(10):
            try:
                self.pool = await asyncpg.create_pool(
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    host=DB_HOST
                )

                async with self.pool.acquire() as conn:
                    # Create users table (first-time setup)
                    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id BIGINT PRIMARY KEY,
                        notification_time TIME DEFAULT TIME '09:00',
                        language TEXT DEFAULT 'ru',
                        timezone TEXT DEFAULT 'UTC'
                    );
                    """)

                    # Schema migrations for existing databases
                    # These are safe to run even if columns already exist
                    await conn.execute("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_time TIME DEFAULT TIME '09:00';
                    """)
                    await conn.execute("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'ru';
                    """)
                    await conn.execute("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'UTC';
                    """)

                    # Create busy_slots table
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
        """
        Insert a new user or do nothing if already exists.

        Args:
            user_id: Telegram user ID (BIGINT).
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users(id) VALUES($1) ON CONFLICT DO NOTHING",
                user_id
            )

    async def set_notification_time(self, user_id, time):
        """
        Update user's daily notification time.

        Args:
            user_id: Telegram user ID.
            time: datetime.time object for notification time.
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET notification_time=$1 WHERE id=$2",
                time, user_id
            )

    async def get_notification_time(self, user_id):
        """
        Retrieve user's notification time.

        Returns:
            datetime.time object or None if not set.
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT notification_time FROM users WHERE id=$1",
                user_id
            )
            return result

    async def set_language(self, user_id, lang):
        """
        Update user's interface language preference.

        Args:
            user_id: Telegram user ID.
            lang: Language code string ("ru" or "en").
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET language=$1 WHERE id=$2",
                lang, user_id
            )

    async def get_language(self, user_id):
        """
        Get user's language preference, defaulting to "ru".

        Returns:
            Language code string ("ru" or "en").
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT language FROM users WHERE id=$1",
                user_id
            )
            return result or 'ru'

    async def set_timezone(self, user_id, tz):
        """
        Update user's timezone.

        Args:
            user_id: Telegram user ID.
            tz: IANA timezone string (e.g. "Europe/Moscow", "UTC").
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET timezone=$1 WHERE id=$2",
                tz, user_id
            )

    async def get_timezone(self, user_id):
        """
        Get user's timezone, defaulting to "UTC".

        Returns:
            IANA timezone string.
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT timezone FROM users WHERE id=$1",
                user_id
            )
            return result or 'UTC'

    async def add_busy(self, user_id, day, start, end):
        """
        Add a busy time slot for a user on a specific day of week.

        Args:
            user_id: Telegram user ID.
            day: Day of week (0=Monday, 6=Sunday).
            start: Start time (datetime.time).
            end: End time (datetime.time).
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO busy_slots(user_id, day_of_week, start_time, end_time)
                VALUES($1,$2,$3,$4)
                """,
                user_id, day, start, end
            )

    async def get_users(self):
        """
        Fetch all users with their notification preferences.

        Returns:
            List of dicts with keys: id, notification_time, language, timezone.
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT id, notification_time, language, timezone FROM users")

    async def get_busy_for_day(self, user_id, day):
        """
        Get all busy slots for a user on a specific day of week.

        Args:
            user_id: Telegram user ID.
            day: Day of week (0=Monday, 6=Sunday).

        Returns:
            List of dicts with start_time and end_time.
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT start_time, end_time FROM busy_slots WHERE user_id=$1 AND day_of_week=$2",
                user_id, day
            )

    async def check_conflict(self, user_id, day, start_time, end_time):
        """
        Check if a new busy slot overlaps with existing ones.

        Two intervals [a, b) and [c, d) overlap if a < d AND c < b.

        Args:
            user_id: Telegram user ID.
            day: Day of week (0=Monday, 6=Sunday).
            start_time: Proposed start time.
            end_time: Proposed end time.

        Returns:
            True if conflict exists, False otherwise.
        """
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
        """
        Get all busy slots for a user across all days of week.

        Args:
            user_id: Telegram user ID.

        Returns:
            List of dicts with keys: id, day_of_week, start_time, end_time.
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT id, day_of_week, start_time, end_time FROM busy_slots WHERE user_id=$1",
                user_id
            )

    async def delete_busy(self, slot_id):
        """
        Remove a busy slot by its ID.

        Args:
            slot_id: Primary key of the busy_slots row.
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM busy_slots WHERE id=$1",
                slot_id
            )
