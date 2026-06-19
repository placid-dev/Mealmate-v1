import os
import streamlit as st
from storage import *

#--------------------PROFILE  ------------------------
 #Inputs the details and saves it to json file
def data_input(): 
    with st.form("Enter name and daily budget",clear_on_submit=True):
    # st.form is to prevent the running of code after every click until all data entered successfully
        name = st.text_input("Enter your name")
        daily_budget = st.number_input("Enter your daily_budget",min_value=100)
        submitted=st.form_submit_button("Submit")
        if submitted:
            if name.strip =="":
                st.error("Field cannot be empty")
            else:
                profile = {"name": name.title(), "daily_budget": daily_budget}
                save_json("user_profile.json", profile)           #saving
                st.success("Data saved successfully")
                st.rerun() #The browser to refresh immediately
                               
#Loads the profile if it exists or it creates one      
def init_profile(): 
    profile = load_json("user_profile.json", None)
    if profile is None:
        data_input()
    else:    
        st.write(f"Welcome back {profile['name']}")
    return profile

#output
def prof():
    profile=init_profile() #Gets the profile
    if profile is not None: #Check to make sure the profile actually exists
        st.write(f"Name: {profile['name']}")
        st.write(f"Budget: {profile['daily_budget']}")
        st.divider()

#A delete button to ...
        if st.button("Delete Profile",type= "primary"):
            file_path="user_profile.json"

        #To confirm it exists in the computer then delete it
            if os.path.exists(file_path):
                os.remove(file_path)   
                st.success("Profile deleted successfully")
                st.rerun()

st.header("Profile")
if __name__=="__main__":
     
     prof()
     