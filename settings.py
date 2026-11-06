import os
import streamlit as st
import finance
from datetime  import datetime
import db_operations

#--------------------PROFILE  ------------------------
 #Inputs the details and saves it to json file

#==============================================================
#    LONG PROFILE CREATION FUNTION
# ============================================================= 
def user_data_input(key_suffix="default"):
    st.title("Settings") #The parameter is to uniquely identify the form
    st.caption("Set up your mealmate profile. Already have one? Enter your username to sign back in.")
    st.divider()
    with st.form(f"Enter_name_and_budget_{key_suffix}",clear_on_submit=False):
    # st.form is to prevent the running of code after every click until all data entered successfully
        name = st.text_input("Enter your username")
        
        daily_budget = st.number_input("Enter your daily budget",min_value=100) #It can be derived from monthly
        monthly_budget=daily_budget*30#st.number_input("Enter your monthly budget", min_value=3000)#OR IT CAN BE DERIVED FROM DAILY
        submitted=st.form_submit_button("Save Profile",use_container_width=True)
        if submitted:
            if name.strip() =="":
                st.error("Please enter your name")
            elif daily_budget > monthly_budget:
                st.error("Your daily budget can't be more than your monthly budget")
            else:
                #save the user profile on database
                try:
                    existing_user=db_operations.get_user_by_username(name.strip().title())
                    if existing_user is not None:
                        #The username is already registered: sign back in with the saved budget
                        user_id=existing_user[0]
                        daily_budget=existing_user[2]
                        monthly_budget=existing_user[3]
                    else:
                        user_id=db_operations.create_user(username=name.strip().title(),daily_budget=daily_budget)
                    if user_id is None:
                        st.error(f"{name.title()} already exists.")
                        st.stop()
                    st.session_state["user_id"]=user_id
                    st.session_state["profile"]={"user_id":user_id,
                                                 "username":name.strip().title(),
                                                 "daily_budget":daily_budget,
                                                 "monthly_budget":monthly_budget}

                except Exception as e:
                    st.error(f"Could Not Save Profile:{e}")
                    st.stop()    
                          #saving the user profile
            

                st.success("Data saved successfully")
                st.rerun() #The browser to refresh immediately
                return monthly_budget
                       
#Loads the profile..From the database   
def init_profile(): 
    user_id=st.session_state.get("user_id")
    if user_id is None:
        return None
    #Retrieve user from db
    user=db_operations.get_user(user_id)
    if user is None:
        st.session_state.pop("user_id",None)#remove user_id from session state
        return None
    #converting db row into a dictionary
    profile={
        "user_id":user[0],
        "name":user[1],
        "daily_budget":user[2],
        "monthly_budget":user[3]
    }
    return profile

#delete funtion
def delete_profile():
    #delete all files related to user
    st.subheader("Danger zone")
    st.error("Deleting your profile will permanently delete your profile and financial records")

# confirmation check
    agree=st.checkbox("I understand this action cannot be undone")
    
    if st.button("Delete Account",disabled=not agree,type="primary",use_container_width=True):
       
        #deleting the user also deletes their purchases and daily summaries
        db_operations.delete_user(st.session_state.get("user_id"))

        #clearing the active memory session
        st.session_state.clear()

        st.success("Account deleted")
        st.rerun()    
          

#output
def view_profile():
    profile=init_profile() #Gets the profile
    if profile is not None: #Check to make sure the profile actually exists
        st.subheader("Profile")
        col1,col2,col3=st.columns(3)
        with col1:
            st.metric("**:blue[Name]**",f"{profile['name']}")
        with col2:
            st.metric("**Daily Budget**",finance.ksh(profile['daily_budget']))
        with col3:
            st.metric("**Monthly Budget**",finance.ksh(profile['monthly_budget']))
        

        
if __name__=="__main__":
    profile=init_profile()
    if profile is None:
        user_data_input()   # draws its own title, so it isn't repeated here
    else:    
      st.title("Settings")
      st.caption("Manage your profile and preferences")
      tab1,tab2=st.tabs(["Profile","Advanced"])
      with tab1:
        view_profile()
        st.divider()
        with tab2:
            delete_profile()

    print(profile)