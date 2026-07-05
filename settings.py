import os
import streamlit as st
import storage
from datetime  import datetime

#--------------------PROFILE  ------------------------
 #Inputs the details and saves it to json file

#==============================================================
#    LONG PROFILE CREATION FUNTION
# ============================================================= 
def user_data_input(key_suffix="default"): #The parameter is to uniquely identify the form
    with st.form(f"Enter_name_and_budget_{key_suffix}",clear_on_submit=True):
    # st.form is to prevent the running of code after every click until all data entered successfully
        name = st.text_input("Enter your name")
        monthly_budget=st.number_input("Enter your monthly budget", min_value=3000)#OR IT CAN BE DERIVED FROM DAILY
        daily_budget = st.number_input("Enter your daily budget",min_value=100) #It can be derived from monthly
        weekly_budget = monthly_budget / 4
        submitted=st.form_submit_button("Submit")
        if submitted:
            if name.strip() =="":
                st.error("Field cannot be empty")
            else:
                profile = {"name": name.title(), "daily_budget": daily_budget,"monthly_budget":monthly_budget}
                storage.save_json("user_profile.json", profile)           #saving the user profile
            
            #-------Setting up and saving th food funds    
                
                data = {
            "monthly_budget": monthly_budget,
            "spent": 0,
            "weekly_budget": weekly_budget,
            "weekly_spent": 0,
            "last_weekly_reset": datetime.now().strftime("%Y-%m-%d")
                        }
                storage.save_json("food_funds.json", data)
                

                st.success("Data saved successfully")
                st.rerun() #The browser to refresh immediately
                return monthly_budget
                       
#Loads the profile      
def init_profile(): 
    profile = storage.load_json("user_profile.json", None)
    return profile

#delete funtion
def delete_profile():
    #delete all files related to user
    st.markdown("###Warning")
    st.info("Deleting your profile will permanently clear your account")

# confirmation check
    agree=st.checkbox("I understand thet the action cannot be undone")
    
    if st.button("Delete Acount",disabled=not agree,type="primary"):
        # Did not work because the system was  currently reading/modifying the files
        #target_files=["user_profile.json","food_funds.json","wallet.json","menu.json"] #list of files to be deleted
        #for file in target_files:
            #if os.path.exists(file):
        #        os.remove

        #clearing the active memory session
        st.session_state.clear()

        #Overwriting instead of deleting entirely
        #The bluebrints tell how the files will be overwritten....not just "null". Learnt from a massive mistake
        reset_blueprints={
            "user_profile.json":None,
            "food_funds.json":{"balance":0,"history":[],"savings":0,"monthly_bugdet":0,"weekly_budget":0,"weekly_spent":0},
            "wallet.json":{},
            "menu.json":{
    "rice beans": 50,
    "ugali beans": 40,
    "chapoo special": 80,
    "chai": 20,
    "chafua": 60,
    "fried rice": 100,
    "pilau": 120
}
        }
        for file, clean_data in reset_blueprints.items():
            storage.save_json(file,clean_data)
        st.success("Account deleted")
        st.rerun()    
          

#output
def view_profile():
    profile=init_profile() #Gets the profile
    if profile is not None: #Check to make sure the profile actually exists
        st.write(f"Name: {profile['name']}")
        st.write(f"Money Allocated this month: {profile['monthly_budget']}")
        st.write(f"Daily Budget: {profile['daily_budget']}")
        st.divider()

#A delete button to ...
        
if __name__=="__main__":
    profile=init_profile()
    if profile is None:
        user_data_input()
    else:    
      tab1,tab2=st.tabs(["Profile","Na"])
      with tab1:
        view_profile()
        st.divider()
        with st.expander("Advanced Options"):
            delete_profile()
     