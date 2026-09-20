import storage
from datetime import datetime, timedelta, timezone
import streamlit as st

# -----------------------
# Clock & formatting helpers
# -----------------------
# The app is used in Kenya (no daylight saving), so a fixed UTC+3 offset is enough.
# Cloud servers run in UTC - without this the "day" would roll over at 3 AM local time
# and purchase times would show 3 hours early. Change the offset here if needed.
LOCAL_TZ = timezone(timedelta(hours=3))

def now():
    return datetime.now(LOCAL_TZ)

def today():
    return now().strftime("%Y-%m-%d")

def ksh(amount):
    """Format money the same way everywhere: 'Ksh 3000' (no stray '.0')."""
    amount = amount or 0
    if float(amount).is_integer():
        amount = int(amount)
    else:
        amount = round(amount, 2)
    return f"Ksh {amount}"

#setting up the wallet 
def init_wallet(profile):
    default = {"balance": profile["daily_budget"], "history": [], "savings": 0}
    wallet = storage.load_json("wallet.json", default)
    # ensure keys exist
    wallet.setdefault("balance", profile["daily_budget"])
    wallet.setdefault("history", [])
    wallet.setdefault("history_archive", [])  # past days' purchases (feeds the analytics charts)
    wallet.setdefault("savings", 0)
    wallet.setdefault("last_used", None)
    return wallet

#setting up the money allocated
def init_food_funds(profile):
    default = None
    data = storage.load_json("food_funds.json", default)#loading
    if profile is not None: #if there is a profile existing
        monthly_funds =profile.get("monthly_budget",0)
        
    else:#New structure
        monthly_funds=0
    is_new = data is None
    if is_new:
        data = {}
    # Existing values are never overwritten, but any missing key is filled in
    # (older or reset files don't always have every field).
    data.setdefault("monthly_budget", monthly_funds)
    data.setdefault("spent", 0)
    data.setdefault("weekly_budget", data["monthly_budget"] / 4)
    data.setdefault("weekly_spent", 0)
    data.setdefault("last_weekly_reset", today())
    data.setdefault("last_monthly_reset", today())
    if is_new:
        storage.save_json("food_funds.json", data)
    return data

# -----------------------
# Daily & Weekly reset logic
# -----------------------
def daily_reset_if_needed(wallet, profile):
    today_str = today()
    last_used = wallet.get("last_used")
    if last_used != today_str:
        # save yesterday leftover into savings
        # (a brand-new wallet has no "yesterday": its starting balance was never left over, so nothing is saved)
        leftover = wallet.get("balance", 0) if last_used else 0
        wallet["savings"] = wallet.get("savings", 0) + leftover
        # keep the finished day's purchases for the analytics before the daily list is cleared
        archive = wallet.setdefault("history_archive", [])
        for entry in wallet.get("history", []):
            archived = dict(entry)
            archived.setdefault("date", last_used or today_str)
            archive.append(archived)
        # reset daily fields
        wallet["balance"] = profile["daily_budget"]
        wallet["history"] = []  # today's list only - past days live in history_archive
        wallet["last_used"] = today_str
        storage.save_json("wallet.json",wallet) # very crucial to ensure the update is saved on the wallet
        #print(" New day detected — daily balance reset and leftover saved.")
        return leftover
    return 0

def weekly_reset_if_needed(food_funds):
    today_date = now().date()
    last_reset = datetime.strptime(food_funds.get("last_weekly_reset", today()), "%Y-%m-%d").date()
    days = (today_date - last_reset).days
    if days >= 7:
        # imported here (not at the top) so finance.py and dashboard.py don't import each other
        from dashboard import view_weekly_funds_summary
        st.caption("End of week summary")
        view_weekly_funds_summary(food_funds)
        # reset weekly counters
        food_funds["weekly_spent"] = 0
        food_funds["weekly_budget"] = food_funds["monthly_budget"] / 4
        food_funds["last_weekly_reset"] = today()
        storage.save_json("food_funds.json", food_funds)
        st.success("Weekly food budget has been reset.")
        return True
    return False

def monthly_reset_if_needed(food_funds):
    # "Spent" for the month used to keep growing forever - start a fresh month when the calendar month changes
    today_str = today()
    last_reset = food_funds.get("last_monthly_reset", today_str)
    if last_reset[:7] != today_str[:7]:   # compares "YYYY-MM"
        food_funds["spent"] = 0
        food_funds["last_monthly_reset"] = today_str
        storage.save_json("food_funds.json", food_funds)
        st.info("A new month has started - your monthly food budget has been reset.")
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
            "time": now().strftime("%A, %b %d at %I:%M %p"),
            "date": today()   # easy-to-read date used by the analytics charts
        }
        wallet["history"].append(entry)
        # update food funds
        food_funds["spent"] = food_funds.get("spent", 0) + cost
        food_funds["weekly_spent"] = food_funds.get("weekly_spent", 0) + cost
        storage.save_json("food_funds.json", food_funds)
        storage.save_json("wallet.json", wallet)
        # (the "You bought ..." confirmation is shown by meals.py, which refreshes the page after a purchase)
        return True
    else:
        st.error(f"Not enough balance: {choice.title()} costs {ksh(cost)} but you only have {ksh(wallet['balance'])} left today.")
        return False

#handles the math for monthly balance   
def get_remaining_monthly(food_funds):
    return food_funds["monthly_budget"] - food_funds["spent"]  

#For weekly balance
def get_remaining_weekly(food_funds):
    return food_funds['weekly_budget'] - food_funds['weekly_spent']   


# -----------------------
# Analytics helpers (feed the charts on the Dashboard and Meals pages)
# -----------------------
def get_all_purchases(wallet):
    """Every recorded purchase (past days + today), oldest first. Each has a 'date' (YYYY-MM-DD)."""
    purchases = [dict(entry) for entry in wallet.get("history_archive", [])]
    for entry in wallet.get("history", []):
        entry = dict(entry)
        # purchases logged before 'date' existed all belong to the wallet's current day
        entry.setdefault("date", wallet.get("last_used") or today())
        purchases.append(entry)
    return purchases

def get_daily_totals(wallet, days=14):
    """[(date, total spent)] for the last `days` days ending today, with 0 for days without purchases."""
    end = now().date()
    totals = {end - timedelta(days=i): 0 for i in range(days - 1, -1, -1)}
    for entry in get_all_purchases(wallet):
        try:
            day = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if day in totals:
            totals[day] += entry.get("cost", 0)
    return list(totals.items())

def get_meal_stats(wallet):
    """{meal: {"count": times logged, "spent": total cost}} across all recorded purchases."""
    stats = {}
    for entry in get_all_purchases(wallet):
        meal = entry.get("meal", "").strip().lower()
        if not meal:
            continue
        item = stats.setdefault(meal, {"count": 0, "spent": 0})
        item["count"] += 1
        item["spent"] += entry.get("cost", 0)
    return stats
