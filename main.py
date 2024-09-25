import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

user_dir = "users"
cred_file = "credentials.json"

if not os.path.exists(user_dir):
    os.makedirs(user_dir)

# Load credentials from the JSON file
def load_credentials():
    if os.path.exists(cred_file):
        try:
            with open(cred_file, "r") as f:
                data = f.read().strip()
                if not data:  # Check if the file is empty
                    return {}  # Return an empty dictionary if empty
                return json.loads(data)
        except json.JSONDecodeError:
            # If there is an error in decoding, return an empty dictionary
            return {}
    return {}

# Save updated credentials to the JSON file
def save_credentials(credentials):
    with open(cred_file, "w") as f:
        json.dump(credentials, f, indent=4)

# Check if a user with the email already exists
def user_exists(email):
    credentials = load_credentials()
    return email in credentials

# Get user information based on email
def get_user(email):
    credentials = load_credentials()
    return credentials.get(email, None)

# Add a new user and save it in credentials
def add_user(name, phone, dob, email, password):
    credentials = load_credentials()
    credentials[email] = {"name": name, "phone": phone, "dob": str(dob), "password": password}
    save_credentials(credentials)

# Create a unique folder name for the user based on name and email
def folder_name(name, email):
    email_identifier = email.split('@')[0]
    return f"{name}_{email_identifier}"

# Sign up page logic
def signup():
    st.title("Welcome to the Sign Up Page")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    dob = st.date_input("DOB")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')

    if st.button("Sign Up"):
        if user_exists(email):
            st.error("User with this email already exists. Please log in.")
        else:
            # Add the new user to the credentials
            add_user(name, phone, dob, email, password)

            # Create a user folder after successful sign-up
            folder_path = os.path.join(user_dir, folder_name(name, email))
            os.mkdir(folder_path)  
            
            # Set session state to logged in
            st.session_state['logged_in_user'] = email
            st.success(f"Sign Up successful. Redirecting to Input Marks page...")
            st.experimental_rerun()  # Immediately rerun the app to redirect

# Login page logic
def login():
    st.title("Welcome to the Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        user_data = get_user(email)
        if user_data and user_data['password'] == password:
            st.session_state['logged_in_user'] = email
            st.success(f"Login successful. Redirecting to Input Marks page...")
            st.rerun()  # Immediately rerun the app to redirect
        else:
            st.error("Invalid email or password. Please try again.")

# Input Marks and Report Generation on the same page
def input_marks_and_generate_report():
    st.title(f"Welcome {st.session_state['logged_in_user']}")
    user_data = get_user(st.session_state['logged_in_user'])
    folder_path = os.path.join(user_dir, folder_name(user_data['name'], st.session_state['logged_in_user']))

    subjects = ["Maths", "Science", "English", "History", "Geography", "Physics", "Chemistry"]
    marks = {}

    for subject in subjects:
        marks[subject] = st.slider(f"Choose your marks for {subject}", 0, 100)

    if st.button("Submit"):
        df = pd.DataFrame(list(marks.items()), columns=['Subject', 'Marks'])
        file_path = os.path.join(folder_path, "marks.csv")
        df.to_csv(file_path, index=False)
        st.success("Marks saved successfully")
        
        # Generate graphs after marks are saved
        generate_report(df)

# Report Generation function (to be called after marks submission)
def generate_report(df):
    st.write("## Average Marks Chart (Bar Graph)")
    bar_chart = px.bar(df, x='Subject', y='Marks')
    st.plotly_chart(bar_chart)

    st.write("## Marks as per each subject (Line Graph)")
    line_chart = px.line(df, x='Subject', y='Marks')
    st.plotly_chart(line_chart)

    st.write("## Marks as per each subject (Pie Chart)")
    pie_chart = px.pie(df, names='Subject', values='Marks')
    st.plotly_chart(pie_chart)

# Initialize session state
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

# Main function to handle page navigation and user flow
def main():
    # Sidebar only shows "Login" and "Sign Up" until the user logs in
    if st.session_state['logged_in_user'] is None:
        st.sidebar.title("Menu")
        menu = st.sidebar.selectbox("Choose an option", ["Login", "Sign Up"])

        if menu == "Login":
            login()
        elif menu == "Sign Up":
            signup()
    else:
        # Once logged in, redirect directly to marks input and report generation
        input_marks_and_generate_report()

if __name__ == "__main__":
    main()

       



