import finance
import meals
import settings
from dashboard import *
import storage

# -----------------------
# Main program
# -----------------------
#Page set up
st.set_page_config(
        page_title="Mealmate",
        layout="centered",
        
    )
#======INITIALIZATION========
profile = settings.init_profile()
#my_food_funds=finance.init_food_funds(profile)

#Pages
home_page=st.Page("meals.py",title="Home")
setting_page=st.Page("settings.py",title="Settings")
dashboard=st.Page("dashboard.py",title="Dashboard")

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

#standard full navigation menu
navigation=st.navigation([home_page,dashboard,setting_page])
navigation.run()


#=================Save ENGINE=========================
storage.save_json("wallet.json", st.session_state["wallet"])
storage.save_json("food_funds.json", st.session_state["food_funds"])
storage.save_json("menu.json", st.session_state["menu"])

   

    


