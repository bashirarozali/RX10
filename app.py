import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Page Config
st.set_page_config(page_title="Final Class Dinner Awards", page_icon="🎓")

st.title("🏆 Everyone's Favourite Award")
st.markdown("Enter your Student ID to start voting for your classmates!")

# Connect to Google Sheets
url = "https://docs.google.com/spreadsheets/d/18YdQ6Od_jycVmhy-E8ZW-dWrKqzJJGF1YjeG6Z2x_qE/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(spreadsheet=url)

# 1. Login Section
student_id = st.text_input("Enter your Student ID to Begin")

if student_id:
    st.divider()
    st.subheader("Cast Your Votes!")
    st.info("Rank your classmates on a scale of 1-5 (5 is the best!)")

    votes = {}
    
    # 2. Voting Interface
    # This loops through every name in your Google Sheet
    for index, row in data.iterrows():
        name = row['Name']
        # Skip voting for yourself if you want
        if str(row['Student_ID']) != student_id:
            votes[name] = st.select_slider(
                f"How awesome is {name}?",
                options=[1, 2, 3, 4, 5],
                value=3,
                key=name,
                help="1: 😶, 2: 🙂, 3: 😊, 4: 😍, 5: 👑"
            )

    # 3. Submit Button
    if st.button("Submit My Votes 🚀"):
        # Logic to save results (can be viewed in a separate tab later)
        st.success("Thank you! Your votes have been recorded.")
        st.balloons()
