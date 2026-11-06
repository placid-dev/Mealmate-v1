import db_operations
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
    # users row: 4 = current_daily_balance, 5 = savings_balance, 8 = last_daily_reset
    user = db_operations.get_user(profile["user_id"])
    last_used = user[8]
    wallet = {"balance": user[4], "history": [], "history_archive": [], "savings": user[5], "last_used": last_used}
    # purchase_history rows: (purchase_id, user_id, meal_name, cost, purchase_time) - oldest first.
    # The wallet's current day goes in "history", earlier days in "history_archive" (feeds the analytics charts)
    for row in sorted(db_operations.get_purchase_history(profile["user_id"]), key=lambda row: (row[4], row[0])):
        entry = {
            "meal": row[2],
            "cost": row[3],
            "time": datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S").strftime("%A, %b %d at %I:%M %p"),
            "date": row[4][:10]
        }
        if last_used and entry["date"] >= last_used:
            wallet["history"].append(entry)
        else:
            wallet["history_archive"].append(entry)
    return wallet

#setting up the money allocated
def init_food_funds(profile):
    # users row: 3 = monthly_budget, 6 = last_weekly_reset, 7 = last_mothly_reset
    user = db_operations.get_user(profile["user_id"])
    last_weekly_reset = user[6] or today()
    last_monthly_reset = user[7] or today()
    data = {
        "monthly_budget": user[3],
        "spent": 0,
        "weekly_budget": user[3] / 4,
        "weekly_spent": 0,
        "last_weekly_reset": last_weekly_reset,
        "last_monthly_reset": last_monthly_reset
    }
    # what has been spent this week / month is everything bought since the last reset
    for row in db_operations.get_purchase_history(profile["user_id"]):
        if row[4][:10] >= last_monthly_reset:
            data["spent"] += row[3]
        if row[4][:10] >= last_weekly_reset:
            data["weekly_spent"] += row[3]
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
        day_spent = sum(entry["cost"] for entry in wallet.get("history", []))  # what the finished day cost
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
        db_operations.start_new_day(profile["user_id"], today_str, profile["daily_budget"], last_used, day_spent, leftover) # very crucial to ensure the update is saved on the wallet
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
        db_operations.update_weekly_reset(st.session_state["user_id"], food_funds["last_weekly_reset"])
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
        db_operations.update_monthly_reset(st.session_state["user_id"], today_str)
        st.info("A new month has started - your monthly food budget has been reset.")
        return True
    return False

# -----------------------
# Purchasing & update
# -----------------------
def handle_purchase(choice, menu, wallet, food_funds):
    cost = menu[choice]
    if cost <= wallet["balance"]:
        # records the purchase and deducts the cost from the user's balance in the database
        db_operations.log_purchase(st.session_state["user_id"], choice, cost, now().strftime("%Y-%m-%d %H:%M:%S"))
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
