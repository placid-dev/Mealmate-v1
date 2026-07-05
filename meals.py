# -----------------------
# Recommendation & Menu edit & meal logging
# -----------------------
import storage
import finance
import streamlit as st

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
def add_meal(menu):
  with st.form("Add meal", clear_on_submit=True):
        
            new_meal = st.text_input("Meal name ")
            new_price = st.number_input(f"Enter the price",min_value=0,step=5)
            #Found a very silly bug here 
            save_changes=st.form_submit_button("Save")
            if save_changes:
                if not new_meal or new_price==0:
                    st.error("Field cannot be empty")
                else:
                    menu[new_meal] = new_price
                    storage.save_json("menu.json",menu)
                    st.success(f" Added {new_meal.title()} for {new_price} kshs!")
                    #st.rerun()

#Updating the price of an existing meal
def update_existing_meal(menu):
    if not menu:
         st.warning("The menu is empty.")
         return
    
    with st.form("update_meal_form"):
        meal_to_update=st.selectbox("Select meal",menu.keys())
        new_price=st.number_input(f"Enter the price",min_value=0,step=5)
        save_changes=st.form_submit_button("Update price")
        if save_changes:
            if new_price==0:
                st.error("Price cannot be zero")    
            else:
                menu[meal_to_update] = new_price
                #save
                storage.save_json("menu.json", menu)
                st.success(f"Updated {meal_to_update.title()} to {new_price} Kshs")
                #st.rerun()

#To delete a meal
def delete_meal(menu):
    if not menu:
        st.warning("The menu is empty") 
        return
    with st.form("delete_meal_form"):
        meal_to_delete=st.selectbox("Select a meal to delete",list(menu.keys()),format_func=lambda x: x.title())               
        confirm_delete=st.form_submit_button("Delete meal",type='primary')
        if confirm_delete:
            #delete from json
            del menu[meal_to_delete]
            storage.save_json("menu.json",menu)  
            st.success(f"Successfully removed {meal_to_delete.title()} from the menu!",icon=":material/thumb_up:")


#To add or change price of a meal
def modify_menu(menu):
    st.subheader(":rainbow[Manage Menu]")
    st.write("**Current menu items:**")
    for meal, price in menu.items():
        st.write(f"*{meal.title()} - {price} Kshs")
    st.divider()
    
    #Horizontal radio
    manage_action=st.radio("Choose an action:",["View menu","Add meal", "Update Price","Delete Meal"], horizontal=True)
    if manage_action=="Add meal":
        add_meal(menu)
    elif manage_action=="Update Price":
        update_existing_meal(menu)  
    elif manage_action=="Delete Meal":
        delete_meal(menu)     
    return menu
    

def show_recommendation(menu, balance):
    affordable = {meal: cost for meal, cost in menu.items() if cost <= balance}
    if not affordable:
        st.error(" None of the meals fit your budget")
    else:
        st.write("\n Meals you can afford:")
        for meal, cost in affordable.items():
            st.write(f" {meal.title()} - {cost} Kshs")

#Meal logging
def log_meal(menu,wallet,food_funds):
        st.subheader("Log a meal")
        if not menu:
            st.error("No meals available to log")
            return
           #INSERT THE RECOMENDATION FUNCTION HERE SO AS THE USER CAN SEE ONLY WHAT HE CAN BUY
        show_recommendation(menu,balance=wallet.get("balance",0))
            
        with st.form("log_meal_form"):

            choice = st.selectbox("Select meal to eat",menu.keys(),format_func=lambda x: x.title())
            submit_log=st.form_submit_button("Log purchase")
            if submit_log:
                purchase_successful=finance.handle_purchase(choice, menu, wallet, food_funds)
                if purchase_successful: #update the session states
                    st.session_state["wallet"]=wallet
                    st.session_state["food_funds"]=food_funds
                    
                
                


def main_meals():
    #loading stuff/ Initialization
    menu=st.session_state["menu"]
    my_food_funds=st.session_state["food_funds"]
    wallet=st.session_state["wallet"]
    balance=wallet.get('balance',0)
    
    #UI  
    st.title("WELCOME TO MEALMATE!")    
    tab1,tab2,tab3=st.tabs(["Menu Management","Meal Logging","Recomendations"]) 
    with tab1:
        modify_menu(menu)  
    with tab2:
        log_meal(menu,wallet,my_food_funds)  
    with tab3:
        st.subheader(":blue[Budget Recommendation]")
        show_recommendation(menu,balance)

if __name__=="__main__":
    main_meals()