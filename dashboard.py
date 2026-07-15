import storage
import finance
import streamlit as st
from meals import init_menu
import settings

# -----------------------
# Views / summaries
# -----------------------
def view_history(wallet):
    st.subheader("Recent Purchases")
    if not wallet["history"]:
        st.info("No purchase history available.")
        return
    
    for entry in reversed(wallet["history"]):
        with st.container(border=True):
            col1,col2=st.columns([3,1])
            with col1:
                st.write(f"**{entry['meal'].title()}**")
                st.caption(entry["time"])
            with col2:
                st.metric("Cost",f"Ksh {entry['cost']}")    
     #st.write(f"• {entry['meal']} - {entry['cost']} Kshs on {entry['time']}")

def view_cost_summary(wallet, food_funds, amount_to_save):
    monthly_rem=finance.get_remaining_monthly(food_funds)
    total_spent = sum(entry["cost"] for entry in wallet["history"])
    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.metric("Wallet",f" Ksh {wallet['balance']}")

    with col2:
        st.metric("Today",f"Ksh {total_spent}") 

    with col3:
        st.metric("Mothly left",f"Ksh {monthly_rem}")   

    with col4:
        st.metric("Savings",f"Kshs {wallet.get('savings',0)}")  

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
        st.metric("Monthly Budget",f"Ksh {food_funds['monthly_budget']}")
    with col2:
        st.metric("Spent",f"Ksh {food_funds['spent']} ")
    with col3:
        st.metric("Remaining",f"Ksh {monthly_rem}")
    

def view_weekly_funds_summary(food_funds):
    weekly_rem=finance.get_remaining_weekly(food_funds)
    st.subheader(":blue[Weekly Tracking]")
    col1,col2,col3=st.columns(3)
    with col1:
        st.metric("Weekly Budget",f"Ksh {food_funds['weekly_budget']}")
    with col2:
        st.metric("Weekly Spent",f"Ksh {food_funds['weekly_spent']}")
    with col3:    
        st.metric("Weekly Remaining",f" Ksh {weekly_rem}")

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
    #with tab3:
    view_history(wallet)   

if __name__=="__main__":
    if "wallet" not in st.session_state or "food_funds" not in st.session_state:
        st.warning("User Friendly warning")
    else:
        main_dashboard()    