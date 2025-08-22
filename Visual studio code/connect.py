import streamlit as st
import datetime
import pandas as pd

import mysql.connector

con = mysql.connector.connect(host="localhost",user="root",password="root",port=3306,database="gym_management")
res = con.cursor()

if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
if 'customer_logged_in' not in st.session_state:
    st.session_state.customer_logged_in = False
    st.session_state.customer_id = None
    st.session_state.customer_name = None
rad = st.sidebar.radio("LOGIN",["Admin login","Customer login","Trainer login"])



st.title("Gym_Administration_system")

if rad == "Admin login" and not st.session_state['admin_logged_in']:
    user = st.text_input("Enter the username")
    password = st.text_input("Enter the password",type="password")
    button = st.button("Login")
    if user == "gym" and password == "gym123":
        st.session_state['admin_logged_in'] = True
        st.success("Login successful!")
    else:
        st.error("Invalid credentials")

if rad == "Admin login" and st.session_state['admin_logged_in']:
    st.sidebar.success("Logged in as Admin")
    update_expired_qry = """
    UPDATE payments p
    JOIN members m ON p.member_id = m.member_id AND p.plan_id = m.plan_id
    SET p.receipt_status = 'Expired'
    WHERE m.expiry_date < CURDATE() AND p.receipt_status != 'Expired';
    """
    try:
        res.execute(update_expired_qry)
        con.commit()
    except Exception as e:
        st.error(f"Failed to update expired payments: {e}")
    ask = st.sidebar.selectbox("Manage Members",["Add new member","Add new trainer","Add membership","Add payment","Pay trainer"])
    if ask == "Add new member":
        st.header("Add New Member")

        m_name, phone_no = st.columns(2)
        name = m_name.text_input("Name")
        phone = phone_no.text_input("Mobile Number") 

        plan_col, trainer_col = st.columns(2)
        plan_id = plan_col.text_input("Plan ID")
        trainer_id = trainer_col.number_input("Trainer ID", step=1, format="%d")

        join_date_col, expire_col = st.columns(2)
        joined_date = join_date_col.date_input("Joined Date", value=datetime.date.today())


        default_expiry = datetime.date.today()
        if plan_id and joined_date:
            try:
                res.execute("SELECT duration_days FROM membership_types WHERE plan_id = %s", (plan_id,))
                duration_result = res.fetchone()
                if duration_result:
                    duration_days = duration_result[0]
                    default_expiry = joined_date + datetime.timedelta(days=duration_days)
            except:
                pass  

        expiry_date = expire_col.date_input("Expiry Date", value=default_expiry)

        user_col, pass_col = st.columns(2)
        username = user_col.text_input("Username")
        password = pass_col.text_input("Password", type="password")

        status = st.text_input("Status")

        if st.button("Add Member"):
            insert_member_qry = """
                INSERT INTO members 
                (name, phone, joined_date, plan_id, expiry_date, status, trainer_id, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            member_val = (name, phone, joined_date, plan_id, expiry_date, status, trainer_id, username, password)
            res.execute(insert_member_qry, member_val)
            con.commit()

            new_member_id = res.lastrowid

            res.execute("SELECT cost_of_plan FROM membership_types WHERE plan_id = %s", (plan_id,))
            plan_data = res.fetchone()

            if plan_data:
                cost = plan_data[0]
                today = datetime.date.today()
                receipt_status = "Paid"

                insert_payment_qry = """
                    INSERT INTO payments (member_id, amount, payment_date, plan_id, receipt_status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                payment_val = (new_member_id, cost, today, plan_id, receipt_status)
                res.execute(insert_payment_qry, payment_val)
                con.commit()

                st.success("Member and payment added successfully!")
            else:
                st.warning("Plan ID not found. Payment not added.")


    elif ask == "Add new trainer":
        st.header("Add New Trainer")

        tname_col, phone_col = st.columns(2)
        trainer_name = tname_col.text_input("Trainer Name")
        phone_no = phone_col.text_input("Mobile Number")

        join_col, speci_col = st.columns(2)
        joined_date = join_col.date_input("Joined Date").strftime('%Y-%m-%d')  

        specialization = speci_col.text_input("Specialization")

        sal_col = st.columns(1)[0]
        salary = sal_col.number_input("Salary", step=0.01, format="%.2f")

        user_col, pass_col = st.columns(2)
        username = user_col.text_input("Username")
        password = pass_col.text_input("Password", type="password")

        if st.button("Add Trainer"):
            qry = """
                INSERT INTO trainer 
                (trainer_name, phone_no, joined_date, specialization, salary, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            val = (trainer_name, phone_no, joined_date, specialization, salary, username, password)
            try:
                res.execute(qry, val)
                con.commit()
                st.success("Trainer added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
    elif ask == "Add membership":
        st.header("Add Membership")
        Plan_type = st.selectbox("Select Plan Duration", ["Monthly", "Half-Yearly", "Yearly"])
        duration_days = st.number_input("Enter Number of days", min_value=1)
        cost_of_plan = st.number_input("Enter cost of plan", min_value=1)

        if st.button("Submit"):
            insert_query = """
                INSERT INTO membership_types (plan_type, duration_days, cost_of_plan)
                VALUES (%s, %s, %s)
            """
            res.execute(insert_query, (Plan_type, duration_days, cost_of_plan))
            con.commit()
            st.success("Membership plan added successfully!") 
    
    elif ask == "Add payment":
        st.header("Renew Membership for Expired Member")


        res.execute("""
            SELECT m.member_id, m.name 
            FROM members m
            JOIN payments p ON m.member_id = p.member_id
            WHERE m.expiry_date < CURDATE() AND p.receipt_status = 'Expired'
        """)
        expired_members = res.fetchall()

        if expired_members:
            member_dict = {f"{member_id} - {name}": member_id for member_id, name in expired_members}
            selected_member = st.selectbox("Select Expired Member", list(member_dict.keys()))
            member_id = member_dict[selected_member]

            res.execute("SELECT plan_id, plan_type FROM membership_types")
            plans = res.fetchall()
            plan_dict = {f"{pid} - {ptype}": pid for pid, ptype in plans}
            selected_plan = st.selectbox("Select New Plan", list(plan_dict.keys()))
            plan_id = plan_dict[selected_plan]

            res.execute("SELECT duration_days, cost_of_plan FROM membership_types WHERE plan_id = %s", (plan_id,))
            plan_data = res.fetchone()
            duration_days, cost = plan_data

            joined_date = st.date_input("Renewal Date", value=datetime.date.today())
            expiry_date = joined_date + datetime.timedelta(days=duration_days)
            status = st.text_input("Status", value="Active")

            if st.button("Renew Membership"):
                update_member_qry = """
                    UPDATE members
                    SET plan_id = %s, joined_date = %s, expiry_date = %s, status = %s
                    WHERE member_id = %s
                """
                res.execute(update_member_qry, (plan_id, joined_date, expiry_date, status, member_id))

            
                insert_payment_qry = """
                    INSERT INTO payments (member_id, amount, payment_date, plan_id, receipt_status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                res.execute(insert_payment_qry, (member_id, cost, joined_date, plan_id, "Paid"))
                con.commit()

                st.success("Membership renewed and payment added successfully!")
        else:
            st.warning("No expired members available.")

    elif ask == "Pay trainer":
        st.header("Pay Monthly Salary to Trainers")

        today = datetime.date.today()
        current_month = today.strftime("%B %Y")

        update_expired_qry = """
            UPDATE trainer_payments
            SET status = 'Pending'
            WHERE expiry_date < %s AND status != 'Pending'
        """
        try:
            res.execute(update_expired_qry, (today,))
            con.commit()
        except Exception as e:
            st.error(f"Failed to update expired payments: {e}")


        res.execute("SELECT trainer_id, trainer_name, salary FROM trainer")
        trainers = res.fetchall()
        res.execute("""
            SELECT trainer_id, status FROM trainer_payments
            WHERE payment_month = %s OR status = 'Pending'
        """, (current_month,))
        payments = res.fetchall()
        payment_status_map = {row[0]: row[1] for row in payments}
        unpaid_trainers = []
        for tid, name, salary in trainers:
            if tid not in payment_status_map or payment_status_map.get(tid) == 'Pending':
                unpaid_trainers.append((tid, name, salary))

        if unpaid_trainers:
            trainer_dict = {f"{tid} - {name}": (tid, salary) for tid, name, salary in unpaid_trainers}
            selected = st.selectbox("Select Trainer to Pay", list(trainer_dict.keys()))
            trainer_id, salary = trainer_dict[selected]

            payment_date = st.date_input("Payment Date", value=today)
            status = st.selectbox("Status", ["Paid", "Pending"], index=0)

            if st.button("Pay Salary"):
                expiry_date = payment_date + datetime.timedelta(days=30)
                insert_qry = """
                    INSERT INTO trainer_payments 
                    (trainer_id, amount, payment_date, payment_month, status, expiry_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                res.execute(insert_qry, (trainer_id, salary, payment_date, current_month, status, expiry_date))
                con.commit()
                st.success(f"Salary paid to trainer for {current_month}.")
        else:
            st.info(f"All trainers have been paid and no pending payments exist for {current_month}.")



    if st.sidebar.button("Logout", key="admin_logout_btn"):
            st.session_state.admin_logged_in = False
            st.success("Logged out successfully!")
            st.rerun()
                

elif rad == "Customer login":
    if not st.session_state.customer_logged_in:
        st.header("Customer Login")
        cus_id = st.number_input("Enter your Member ID", min_value=1, step=1, key="cust_id_input")
        password = st.text_input("Enter Password", type="password")

        if st.button("Login"):
            qry = "SELECT * FROM members WHERE member_id = %s AND password = %s"
            res.execute(qry, (cus_id, password))
            member = res.fetchone()

            if member:
                st.session_state.customer_logged_in = True
                st.session_state.customer_id = member[0]
                st.session_state.customer_name = member[1]
                st.success(f"Login successful! Welcome, {member[1]}")
                st.rerun()
            else:
                st.error("Invalid Member ID or Password")

    else:
        cus_id = st.session_state.customer_id
        st.sidebar.success(f"Logged in as {st.session_state.customer_name}")
        ask = st.sidebar.selectbox("Attendance", ["Check in", "Check out"])

        st.subheader("📋Member Attendance")

        if ask == "Check in":
            check_in_date = st.date_input("Check-In Date", value=datetime.date.today(), key="cust_checkin_date")
            check_in_time = st.time_input("Check-In Time", value=datetime.datetime.now().time(), key="cust_checkin_time")
            status = st.selectbox("Status", ["Present", "Absent", "Late"], key="cust_status")

            if st.button("Submit Check-In"):
                insert_qry = """
                    INSERT INTO member_attendance (member_id, check_in_date, check_in_time, status)
                    VALUES (%s, %s, %s, %s)
                """
                res.execute(insert_qry, (
                    cus_id,
                    check_in_date,
                    datetime.datetime.combine(check_in_date, check_in_time),
                    status
                ))
                con.commit()
                st.success("Check-in recorded successfully!")

        elif ask == "Check out":
            check_out_time = st.time_input("Check-Out Time", value=datetime.datetime.now().time(), key="cust_checkout_time")

            if st.button("Submit Check-Out"):
                update_qry = """
                    UPDATE member_attendance
                    SET check_out_time = %s
                    WHERE member_id = %s
                    AND check_out_time IS NULL
                    ORDER BY attendance_id DESC
                    LIMIT 1
                """
                res.execute(update_qry, (
                    datetime.datetime.combine(datetime.date.today(), check_out_time),
                    cus_id
                ))
                con.commit()
                st.success("Check-out recorded successfully!")

        if st.sidebar.button("Logout"):
            st.session_state.customer_logged_in = False
            st.session_state.customer_id = None
            st.session_state.customer_name = None
            st.success("Logged out successfully!")
            st.rerun()

elif rad == "Trainer login":
    if not st.session_state.get("trainer_logged_in", False):
        st.header("Trainer Login")
        trainer_id = st.number_input("Enter your Trainer ID", min_value=1, step=1, key="trainer_id_input")
        password = st.text_input("Enter Password", type="password")

        if st.button("Login", key="trainer_login_btn"):
            qry = "SELECT * FROM trainer WHERE trainer_id = %s AND password = %s"
            res.execute(qry, (trainer_id, password))
            trainer = res.fetchone()

            if trainer:
                st.session_state.trainer_logged_in = True
                st.session_state.trainer_id = trainer[0]
                st.session_state.trainer_name = trainer[1]
                st.success(f"Login successful! Welcome, {trainer[1]}")
                st.rerun()
            else:
                st.error("Invalid Trainer ID or Password")

    else:
        trainer_id = st.session_state.trainer_id
        st.sidebar.success(f"Logged in as {st.session_state.trainer_name}")
        ask = st.sidebar.selectbox("Attendance", ["Check in", "Check out"])

        st.subheader("📋Trainer Attendance")

        if ask == "Check in":
            check_in_date = st.date_input("Check-In Date", value=datetime.date.today(), key="trainer_checkin_date")
            check_in_time = st.time_input("Check-In Time", value=datetime.datetime.now().time(), key="trainer_checkin_time")
            status = st.selectbox("Status", ["Present", "Absent", "Late"], key="trainer_status")

            if st.button("Submit Check-In", key="trainer_checkin_btn"):
                insert_qry = """
                    INSERT INTO trainer_attendance (trainer_id, check_in_date, check_in_time, status)
                    VALUES (%s, %s, %s, %s)
                """
                res.execute(insert_qry, (
                    trainer_id,
                    check_in_date,
                    datetime.datetime.combine(check_in_date, check_in_time),
                    status
                ))
                con.commit()
                st.success("Check-in recorded successfully!")

        elif ask == "Check out":
            check_out_time = st.time_input("Check-Out Time", value=datetime.datetime.now().time(), key="trainer_checkout_time")

            if st.button("Submit Check-Out", key="trainer_checkout_btn"):
                update_qry = """
                    UPDATE trainer_attendance
                    SET check_out_time = %s
                    WHERE trainer_id = %s
                    AND check_out_time IS NULL
                    ORDER BY attendance_id DESC
                    LIMIT 1
                """
                res.execute(update_qry, (
                    datetime.datetime.combine(datetime.date.today(), check_out_time),
                    trainer_id
                ))
                con.commit()
                st.success("Check-out recorded successfully!")

        if st.sidebar.button("Logout", key="trainer_logout_btn"):
            st.session_state.trainer_logged_in = False
            st.session_state.trainer_id = None
            st.session_state.trainer_name = None
            st.success("Logged out successfully!")
            st.rerun()
