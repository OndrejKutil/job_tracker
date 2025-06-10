import streamlit as st
import supabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("PROJECT_URL")
DATABASE_KEY = os.getenv("ANON_KEY")

# Create Supabase client
supabase_client = supabase.create_client(DATABASE_URL, DATABASE_KEY)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

def login_page():
    st.title("🔐 Job Tracker - Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        email_login = st.text_input("Email")
        password_login = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if len(password_login) < 8:
                st.error("Password must be at least 8 characters long.")
            elif not any(c.isupper() for c in password_login):
                st.error("Password must contain at least one uppercase letter.")
            elif not any(c.islower() for c in password_login):
                st.error("Password must contain at least one lowercase letter.")
            elif not any(c.isdigit() for c in password_login):
                st.error("Password must contain at least one number.")            
            else:                
                try:
                    credentials = {'email': email_login, 'password': password_login}
                    response = supabase_client.auth.sign_in_with_password(credentials)
                    
                    if response.user:
                        user_uuid = response.user.id
                        user_name = response.user.user_metadata.get('full_name', '') if response.user.user_metadata else ''
                        st.success(f"Login successful!")
                        
                        # Store user info in session state
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_uuid
                        st.session_state.user_email = response.user.email
                        st.session_state.user_name = user_name
                        st.rerun()  # Refresh the app to show dashboard
                    else:
                        st.error("Login failed. Please check your credentials.")
                except Exception as e:
                    st.error(f"Login error: {str(e)}")

    with tab2:
        st.header("Register")
        email_register = st.text_input("Email", key="reg_email")
        name_register = st.text_input("Name", key="reg_name", placeholder="Optional")
        password_register = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register", use_container_width=True):
            if len(password_register) < 8:
                st.error("Password must be at least 8 characters long.")
            elif not any(c.isupper() for c in password_register):
                st.error("Password must contain at least one uppercase letter.")
            elif not any(c.islower() for c in password_register):
                st.error("Password must contain at least one lowercase letter.")
            elif not any(c.isdigit() for c in password_register):
                st.error("Password must contain at least one number.")
            elif password_register != confirm_password:
                st.error("Passwords do not match.")
            else:                
                try:
                    if not name_register:
                        credentials = {'email': email_register, 'password': password_register}
                    else:
                        credentials = {'email': email_register, 'password': password_register, 'options': {'data': {'full_name': name_register}}}
                    response = supabase_client.auth.sign_up(credentials)
                    
                    if response.user:
                        user_uuid = response.user.id
                        user_name = response.user.user_metadata.get('full_name', '') if response.user.user_metadata else ''
                        st.success(f"Registration successful!")
                        st.success(f"Check your email ({response.user.email}) for a confirmation link.")
                        
                        # Store user info in session state
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_uuid
                        st.session_state.user_email = response.user.email
                        st.session_state.user_name = user_name
                        st.rerun()  # Refresh the app to show dashboard
                    else:
                        st.error("Registration failed. Please try again.")
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")

def dashboard_page():
    st.title("📊 Job Tracker Dashboard")
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.write(f"**Logged in as:** {st.session_state.user_name}")
        st.write(f"**User ID:** {st.session_state.user_id}")
        
        if st.button("Logout", use_container_width=True):
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()
    
    # Main dashboard content
    st.header("Welcome to your Job Tracker!")
    
    # You can add tabs or different sections here
    dashboard_tab1, dashboard_tab2, dashboard_tab3 = st.tabs(["Applications", "Add Application", "Analytics"])
    
    with dashboard_tab1:
        st.subheader("Your Job Applications")
        st.info("Here you'll see all your job applications")
        # TODO: Add code to fetch and display applications from your API
    
    with dashboard_tab2:
        st.subheader("Add New Application")
        st.info("Here you can add a new job application")
        # TODO: Add form to create new applications
    
    with dashboard_tab3:
        st.subheader("Analytics")
        st.info("Here you'll see charts and statistics about your applications")
        # TODO: Add charts and analytics

# Main app logic
def main():
    # Check authentication status
    if not st.session_state.authenticated:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()

