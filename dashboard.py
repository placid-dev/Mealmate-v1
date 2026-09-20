import storage
import finance
import pandas as pd
import streamlit as st
from meals import init_menu
import settings

# -----------------------
# Views / summaries
# -----------------------
def view_history(wallet):
    st.subheader("Recent Purchases")
    purchases = finance.get_all_purchases(wallet)  # past days + today, so this isn't empty every morning
    if not purchases:
        st.info("No purchases yet. Log a meal on the Meals page and it will show up here.")
        return
    
    for entry in reversed(purchases[-10:]):
        with st.container(border=True):
            col1,col2=st.columns([3,1])
            with col1:
                st.write(f"**{entry['meal'].title()}**")
                st.caption(entry["time"])
            with col2:
                st.metric("Cost",finance.ksh(entry['cost']))    
     #st.write(f"• {entry['meal']} - {entry['cost']} Kshs on {entry['time']}")

def view_cost_summary(wallet, food_funds, amount_to_save):
    monthly_rem=finance.get_remaining_monthly(food_funds)
    total_spent = sum(entry["cost"] for entry in wallet["history"])
    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.metric("Wallet",finance.ksh(wallet['balance']))

    with col2:
        st.metric("Today",finance.ksh(total_spent)) 

    with col3:
        st.metric("Monthly left",finance.ksh(monthly_rem))   

    with col4:
        st.metric("Savings",finance.ksh(wallet.get('savings',0)))  

    st.divider()
              
    #st.subheader(":blue[Financial Overview]")
    #st.write(f"**Total spent today:** {total_spent} Kshs")
    #st.write(f"Today's remaining balance: {wallet['balance']} Kshs")
    #st.write(f"Today's amount saved (yesterday leftover): {amount_to_save} Kshs")
    #st.write(f"Total savings: {wallet.get('savings', 0)} Kshs")
    #st.write(f"Food funds monthly budget: {food_funds['monthly_budget']} Kshs")
    #st.write(f"Total food funds spent so far: {food_funds['spent']} Kshs")
    #st.write(f"Remaining monthly funds: {monthly_rem} Kshs")          

def view_funds_summary(food_funds):
    monthly_rem=finance.get_remaining_monthly(food_funds)
    st.subheader(":blue[Monthly Tracking]")
    col1,col2,col3=st.columns(3)
    with col1:
        st.metric("Monthly Budget",finance.ksh(food_funds['monthly_budget']))
    with col2:
        st.metric("Spent",finance.ksh(food_funds['spent']))
    with col3:
        st.metric("Remaining",finance.ksh(monthly_rem))
    view_budget_progress(food_funds['spent'], food_funds['monthly_budget'], "monthly")
    

def view_weekly_funds_summary( food_funds):
    weekly_rem=finance.get_remaining_weekly(food_funds)
    st.subheader(":blue[Weekly Tracking]")
    col1,col2,col3=st.columns(3)
    with col1:
        st.metric("Weekly Budget",finance.ksh(food_funds['weekly_budget']))
    with col2:
        st.metric("Weekly Spent",finance.ksh(food_funds['weekly_spent']))
    with col3:    
        st.metric("Weekly Remaining",finance.ksh(weekly_rem))
    view_budget_progress(food_funds['weekly_spent'], food_funds['weekly_budget'], "weekly")

# -----------------------
# Analytics
# -----------------------
def view_budget_progress(spent, budget, period):
    # a quick "how much of the budget is used" bar under the weekly / monthly numbers
    if budget <= 0:
        return
    if spent > budget:
        st.progress(1.0, text=f"Over your {period} budget by {finance.ksh(spent - budget)}")
    else:
        used = spent / budget
        st.progress(used, text=f"{used:.0%} of your {period} budget used")

def view_spending_trend(wallet):
    st.subheader(":blue[Spending Trend]")
    if not finance.get_all_purchases(wallet):
        st.info("Charts will appear here once you have logged some meals.")
        return

    period = st.radio("Show the last",[7,14,30],index=1,horizontal=True,
                      format_func=lambda days: f"{days} days")
    daily = finance.get_daily_totals(wallet, period)
    daily_df = pd.DataFrame({"Date": pd.to_datetime([day for day, _ in daily]),
                             "Spent (Ksh)": [total for _, total in daily]})
    st.markdown("#### Daily spending")
    st.bar_chart(daily_df, x="Date", y="Spent (Ksh)")

    profile = settings.init_profile() or {}
    caption = f"Spent {finance.ksh(sum(total for _, total in daily))} in the last {period} days"
    if profile.get("daily_budget"):
        caption += f" - your daily budget is {finance.ksh(profile['daily_budget'])}"
    st.caption(caption)

    stats = finance.get_meal_stats(wallet)
    top_meals = sorted(stats.items(), key=lambda item: -item[1]["spent"])[:8]
    st.markdown("#### Where your money goes")
    meals_df = pd.DataFrame({"Meal": [meal.title() for meal, _ in top_meals],
                             "Spent (Ksh)": [item["spent"] for _, item in top_meals]})
    st.bar_chart(meals_df, x="Meal", y="Spent (Ksh)")
    st.caption("Total spent per meal, across all your logged purchases")

#-----------------------------------------------------------------
#       DISPLAY
#-----------------------------------------------------------------
def main_dashboard():
    st.title(":green[Dashboard]")
    st.caption("Track your spending,savings and meal activity")
    st.divider()
    # Exctract live data from thr session
    wallet=st.session_state["wallet"]
    my_food_funds=st.session_state["food_funds"]
    amount_to_save=wallet.get("savings",0)    

    #---------------------tabs---------------------------------
    #tab1,tab2,tab3=st.tabs(["Cost Breakdown","Weekly and monthly Progress","Purchase History"])
    #with tab1:
    view_cost_summary(wallet, my_food_funds, amount_to_save)   
    #with tab2:
    view_funds_summary(my_food_funds)
    st.divider()  
    view_weekly_funds_summary(my_food_funds)          
    st.divider()
    view_spending_trend(wallet)
    st.divider()
    #with tab3:
    view_history(wallet)   

if __name__=="__main__":
    if "wallet" not in st.session_state or "food_funds" not in st.session_state:
        st.warning("Your data hasn't loaded yet. Please refresh the page or open the Meals page first.")
    else:
        main_dashboard()    