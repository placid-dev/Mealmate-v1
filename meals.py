# -----------------------
# Recommendation & Menu edit & meal logging
# -----------------------
import storage
import finance
import streamlit as st

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


def add_meal(menu):
  st.subheader("Add Meal")
  with st.form("Add_meal_form", clear_on_submit=True):
        
            new_meal = st.text_input("Meal name")
            new_price = st.number_input(f"Enter the price",min_value=0,step=5)
            #Found a very silly bug here 
            save_changes=st.form_submit_button("Save meal",use_container_width=True)
            if save_changes:
                if not new_meal or new_price==0:
                    st.error("Please complete all fields")
                    return
                
                menu[new_meal] = new_price
                storage.save_json("menu.json",menu)
                st.success(f" Added {new_meal.title()} successfully!")
                    #st.rerun()

#Updating the price of an existing meal
def update_existing_meal(menu):
    st.subheader("Update Meal Price")
    if not menu:
         st.warning("The menu is empty.")
         return
    
    with st.form("update_meal_form"):
        meal_to_update=st.selectbox("Select meal",list(menu.keys()),format_func=lambda x: x.title())
        new_price=st.number_input(f"New Price(Ksh)",min_value=0,step=5)
        save_changes=st.form_submit_button("Update price",use_container_width=True)
        if save_changes:
            if new_price==0:
                st.error("Price cannot be zero")  
                return  
            
            menu[meal_to_update] = new_price
                #save
            storage.save_json("menu.json", menu)
            st.success(f"Updated {meal_to_update.title()} updated successfully!")
                #st.rerun()

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
            st.success(f"Successfully removed {meal_to_delete.title()} from the menu!",icon=":material/thumb_up:")


#To add or change price of a meal
def modify_menu(menu):
    st.subheader("Menu Management")
    left,right=st.columns([2,1])
    with left:
        st.markdown("### Current Menu")
        display_menu(menu)
    
    #for meal, price in menu.items():
       # st.write(f"*{meal.title()} - {price} Kshs")
    #st.divider()
    with right:
        st.markdown("###Manage")
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
    st.subheader("Meals you can afford")
    if not affordable:
        st.error(" None of the meals fit your wallet balance")
        return
    
    for meal, cost in affordable.items():
       with st.container(border=True):
           col1,col2=st.columns([4,1])
           with col1:
               st.markdown(f"###{meal.title()}")
           with col2:
               st.metric("Price",f"Ksh {cost}")

#Meal logging
def log_meal(menu,wallet,food_funds):
        st.subheader("Log a meal")
        if not menu:
            st.error("No meals available to log")
            return
        balance=wallet.get("balance",0)
        col1,col2=st.columns(2)

        with col1:
            st.metric("wallet Balance",f"{balance}")
        with col2:
            st.metric("Available Meals",len(menu))   
        st.divider()     
           #INSERT THE RECOMENDATION FUNCTION HERE SO AS THE USER CAN SEE ONLY WHAT HE CAN BUY before selection
        show_recommendation(menu,balance=wallet.get("balance",0))
            
        with st.form("log_meal_form"):

            choice = st.selectbox("Select meal to eat",menu.keys(),format_func=lambda x: x.title())
            submit_log=st.form_submit_button("Log Meal")
            if submit_log:
                purchase_successful=finance.handle_purchase(choice, menu, wallet, food_funds)
                if purchase_successful: #update the session states
                    st.session_state["wallet"]=wallet
                    st.session_state["food_funds"]=food_funds
                    
def meal_history():
    st.subheader("Meal History")
    st.info("Meal history will appear here once you implement purchase history")          
                


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
    tab1,tab2,tab3=st.tabs(["Meal Logging","Menu Management","Recomendations"]) 
    with tab1:
        log_meal(menu,wallet,my_food_funds)
        
    with tab2:
          modify_menu(menu)  
    with tab3:
        meal_history()

if __name__=="__main__":
    main_meals()