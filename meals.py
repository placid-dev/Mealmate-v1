# -----------------------
# Recommendation & Menu edit & meal logging
# -----------------------
import csv
import io
import pandas as pd
import storage
import finance
import streamlit as st

#---------------------------------------------------------------
#  Feedback after a change
#  Streamlit draws the page top to bottom, so after a change the menu table / wallet balance
#  that were already drawn above the form are out of date. Refreshing the page fixes that,
#  and this keeps the confirmation message alive across the refresh.
#---------------------------------------------------------------
def _flash(message, icon=":material/check_circle:"):
    st.session_state["_flash"] = (message, icon)

def _show_flash():
    flash = st.session_state.pop("_flash", None)
    if flash:
        st.toast(flash[0], icon=flash[1])

#---------------------------------------------------------------
#-------------------------------Initialization of menu--------------------
#-------------------------------------------------------------------------------
def init_menu():
    default_menu = {
        "rice beans": 50,
        "ugali beans": 40,
        "chapoo special": 80,
        "chai": 20,
        "chafua": 60,
        "fried rice": 100,
        "pilau": 120
    }
    return storage.load_json("menu.json", default_menu)

# adding new meal(s) into the existing menu

#==================Display menu ======================
def display_menu(menu):
    if not menu:
        st.warning("No Meals Available")
        return
    rows=[
        {
            "Meal":meal.title(),
            "Price (KSh)": price
        }
        for meal, price in menu.items()
    ]
    st.table(rows)

#==================Export menu (downloadable copies) ======================
def menu_to_csv(menu):
    # CSV opens directly in Excel / Google Sheets
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Meal", "Price (KSh)"])
    for meal, price in menu.items():
        name = meal.title()
        if name[:1] in ("=", "+", "-", "@"):
            name = "'" + name   # stops spreadsheets from treating a meal name as a formula
        writer.writerow([name, price])
    return buffer.getvalue().encode("utf-8-sig")   # BOM so Excel shows the text correctly

def menu_to_text(menu):
    # Plain-text menu that is easy to paste into WhatsApp or print
    width = max(len(meal) for meal in menu) + 4
    lines = ["MealMate Menu", f"Updated {finance.now().strftime('%d %b %Y')}", ""]
    for meal, price in menu.items():
        lines.append(f"{meal.title().ljust(width, '.')} {finance.ksh(price)}")
    return "\n".join(lines).encode("utf-8")

def export_menu(menu):
    if not menu:
        return
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download CSV", data=menu_to_csv(menu),
                           file_name="mealmate_menu.csv", mime="text/csv",
                           use_container_width=True)
    with col2:
        st.download_button("Download text", data=menu_to_text(menu),
                           file_name="mealmate_menu.txt", mime="text/plain",
                           use_container_width=True)


def add_meal(menu):
  st.subheader("Add Meal")
  with st.form("Add_meal_form", clear_on_submit=True):
        
            new_meal = st.text_input("Meal name")
            new_price = st.number_input(f"Enter the price",min_value=0,step=5)
            #Found a very silly bug here 
            save_changes=st.form_submit_button("Save meal",use_container_width=True)
            if save_changes:
                # menu names are stored lowercase (shown with .title()), so "Chai " and "chai" are the same meal
                name = new_meal.strip().lower()
                if not name or new_price==0:
                    st.error("Please complete all fields")
                    return
                if any(existing.strip().lower() == name for existing in menu):
                    st.error(f"{name.title()} is already on the menu. Use 'Update Price' to change its price.")
                    return
                
                menu[name] = new_price
                storage.save_json("menu.json",menu)
                _flash(f"Added {name.title()} to the menu.")
                st.rerun()

#Updating the price of an existing meal
def update_existing_meal(menu):
    st.subheader("Update Meal Price")
    if not menu:
         st.warning("The menu is empty.")
         return
    
    with st.form("update_meal_form"):
        meal_to_update=st.selectbox("Select meal",list(menu.keys()),format_func=lambda x: f"{x.title()} ({finance.ksh(menu[x])})")
        new_price=st.number_input(f"New price (Ksh)",min_value=0,step=5)
        save_changes=st.form_submit_button("Update price",use_container_width=True)
        if save_changes:
            if new_price==0:
                st.error("Price cannot be zero")  
                return  
            
            menu[meal_to_update] = new_price
                #save
            storage.save_json("menu.json", menu)
            _flash(f"Updated {meal_to_update.title()} to {finance.ksh(new_price)}.")
            st.rerun()

#To delete a meal
def delete_meal(menu):
    st.subheader("Delete Meal")
    if not menu:
        st.warning("No Meals Available") 
        return
    with st.form("delete_meal_form"):
        meal_to_delete=st.selectbox("Select a meal to delete",list(menu.keys()),format_func=lambda x: x.title())               
        confirm_delete=st.form_submit_button("Delete meal",type='primary',use_container_width=True)
        if confirm_delete:
            #delete from json
            del menu[meal_to_delete]
            storage.save_json("menu.json",menu)  
            _flash(f"Removed {meal_to_delete.title()} from the menu.", ":material/thumb_up:")
            st.rerun()


#To add or change price of a meal
def modify_menu(menu):
    st.subheader("Menu Management")
    left,right=st.columns([2,1])
    with left:
        st.markdown("### Current Menu")
        display_menu(menu)
        export_menu(menu)
    
    #for meal, price in menu.items():
       # st.write(f"*{meal.title()} - {price} Kshs")
    #st.divider()
    with right:
        st.markdown("### Manage")
    #Horizontal radio
        manage_action=st.radio("Choose an action:",
                               ["Add meal", "Update Price","Delete Meal"], 
                               label_visibility="collapsed")
        st.divider()
    if manage_action=="Add meal":
        add_meal(menu)
    elif manage_action=="Update Price":
        update_existing_meal(menu)  
    elif manage_action=="Delete Meal":
        delete_meal(menu)     
    return menu
    
#_____________________Recommendation____________________
def show_recommendation(menu, balance):
    affordable = {meal: cost for meal, cost in menu.items() if cost <= balance}
    st.subheader("Meals you can afford.")
    if not affordable:
        st.error(" None of the meals fit your wallet balance")
        return
    
    for meal, cost in affordable.items():
       with st.container(border=True):
           col1,col2=st.columns([4,1])
           with col1:
               st.markdown(f":blue[**{meal.title()}**]")
           with col2:
               st.metric("Price",f":yellow[Ksh {cost}]")

#Meal logging
def log_meal(menu,wallet,food_funds):
        st.subheader("Log a meal")
        if not menu:
            st.error("No meals available to log")
            return
        balance=wallet.get("balance",0)
        col1,col2=st.columns(2)

        with col1:
            st.metric("Wallet Balance",finance.ksh(balance))
        with col2:
            st.metric("Available Meals",f":green[{len(menu)}]")   
        st.divider()     
           #INSERT THE RECOMENDATION FUNCTION HERE SO AS THE USER CAN SEE ONLY WHAT HE CAN BUY before selection
        show_recommendation(menu,balance=wallet.get("balance",0))
            
        with st.form("log_meal_form"):

            choice = st.selectbox("Select meal to eat",menu.keys(),format_func=lambda x: x.title())
            submit_log=st.form_submit_button("Log Meal",icon_position="right")
            if submit_log:
                purchase_successful=finance.handle_purchase(choice, menu, wallet, food_funds)
                if purchase_successful: #update the session states
                    st.session_state["wallet"]=wallet
                    st.session_state["food_funds"]=food_funds
                    _flash(f"You bought {choice.title()} for {finance.ksh(menu[choice])}. Remaining: {finance.ksh(wallet['balance'])}")
                    st.rerun()  # so the balance and "Meals you can afford" above the form update straight away
                    
def meal_history(wallet):
    st.subheader("Meal History")
    stats = finance.get_meal_stats(wallet)
    if not stats:
        st.info("No meals logged yet. Log a meal in the Meal Logging tab and your eating habits will show up here.")
        return

    total_logged = sum(item["count"] for item in stats.values())
    total_spent = sum(item["spent"] for item in stats.values())
    col1,col2=st.columns(2)
    with col1:
        st.metric("Meals Logged",total_logged)
    with col2:
        st.metric("Average Meal Cost",finance.ksh(round(total_spent / total_logged)))

    # most logged first; ties go to the meal that costs less overall
    ranked = sorted(stats.items(), key=lambda item: (-item[1]["count"], item[1]["spent"]))
    favourite, favourite_stats = ranked[0]
    st.caption(f"Most logged: {favourite.title()} ({favourite_stats['count']} times)")

    st.markdown("#### Times each meal was logged")
    chart_data = pd.DataFrame(
        {"Meal": [meal.title() for meal, _ in ranked[:8]],
         "Times logged": [item["count"] for _, item in ranked[:8]]}
    )
    st.bar_chart(chart_data, x="Meal", y="Times logged")
                


def main_meals():
    #loading stuff/ Initialization
    menu=st.session_state["menu"]
    my_food_funds=st.session_state["food_funds"]
    wallet=st.session_state["wallet"]
    balance=wallet.get('balance',0)
    
    #UI  
    st.title("Meals")   
    st.caption("Manage your meals, log purchases and stay within budget") 
    st.divider()
    tab1,tab2,tab3=st.tabs(["Meal Logging","Menu Management","Meal History"]) 
    with tab1:
        log_meal(menu,wallet,my_food_funds)
        
    with tab2:
          modify_menu(menu)  
    with tab3:
        meal_history(wallet)

    # shown after the tabs (not before) so the tab layout doesn't shift and jump back to the first tab
    _show_flash()

if __name__=="__main__":
    main_meals()