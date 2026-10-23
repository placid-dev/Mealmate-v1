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


#______Recording a purchase_________
def log_purchase(user_id,meal_name,cost):
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
            INSERT INTO purchase_history (user_id,meal_name,cost)
            VALUES(?,?,?)
            ;
            """,(user_id,meal_name,cost))

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

if __name__=="__main__":
    #log_purchase(user_id=6,meal_name="pilau",cost=50)
    #print(get_purchase_history(user_id=1))
    #print(get_daily_summaries(user_id=3 ))
    create_user("george",380)   
    add_menu_items(item_name="pilau",cost=20)
    #print(get_purchase_history(6))
    print(get_user(5))
    print(get_daily_summaries(5))
    
    


     
     

