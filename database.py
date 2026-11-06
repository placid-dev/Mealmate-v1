import sqlite3
from contextlib import closing #To automatically close connection
DB_NAME="mealmate.db"

#1. USERS TABLE
def create_users_table():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor=conn.cursor()
        cursor.execute("PRAGMA foreign_keys= ON") #foreign key enforcement after declaring
        with conn:
            
            create_users_sql="""
            --sql
            CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            daily_budget INTEGER  DEFAULT 300,
            monthly_budget INTEGER GENERATED ALWAYS AS (daily_budget*30),
            current_daily_balance REAL NOT NULL,
            savings_balance REAL NOT NULL,
            last_weekly_reset DATE DEFAULT CURRENT_DATE,
            last_mothly_reset DATE DEFAULT CURRENT_DATE,
            last_daily_reset DATE
            );
            """
            cursor.execute(create_users_sql)

            #Databases created before last_daily_reset existed don't have the column yet
            columns=[row[1] for row in cursor.execute("PRAGMA table_info(users)")]
            if "last_daily_reset" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN last_daily_reset DATE")
            

#2. MENU ITEMS TABLE
def create_menu_items_table():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            cursor=conn.cursor()
            #3cursor.execute("PRAGMA foreign_keys= ON")
            create_menu_sql="""
            --sql
            CREATE TABLE IF NOT EXISTS menu_items(
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL,
            cost REAL NOT  NULL
            )
            ;
            """
            cursor.execute(create_menu_sql)

#3. PURCHASE HISTORY TABLE
def create_purchases_table():
    with closing(sqlite3.connect(DB_NAME)) as conn:
            cursor=conn.cursor()
            cursor.execute("PRAGMA foreign_keys= ON")
            with conn:
                
                create_purchases_sql="""
                --sql
                CREATE TABLE IF NOT EXISTS purchase_history(
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_name TEXT NOT NULL,
                cost REAL NOT NULL,
                purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
                ;
                """
                cursor.execute(create_purchases_sql)

#4. DAILY SUMMARIES TABLE
def create_daily_summaries_table():
    with closing(sqlite3.connect(DB_NAME)) as conn:
                cursor=conn.cursor()
                cursor.execute("PRAGMA foreign_keys= ON")
                with conn:
                    
                    create_daily_sumarries_sql="""
                    --sql
                    CREATE TABLE IF NOT EXISTS daily_summaries(
                    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    log_date DATE DEFAULT CURRENT_DATE,
                    allocated_budget REAL NOT NULL,
                    amount_spent REAL NOT NULL,
                    leftover_saved REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    UNIQUE(user_id,log_date)
                    );
                    """
                    cursor.execute(create_daily_sumarries_sql)
                    
#5. DATABASE INITIALIZATION
def initialize_database():
    create_users_table()
    create_purchases_table()
    create_daily_summaries_table()
    create_menu_items_table()

if __name__=="__main__":
    initialize_database()
    print("[SYSTEM]: Mealmate schema initialized and verified successfully! Hehe")
