import streamlit as st
import mysql.connector
import pandas as pd

# --- 1. DATABASE CONNECTION (The "Inclusion" part) ---
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="thahdiln",  # <--- CHANGE THIS TO YOUR MYSQL PASSWORD
            database="payroll_db"
        )
    except mysql.connector.Error as err:
        st.error(f"Connection Error: {err}")
        return None

st.set_page_config(page_title="KTU Payroll System", layout="wide")
st.title("🏦 Employee Payroll Management System")

# --- 2. NAVIGATION SIDEBAR ---
menu = ["📊 View Dashboard", "👤 Add Employee", "💰 Process Monthly Salary"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- 3. DASHBOARD (Fetching from the VIEW) ---
if choice == "📊 View Dashboard":
    st.subheader("Monthly Payroll Report")
    st.info("This table joins Employees, Departments, and Salary using a SQL View.")
    
    conn = get_db_connection()
    if conn:
        query = "SELECT * FROM monthly_payroll_view"
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
        conn.close()

# --- 4. ADD NEW EMPLOYEE ---
elif choice == "👤 Add Employee":
    st.subheader("Register a New Employee")
    with st.form("emp_form"):
        name = st.text_input("Full Name")
        dept_id = st.selectbox("Department", [1, 2, 3], format_func=lambda x: {1:"Engineering", 2:"HR", 3:"Sales"}[x])
        basic_salary = st.number_input("Basic Salary", min_value=0.0, step=1000.0)
        
        if st.form_submit_button("Save to Database"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                sql = "INSERT INTO employees (name, department_id, basic_salary) VALUES (%s, %s, %s)"
                cursor.execute(sql, (name, dept_id, basic_salary))
                conn.commit()
                st.success(f"Successfully added {name}!")
                conn.close()

# --- 5. PROCESS SALARY (Trigger in Action) ---
elif choice == "💰 Process Monthly Salary":
    st.subheader("Generate Monthly Pay")
    st.warning("The Net Salary is automatically calculated by the Database Trigger.")
    
    with st.form("salary_form"):
        emp_id = st.number_input("Employee ID", min_value=1, step=1)
        month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June"])
        bonus = st.number_input("Bonus", min_value=0.0)
        deductions = st.number_input("Deductions", min_value=0.0)
        
        if st.form_submit_button("Generate & Calculate"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                # Note: We do NOT send net_salary here. 
                # The TRIGGER in MySQL calculates it automatically!
                sql = "INSERT INTO salary_details (employee_id, month, year, bonus, deductions) VALUES (%s, %s, 2026, %s, %s)"
                cursor.execute(sql, (emp_id, month, bonus, deductions))
                conn.commit()
                st.success("Record saved! Check the Dashboard for the calculated Net Salary.")
                conn.close()
