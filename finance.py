import storage
from datetime import datetime, timedelta
from dashboard import view_weekly_funds_summary
import streamlit as st
import settings

#setting up the wallet 
def init_wallet(profile):
    default = {"balance": profile["daily_budget"], "history": [], "savings": 0}
    wallet = storage.load_json("wallet.json", default)
    # ensure keys exist
    wallet.setdefault("balance", profile["daily_budget"])
    wallet.setdefault("history", [])
    wallet.setdefault("savings", 0)
    wallet.setdefault("last_used", None)
    return wallet

#setting up the money allocated
def init_food_funds(profile):
    default = None
    data = storage.load_json("food_funds.json", default)#loading
    if data is not None:
        return  data #Escapes so its not overwritten
    if profile is not None: #if there is a profile existing
        monthly_funds =profile.get("monthly_budget",0)
        
    else:#New structure
        monthly_funds=0
    weekly_budget = monthly_funds / 4
    data = {
            "monthly_budget": monthly_funds,
            "spent": 0,
            "weekly_budget": weekly_budget,
            "weekly_spent": 0,
            "last_weekly_reset": datetime.now().strftime("%Y-%m-%d")
        }
    storage.save_json("food_funds.json", data)
    return data

# -----------------------
# Daily & Weekly reset logic
# -----------------------
def daily_reset_if_needed(wallet, profile):
    today_str = datetime.now().strftime("%Y-%m-%d")
    if wallet.get("last_used") != today_str:
        # save yesterday leftover into savings
        leftover = wallet.get("balance", 0)  #amount to save------a small bug here
        wallet["savings"] = wallet.get("savings", 0) + leftover
        # reset daily fields
        wallet["balance"] = profile["daily_budget"]
        wallet["history"] = []  # optional: if you want per-day history only
        wallet["last_used"] = today_str
        storage.save_json("wallet.json",wallet) # very crucial to ensure the update is saved on the wallet
        #print(" New day detected — daily balance reset and leftover saved.")
        return leftover
    return 0

def weekly_reset_if_needed(food_funds):
    today = datetime.now()
    last_reset = datetime.strptime(food_funds.get("last_weekly_reset", today.strftime("%Y-%m-%d")), "%Y-%m-%d")
    days = (today - last_reset).days
    if days >= 7:
        print("\n--- End of the week food monthly_funds summary ---")
        view_weekly_funds_summary(food_funds)
        # reset weekly counters
        food_funds["weekly_spent"] = 0
        food_funds["weekly_budget"] = food_funds["monthly_budget"] / 4
        food_funds["last_weekly_reset"] = today.strftime("%Y-%m-%d")
        storage.save_json("food_funds.json", food_funds)
        st.success("Weekly food monthly_funds have been reset.")
        return True
    return False

# -----------------------
# Purchasing & update
# -----------------------
def handle_purchase(choice, menu, wallet, food_funds):
    cost = menu[choice]
    if cost <= wallet["balance"]:
        wallet["balance"] -= cost
        entry = {
            "meal": choice,
            "cost": cost,
            "time": datetime.now().strftime("%A, %b %d at %I:%M %p")
        }
        wallet["history"].append(entry)
        # update food monthly_funds
        food_funds["spent"] = food_funds.get("spent", 0) + cost
        food_funds["weekly_spent"] = food_funds.get("weekly_spent", 0) + cost
        storage.save_json("food_funds.json", food_funds)
        storage.save_json("wallet.json", wallet)
        st.success(f" You bought {choice.title()} for {cost} Kshs. Remaining: {wallet['balance']} Kshs")
        return True
    else:
        st.error(" Not enough balance.")
        return False

#handles the math for monthly balance   
def get_remaining_monthly(food_funds):
    return food_funds["monthly_budget"] - food_funds["spent"]  

#For weekly balance
def get_remaining_weekly(food_funds):
    return food_funds['weekly_budget'] - food_funds['weekly_spent']   
