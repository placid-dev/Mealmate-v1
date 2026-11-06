from contextlib import closing
import sqlite3
DB_NAME="mealmate.db"

#user creation
def create_user(username,daily_budget,savings_balance=0): #no manually entering user_id
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            cursor=conn.cursor()
            try:
                cursor.execute("""--sql
                INSERT INTO users (username,daily_budget,current_daily_balance,savings_balance)
                VALUES (?,?,?,?);
                """,(username,daily_budget,daily_budget,savings_balance))
                print(f"{username.title()} added successfully!")

                return cursor.lastrowid #returns the id of the new insterted user
                
            except sqlite3.IntegrityError:
                print(f"{username.title()} already exists.")   
            
            
#retriving users information
def get_user(user_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            cursor=conn.cursor()
            cursor.execute("""
            --sql
            SELECT *
            FROM users 
            WHERE user_id=?
            ;
            """,(user_id,)) #Comma is so that the id is supplied as one element tuple
            user=cursor.fetchone() # returns one matching row
            return user # a tuple

#Find user by usefrname
def get_user_by_username(username):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor=conn.cursor()
        cursor.execute("""
        --sql
        SELECT *
        FROM users
        WHERE username=?
        ;
        """,(username,))  
        return cursor.fetchone()          

#Updating a users budget 


#adding menu items to the database
def add_menu_items(item_name,cost):
    with closing(sqlite3.connect(DB_NAME)) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            with conn:
                cursor=conn.cursor()
                try:
                    cursor.execute("""
                    --sql
                    INSERT INTO menu_items(item_name, cost)
                    VALUES (?,?)
                    ;
                    """,(item_name,cost))
                    print(f"{item_name.title()} added to menu")
                    return cursor.lastrowid #returns id
                
                except sqlite3.IntegrityError:
                    print(f"{item_name.title()} already exists")
        
#Retriving from the menu
def get_menu_items():
    with closing(sqlite3.connect(DB_NAME)) as conn:
            cursor=conn.cursor()
            cursor.execute("""
            --sql
            SELECT item_id,item_name,cost
            FROM menu_items
            ORDER BY item_name
            ;
            """)
            return cursor.fetchall() #returns the list of menu

def get_meal(item_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor=conn.cursor()
        cursor.execute("""
        --sql
        SELECT item_id,item_name,cost
        FROM menu_items
        WHERE item_id=?
        ;
        """,(item_id,))   
        return cursor.fetchone() 

#Upate menu items
def update_menu_items(item_id,new_cost): #I doubt using id instead of name, anyway..
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            cursor=conn.cursor()
            cursor.execute("""
            --sql
            UPDATE menu_items
            SET cost=? WHERE item_id=?
            ;
            """,(new_cost,item_id))
            return cursor.rowcount  #tell the no of rows affected

def delete_menu_item(item_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            cursor=conn.cursor()
            cursor.execute("""
            --sql
            DELETE FROM menu_items 
            WHERE item_id=?
            ;
            """,(item_id,))    
            return cursor.rowcount      


#______Recording a purchase_________
def log_purchase(user_id,meal_name,cost,purchase_time=None): #purchase_time: 'YYYY-MM-DD HH:MM:SS', defaults to the database clock
     #verify meal exixts on the menu
     #----------snip----------------
     with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            cursor=conn.cursor()
            #Check the existence of the user
            cursor.execute("""
            --sql
             SELECT user_id FROM users WHERE user_id=?
            ;
            """,(user_id,))

            if cursor.fetchone() is None:
                raise ValueError("User does not exist.")
            #Record the purchase in purchase history table
            cursor.execute("""
            --sql
            INSERT INTO purchase_history (user_id,meal_name,cost,purchase_time)
            VALUES(?,?,?,COALESCE(?,CURRENT_TIMESTAMP))
            ;
            """,(user_id,meal_name,cost,purchase_time))

            #deduct the cost from the balance
            cursor.execute("""
            --sql
            UPDATE users
            SET current_daily_balance=current_daily_balance-?
            WHERE user_id=?
            ;
            """,(cost,user_id))
            print("Transaction recorded successfully!")
            return cursor.lastrowid

#to retrieve the selected user's purchase history from newest
def get_purchase_history(user_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor=conn.cursor()
        cursor.execute("""
        --sql
        SELECT *
        FROM purchase_history
        WHERE user_id=?
        ORDER BY purchase_time DESC
        ;
        """,(user_id,))
        
        return cursor.fetchall()


def save_daily_summary(user_id,log_date,allocated_budget,amount_spent,leftover_saved):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        with conn:
            cursor=conn.cursor()
            cursor.execute("""
            --sql
            INSERT INTO daily_summaries(user_id,log_date,allocated_budget,amount_spent,leftover_saved)
            VALUES(?,?,?,?,?)
            ;
            """,(user_id,log_date,allocated_budget,amount_spent,leftover_saved))
            return cursor.lastrowid


def get_daily_summaries(user_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor=conn.cursor()
        cursor.execute("""
        --sql
        SELECT summary_id,log_date,allocated_budget,amount_spent,leftover_saved
        FROM daily_summaries
        WHERE user_id=?
        ORDER BY log_date DESC
        ;
        """,(user_id,))
        return cursor.fetchall()

#New day: save the finished day's summary, bank its leftover into savings and reset the daily balance
def start_new_day(user_id,today,daily_budget,finished_date=None,amount_spent=0,leftover=0):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            cursor=conn.cursor()
            if finished_date: #a brand-new user has no finished day to summarise
                cursor.execute("""
                --sql
                INSERT INTO daily_summaries(user_id,log_date,allocated_budget,amount_spent,leftover_saved)
                VALUES(?,?,?,?,?)
                ON CONFLICT(user_id,log_date) DO UPDATE SET
                    allocated_budget=excluded.allocated_budget,
                    amount_spent=excluded.amount_spent,
                    leftover_saved=excluded.leftover_saved
                ;
                """,(user_id,finished_date,daily_budget,amount_spent,leftover))
            cursor.execute("""
            --sql
            UPDATE users
            SET savings_balance=savings_balance+?,
                current_daily_balance=?,
                last_daily_reset=?
            WHERE user_id=?
            ;
            """,(leftover,daily_budget,today,user_id))

def update_weekly_reset(user_id,reset_date):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute("UPDATE users SET last_weekly_reset=? WHERE user_id=?;",(reset_date,user_id))

def update_monthly_reset(user_id,reset_date):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute("UPDATE users SET last_mothly_reset=? WHERE user_id=?;",(reset_date,user_id))

#Deleting a user also deletes their purchases and summaries (ON DELETE CASCADE)
def delete_user(user_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            cursor=conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id=?;",(user_id,))
            return cursor.rowcount

if __name__=="__main__":
    log_purchase(user_id=5,meal_name="fried rice",cost=150)
    #print(get_purchase_history(user_id=1))
    #print(get_daily_summaries(user_id=3 ))
    create_user("george",380)   
    add_menu_items(item_name="pilau",cost=20)
    #print(get_purchase_history(6))
    print(get_user(5))
    print(get_daily_summaries(5))
    
    


     
     

