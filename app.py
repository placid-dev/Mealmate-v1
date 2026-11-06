import finance
import meals
import settings
import dashboard
import database
import streamlit  as st

# -----------------------
# Main program
# -----------------------
#Page set up
st.set_page_config(
        page_title="Mealmate",
        page_icon="icon.jpeg",
        layout="centered",
        
    )
#======INITIALIZATION========
database.initialize_database() #creates the tables on a fresh install, does nothing if they already exist
#st.session_state["profile"]=settings.init_profile()
profile = st.session_state.get("profile") #Get profile from the session state

#my_food_funds=finance.init_food_funds(profile)

#Pages
home_page=st.Page("meals.py",title="Meals")
setting_page=st.Page("settings.py",title="Settings")
dashboard_page=st.Page("dashboard.py",title="Dashboard")  

if profile is None:
    st.info("Please set up your profile in the settings tab to get started.")

    #Forces the navigation to only show settings page
    navigation=st.navigation([setting_page])
    navigation.run()
    st.stop() # so the rest iant execouted leading to a crash



#===============================================================
#       SESSION STATE CONTAINER LAYER
#===============================================================
if "wallet" not in st.session_state:
    st.session_state["wallet"]=finance.init_wallet(profile)

if "food_funds" not in st.session_state:
    st.session_state["food_funds"] = finance.init_food_funds(profile)

#meals.py  sets up the food stuff
if "menu" not in st.session_state:
    st.session_state["menu"] = meals.init_menu()
#========================================================================
#         BUSINESS LOGIC LAYER
#=======================================================================
    # DAILY reset must happen before showing menu / taking purchases
amount_to_save = finance.daily_reset_if_needed(st.session_state["wallet"], profile)
    # WEEKLY check (resets if needed)
finance.weekly_reset_if_needed(st.session_state["food_funds"])
    # MONTHLY check (starts a fresh month when the calendar month changes)
finance.monthly_reset_if_needed(st.session_state["food_funds"])

#standard full navigation menu
navigation=st.navigation([home_page,dashboard_page,setting_page])
navigation.run()

   

    


