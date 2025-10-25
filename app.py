import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text

# -------------------- DATABASE CONNECTION --------------------
DB_USER = "root"             # change this
DB_PASSWORD = "0000" # change this
DB_HOST = "localhost"
DB_NAME = "student_project"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="🎓 Student Project Tracer", layout="wide")
st.title("🎓 Student Project Tracer")

# -------------------- SIDEBAR MENU --------------------
menu = st.sidebar.radio("Select Role", ["Admin Login", "Student Login"])

# -------------------- ADMIN LOGIN --------------------
if menu == "Admin Login":
    st.subheader("🔑 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.success("✅ Login Successful!")
            st.session_state["admin_logged_in"] = True
        else:
            st.error("❌ Invalid username or password")

    if st.session_state.get("admin_logged_in", False):
        st.subheader("📋 Admin Dashboard")

        admin_option = st.selectbox(
            "Choose Action",
            ["Add New Project", "View All Projects", "Branch-wise Analysis"]
        )

        # ---------- ADD NEW PROJECT ----------
        if admin_option == "Add New Project":
            st.markdown("### ➕ Enter Project Details")
            project_id = st.number_input("Project ID", min_value=1)
            project_name = st.text_input("Project Name")
            group_leader_name = st.text_input("Group Leader Name")
            group_members = st.text_area("Group Members (comma separated)")
            branch = st.selectbox("Branch", ["CSE", "ISE", "DS", "EC"])
            competition_date = st.date_input("Competition Date")
            competition_venue = st.text_input("Competition Venue")
            status = st.selectbox("Competition Status", ["Win", "Loss", "Pending"])

            with st.form("add_project_form"):
                project_id = st.number_input("Project ID", min_value=1, value=1)
                project_name = st.text_input("Project Name")
                group_leader_name = st.text_input("Group Leader Name")
                group_members = st.text_area("Group Members (comma separated)")
                branch = st.selectbox("Branch", ["CSE", "ISE", "DS", "EC"])
                competition_date = st.date_input("Competition Date")
                competition_venue = st.text_input("Competition Venue")
                status = st.selectbox("Competition Status", ["Win", "Loss", "Pending"])

                submitted = st.form_submit_button("Submit Project")

                if submitted:
                    # ✅ Validation
                    if (
                        project_id > 0
                        and project_name.strip()
                        and group_leader_name.strip()
                        and group_members.strip()
                        and branch
                        and competition_date
                        and competition_venue.strip()
                        and status
                    ):
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO project_details 
                                    (project_id, project_name, group_leader_name, group_members, branch, compititon_date, compitition_venue, status)
                                    VALUES (:project_id, :project_name, :group_leader_name, :group_members, :branch, :competition_date, :competition_venue, :status)
                                """), {
                                    "project_id": project_id,
                                    "project_name": project_name,
                                    "group_leader_name": group_leader_name,
                                    "group_members": group_members,
                                    "branch": branch,
                                    "competition_date": competition_date,
                                    "competition_venue": competition_venue,
                                    "status": status
                                })
                            st.success("✅ Project added successfully!")
                            st.session_state["refresh_table"] = True
                        except Exception as e:
                            st.error(f"❌ Error inserting record: {e}")
                    else:
                        st.warning("⚠️ Please fill all fields before submitting.")



        # ---------- VIEW ALL PROJECTS ----------
        if admin_option == "View All Projects" or st.session_state.get("refresh_table", False):
            st.markdown("### 📊 Registered Projects")
            try:
                df = pd.read_sql("SELECT * FROM project_details", engine)
                st.dataframe(df, use_container_width=True)
                st.session_state["refresh_table"] = False
            except Exception as e:
                st.error(f"❌ Error reading data: {e}")

        # ---------- BRANCH-WISE ANALYSIS ----------
        if admin_option == "Branch-wise Analysis":
            st.markdown("### 📈 Branch-wise Win Statistics")
            try:
                df = pd.read_sql("SELECT branch, status FROM project_details", engine)
                if df.empty:
                    st.info("No data available for analysis yet.")
                else:
                    win_data = df[df["status"] == "Win"].groupby("branch").size()
                    st.bar_chart(win_data)
            except Exception as e:
                st.error(f"❌ Error fetching data for chart: {e}")

# -------------------- STUDENT LOGIN --------------------
elif menu == "Student Login":
    st.subheader("🎓 Student Login")
    usn = st.text_input("Enter USN")
    dob = st.date_input("Enter Date of Birth")

    if st.button("Login as Student"):
        if usn and dob:  # dummy login (no verification)
            st.success("✅ Logged in as Student (Read-Only Mode)")
            try:
                df = pd.read_sql("SELECT * FROM project_details", engine)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error fetching data: {e}")
        else:
            st.warning("⚠️ Please enter valid USN and DOB")
