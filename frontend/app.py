import streamlit as st
import supabase
import requests
from datetime import datetime

# Load secrets from Streamlit secrets management
DATABASE_URL = st.secrets["supabase"]["PROJECT_URL"]
DATABASE_KEY = st.secrets["supabase"]["ANON_KEY"]
API_KEY = st.secrets["backend"]["API_KEY"]
BACKEND_URL = st.secrets["backend"]["BACKEND_URL"]

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
if 'switch_to_applications' not in st.session_state:
    st.session_state.switch_to_applications = False

# Helper functions
def fetch_user_applications():
    """Fetch applications for the current user from the backend API"""
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        response = requests.get(
            f"{BACKEND_URL}/application/user/{st.session_state.user_id}",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch applications: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching applications: {str(e)}")
        return []

def create_application_card(app_data):
    """Create a card for an application with edit functionality"""
    # Define status-based colors
    status = app_data.get('status', '').lower()
    status_colors = {
        'interested': {'bg': '#e3f2fd', 'border': '#2196f3'},  # Light blue
        'applied': {'bg': '#fff3e0', 'border': '#ff9800'},     # Light orange
        'interviewing': {'bg': '#f3e5f5', 'border': '#9c27b0'}, # Light purple
        'offer': {'bg': '#e8f5e8', 'border': '#4caf50'},       # Light green
        'accepted': {'bg': '#e8f5e8', 'border': '#4caf50'},    # Light green
        'rejected': {'bg': '#ffebee', 'border': '#f44336'}     # Light red
    }
    
    # Get colors for current status or default
    colors = status_colors.get(status, {'bg': '#f9f9f9', 'border': '#ddd'})
    
    with st.container():
        # Create a card-like appearance using columns and styling
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Main card content with dynamic colors
            st.markdown(f"""
            <div style="
                border: 2px solid {colors['border']}; 
                border-radius: 10px; 
                padding: 15px; 
                margin: 10px 0;
                background-color: {colors['bg']};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0 0 10px 0; color: #333;">
                    {app_data.get('job_title', 'No Title')} 
                    at {app_data.get('company_name', 'Unknown Company')}
                </h4>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Status:</strong> 
                    <span style="
                        background-color: {colors['border']};
                        color: white;
                        padding: 2px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                    ">{app_data.get('status', 'Unknown').title()}</span>
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Applied:</strong> {app_data.get('applied_date', 'Not specified') or 'Not specified'}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Recruiter:</strong> {app_data.get('recruiter', 'Not specified') or 'Not specified'}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Notes:</strong> {(app_data.get('notes') or 'No notes')[:100]}{'...' if app_data.get('notes') and len(app_data.get('notes')) > 100 else ''}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Edit button (three dots menu style)
            if st.button("⋮", key=f"edit_{app_data['application_id']}", help="Edit application"):
                st.session_state[f"edit_modal_{app_data['application_id']}"] = True
        
        # Edit form modal (appears when edit button is clicked)
        if st.session_state.get(f"edit_modal_{app_data['application_id']}", False):
            with st.expander("Edit Application", expanded=True):
                edit_application_form(app_data)

def delete_application(app_id):
    """Delete an application from the backend"""
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'}
        
        response = requests.delete(
            f"{BACKEND_URL}/application/{app_id}",
            headers=headers
        )
        if response.status_code == 200:
            return {'status': 'success', 'message': 'Application deleted successfully'}
    except Exception as e:
        return {'status': 'error', 'message': f"Error deleting application: {str(e)}, {response.status_code} - {response.text}"}

def delete_user_applications(user_id):
    """Delete all applications for a specific user from the backend"""
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        response = requests.delete(
            f"{BACKEND_URL}/application/user/{user_id}",
            headers=headers
        )
        if response.status_code == 200:
            return {'status': 'success', 'message': 'All applications deleted successfully'}
    except Exception as e:
        return {'status': 'error', 'message': f"Error deleting user applications: {str(e)}, {response.status_code} - {response.text}"}

def edit_application_form(app_data):
    """Create an edit form for an application"""
    app_id = app_data['application_id']
    
    # Form inputs with current values
    with st.form(key=f"edit_form_{app_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", value=app_data.get('company_name', ''))
            job_title = st.text_input("Job Title", value=app_data.get('job_title', ''))
            recruiter = st.text_input("Recruiter", value=app_data.get('recruiter', ''))
        
        with col2:
            status_options = ["interested", "applied", "interviewing", "offer", "rejected", "accepted"]
            current_status = app_data.get('status', 'applied')
            status_index = status_options.index(current_status) if current_status in status_options else 1
            status = st.selectbox("Status", options=status_options, index=status_index)
            
            applied_date = st.date_input("Applied Date", 
                value=datetime.strptime(app_data.get('applied_date', '2025-01-01'), '%Y-%m-%d').date() if app_data.get('applied_date') else None)
            job_url = st.text_input("Job URL", value=app_data.get('job_url', ''))
        
        notes = st.text_area("Notes", value=app_data.get('notes', ''), height=100)
        
        # Form buttons
        col1, col2, col3= st.columns([1, 1, 1])
        
        with col1:
            if st.form_submit_button("✅ Success", use_container_width=True):
                response = update_application(
                    app_id, 
                    company_name, 
                    job_title, 
                    recruiter, 
                    status, 
                    applied_date, 
                    job_url, 
                    notes
                )
                if response['status'] == 'success':
                    st.session_state[f"edit_modal_{app_id}"] = False
                    st.rerun()
                else:
                    st.error(f"Error updating application: {response.get('message', 'Unknown error')}")
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state[f"edit_modal_{app_id}"] = False
                st.rerun()

        with col3:
            if st.form_submit_button("🗑️ Delete", use_container_width=True):
                response = delete_application(app_id)
                if response['status'] == 'success':
                    st.session_state[f"edit_modal_{app_id}"] = False
                    st.rerun()
                else:
                    st.error(f"Error deleting application: {response.get('message', 'Unknown error')}")

def update_application(app_id, company_name, job_title, recruiter, status, applied_date, job_url, notes):
    """Update an application in the backend"""
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Prepare the payload
        payload = {
            'user_id': st.session_state.user_id,  # Include user_id as required by the backend
            'company_name': company_name,
            'job_title': job_title,
            'recruiter': recruiter,
            'status': status,
            'applied_date': applied_date.isoformat() if applied_date else None,
            'job_url': job_url,
            'notes': notes
        }
        
        response = requests.put(
            f"{BACKEND_URL}/application/{app_id}",
            json=payload,  # Use json parameter instead of data
            headers=headers
        )
        
        if response.status_code == 200:
            return {'status': 'success', 'message': 'Application updated successfully'}
    except Exception as e:
        return {'status': 'error', 'message': f"{str(e)}, {response.status_code} - {response.text}"}

def create_application():
    """Create a new application in the backend"""
    st.subheader("Create New Application")
    with st.form(key="create_application_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name")
            job_title = st.text_input("Job Title")
            recruiter = st.text_input("Recruiter")
        
        with col2:
            status_options = ["interested", "applied", "interviewing", "offer", "rejected", "accepted"]
            status = st.selectbox("Status", options=status_options, index=1)
            applied_date = st.date_input("Applied Date", value=datetime.now().date())
            job_url = st.text_input("Job URL")
        
        notes = st.text_area("Notes", height=100)
        
        if st.form_submit_button("Create Application"):
            try:
                headers = {
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'user_id': st.session_state.user_id,
                    'company_name': company_name,
                    'job_title': job_title,
                    'recruiter': recruiter,
                    'status': status,
                    'applied_date': applied_date.isoformat(),
                    'job_url': job_url,
                    'notes': notes
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/application/",
                    json=payload,
                    headers=headers
                )
                if response.status_code == 200:
                    st.success("Application created successfully! Please check the Applications tab to see your new entry.")
                    st.rerun()  # This will refresh the page and clear the form
                else:
                    st.error(f"Error creating application: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error creating application: {str(e)}")

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
                        st.session_state.access_token = response.session.access_token
                        st.session_state.refresh_token = response.session.refresh_token

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
                        st.session_state.access_token = response.session.access_token
                        st.session_state.refresh_token = response.session.refresh_token

                        st.rerun()  # Refresh the app to show dashboard
                    else:
                        st.error("Registration failed. Please try again.")
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")

def profile_page():
    """Display user profile with data and bulk delete functionality"""
    st.subheader("👤 User Profile")
    
    # User information section
    st.markdown("### Personal Information")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {st.session_state.user_name or 'Not provided'}")
        st.write(f"**Email:** {st.session_state.user_email}")
        
    with col2:
        st.write(f"**User ID:** {st.session_state.user_id}")
        # You could add more user data here if available
    
    # Logout button
    if st.button("🚪 Logout", type="primary", use_container_width=True):
        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.rerun()
    
    st.markdown("---")
    
    # Application statistics
    applications = fetch_user_applications()
    total_apps = len(applications) if applications else 0
    
    st.markdown("### Application Statistics")
    
    if total_apps > 0:
        # Calculate status counts
        status_counts = {}
        for app in applications:
            status = app.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Display stats in columns
        stat_cols = st.columns(min(len(status_counts), 4))
        for i, (status, count) in enumerate(status_counts.items()):
            with stat_cols[i % 4]:
                st.metric(label=status.title(), value=count)
        
        st.success(f"**Total Applications:** {total_apps}")
    else:
        st.info("No applications found")
    
    st.markdown("---")
    
    # Danger zone - Delete all applications
    st.markdown("### ⚠️ Danger Zone")
    st.warning("**Warning:** This action cannot be undone!")
    
    if total_apps > 0:
        st.write(f"You currently have **{total_apps}** application(s) in your account.")
        
        # Confirmation checkbox
        confirm_delete = st.checkbox(
            f"I understand that this will permanently delete all {total_apps} of my job applications",
            key="confirm_bulk_delete"
        )
        
        # Big delete button (only enabled if checkbox is checked)
        if st.button(
            f"🗑️ DELETE ALL {total_apps} APPLICATIONS", 
            type="secondary",
            use_container_width=True,
            disabled=not confirm_delete,
            help="This will permanently delete all your job applications"
        ):
            # Perform bulk delete
            with st.spinner("Deleting all applications..."):
                response = delete_user_applications(st.session_state.user_id)
                
                if response['status'] == 'success':
                    st.success("✅ All applications have been successfully deleted!")
                
                    st.rerun()
                else:
                    st.error(f"❌ Error deleting applications: {response.get('message', 'Unknown error')}")
    else:
        st.info("No applications to delete.")

def dashboard_page():
    st.title("📊 Job Tracker Dashboard")
    st.header("Welcome to your Job Tracker!")
    
    # You can add tabs or different sections here
    dashboard_tab1, dashboard_tab2, dashboard_tab3 = st.tabs(["Applications", "Add Application", "Profile"])
    
    with dashboard_tab1:
        st.subheader("Your Job Applications")
        
        # Fetch and display applications
        applications = fetch_user_applications()
        if applications:
            st.write(f"You have {len(applications)} application(s)")
            
            # Create cards for each application
            for app in applications:
                create_application_card(app)
        else:
            st.info("No applications found. Start by adding your first job application!")
    
    with dashboard_tab2:
        create_application()
    
    with dashboard_tab3:
        profile_page()
    



# Main app logic
def main():
    # Check authentication status
    if not st.session_state.authenticated:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()

