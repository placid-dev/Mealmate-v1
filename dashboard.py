import storage
import finance
import streamlit as st
from meals import init_menu
import settings

# -----------------------
# Views / summaries
# -----------------------
def view_history(wallet):
    if not wallet["history"]:
        st.error("No purchase history available.")
        return
    st.write("Purchase History :")# from the current to the oldest
    for entry in reversed(wallet["history"]):
        st.write(f"• {entry['meal']} - {entry['cost']} Kshs on {entry['time']}")

def view_cost_summary(wallet, food_funds, amount_to_save):
    monthly_rem=finance.get_remaining_monthly(food_funds)
    total_spent = sum(entry["cost"] for entry in wallet["history"])
    st.subheader(":blue[Financial Overview]")
    st.write(f"**Total spent today:** {total_spent} Kshs")
    st.write(f"Today's remaining balance: {wallet['balance']} Kshs")
    st.write(f"Today's amount saved (yesterday leftover): {amount_to_save} Kshs")
    st.write(f"Total savings: {wallet.get('savings', 0)} Kshs")
    st.write(f"Food funds monthly budget: {food_funds['monthly_budget']} Kshs")
    st.write(f"Total food funds spent so far: {food_funds['spent']} Kshs")
    st.write(f"Remaining monthly funds: {monthly_rem} Kshs")

def view_funds_summary(food_funds):
    monthly_rem=finance.get_remaining_monthly(food_funds)
    st.subheader(":blue[Monthly Tracking]")
    st.write(f"\nMonthly budget: {food_funds['monthly_budget']} Kshs")
    st.write(f"Total spent so far: {food_funds['spent']} Kshs")
    st.write(f"Remaining balance: {monthly_rem} Kshs")

def view_weekly_funds_summary(food_funds):
    weekly_rem=finance.get_remaining_weekly(food_funds)
    st.subheader(":blue[Weekly Tracking]")
    st.write(f"Weekly budget allocation: {food_funds['weekly_budget']} Kshs")
    st.write(f"Spent this week: {food_funds['weekly_spent']} Kshs")
    st.write(f"Remaining allowance this week: {weekly_rem} Kshs")# error

#-----------------------------------------------------------------
#       DISPLAY
#-----------------------------------------------------------------
def main_dashboard():
    st.title("My Insights And :blue[Anal]ytics :sunglasses:")
    # Exctract live data from thr session
    wallet=st.session_state["wallet"]
    my_food_funds=st.session_state["food_funds"]
    amount_to_save=wallet.get("savings",0)    

    #---------------------tabs---------------------------------
    tab1,tab2,tab3=st.tabs(["Cost Breakdown","Weekly and monthly Progress","Purchase History"])
    with tab1:
        view_cost_summary(wallet, my_food_funds, amount_to_save)   
    with tab2:
        view_funds_summary(my_food_funds)
        st.divider()  
        view_weekly_funds_summary(my_food_funds)          
    with tab3:
        view_history(wallet)   

if __name__=="__main__":
    if "wallet" not in st.session_state or "food_funds" not in st.session_state:
        st.warning("User Friendly warning")
    else:
        main_dashboard()    