import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import mysql.connector

# Database connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="manus12345",
    database="faculty_q"
)

db_cursor = db_connection.cursor()

def validate_login(role):
    username = username_entry.get()
    password = password_entry.get()
    
    #check credentials
    try:
        db_cursor.execute("SELECT * FROM authorization WHERE email = %s AND password = %s AND role = %s", (username, password, role))
        user = db_cursor.fetchone()
        id = user[0]

        if user:
            if role == "student":
                open_student_window(username)
            elif role == "faculty":
                open_faculty_window(username,id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    except Exception as e:
        messagebox.showerror("Login Failed", "Incorrect username or password")

def open_student_window(username):
    # new window for student
    student_window = tk.Tk()
    student_window.title("Student Window")

    #window size
    window_width = student_window.winfo_screenwidth() // 2
    window_height = student_window.winfo_screenheight() // 2
    student_window.geometry(f"{window_width}x{window_height}")
    window_x = (student_window.winfo_screenwidth() - window_width) // 2
    window_y = (student_window.winfo_screenheight() - window_height) // 2
    student_window.geometry(f"+{window_x}+{window_y}")

    heading = tk.Label(student_window, text=f"Welcome, {username}!", font=("Arial", 24, "bold"))
    heading.pack(pady=20)

    # Label and entry
    faculty_name_label = tk.Label(student_window, text="Faculty Name:", font=("Arial", 16))
    faculty_name_label.pack()
    faculty_name_entry = tk.Entry(student_window, font=("Arial", 16))
    faculty_name_entry.pack(pady=5)

    # Styleing
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", font=("Arial", 12), background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
    style.configure("Treeview.Cell", anchor="center")

    #Data in tabular form
    columns = ("Faculty ID", "Faculty Name", "Cabin Address", "Status")
    results_tree = ttk.Treeview(student_window, columns=columns, show="headings", height=20, style="Treeview")
    results_tree.heading("Faculty ID", text="Faculty ID")
    results_tree.heading("Faculty Name", text="Faculty Name")
    results_tree.heading("Cabin Address", text="Cabin Address")
    results_tree.heading("Status", text="Status")
    results_tree.pack(pady=10, expand=True, fill=tk.BOTH)

    #Quering database automatically
    def query_database(event=None):
        for row in results_tree.get_children():
            results_tree.delete(row)

        user_input = faculty_name_entry.get()
        if user_input.strip():

            db_cursor.execute("SELECT f.faculty_id, f.faculty_name, "
                              "CONCAT_WS(', ', c.cabin_no, c.floor_no, c.building_name, c.campus) AS cabin_address, "
                              "a.available "
                              "FROM faculty f "
                              "LEFT JOIN cabin c ON f.faculty_id = c.faculty_id "
                              "LEFT JOIN availability a ON f.faculty_id = a.faculty_id "
                              "WHERE f.faculty_name LIKE %s", (f"%{user_input}%",))
            results = db_cursor.fetchall()
            print(results)
            for row in results:
                status = "Available" if row[3] else "NOT Available"
                results_tree.insert("", "end", values=(row[0], row[1], row[2], status))

    def show_faculty_details(event):
        selected_item = results_tree.selection()[0]
        faculty_id = results_tree.item(selected_item, "values")[0]

        # faculty table
        db_cursor.execute("SELECT * FROM faculty WHERE faculty_id = %s", (faculty_id,))
        faculty_details = db_cursor.fetchone()

        # cabin table 
        db_cursor.execute("SELECT CONCAT_WS(', ', cabin_no, floor_no, building_name, campus) FROM cabin WHERE faculty_id = %s", (faculty_id,))
        cabin_details = db_cursor.fetchall()
        formatted_cabin_details = ", ".join([cabin[0] for cabin in cabin_details])

        # courses table 
        db_cursor.execute("SELECT course_id, course_name, slot FROM courses WHERE faculty_id = %s", (faculty_id,))
        courses_details = db_cursor.fetchall()

        #availability table
        db_cursor.execute("SELECT available FROM availability WHERE faculty_id = %s", (faculty_id,))
        availability = db_cursor.fetchone()[0]

        # display faculty full details
        details_window = tk.Toplevel(student_window)
        details_window.title("Faculty Details")

        #labels
        labels = ["Faculty ID:", "Faculty Name:", "Cabin Address:", "Availability:"]
        details = [faculty_details[1], faculty_details[0], formatted_cabin_details, "Available" if availability else "Not Available"]
        for label, detail in zip(labels, details):
            detail_label = tk.Label(details_window, text=f"{label} ", font=("Arial", 12, "bold"))
            detail_label.pack(padx=10, pady=2)

            # color for availability text
            if label == "Availability:":
                color = "green" if availability else "red"
                availability_label = tk.Label(details_window, text=detail, font=("Arial", 12), fg=color)
                availability_label.pack(padx=10, pady=2)
            else:
                other_label = tk.Label(details_window, text=detail, font=("Arial", 12))
                other_label.pack(padx=10, pady=2)

        # Display courses details
        if courses_details:
            courses_label = tk.Label(details_window, text="Courses:", font=("Arial", 12, "bold"))
            courses_label.pack(padx=10, pady=5)

            for course in courses_details:
                course_id_label = tk.Label(details_window, text=f"Course ID: {course[0]}", font=("Arial", 12))
                course_id_label.pack(padx=10, pady=2)

                course_name_label = tk.Label(details_window, text=f"Course Name: {course[1]}", font=("Arial", 12))
                course_name_label.pack(padx=10, pady=2)

                course_slot_label = tk.Label(details_window, text=f"Slot: {course[2]}", font=("Arial", 12))
                course_slot_label.pack(padx=10, pady=2)

    faculty_name_entry.bind("<KeyRelease>", query_database)
    results_tree.bind("<Double-1>", show_faculty_details)
    student_window.mainloop()

def open_faculty_window(username,faculty_id):
    faculty_window = tk.Toplevel()
    faculty_window.title("Faculty Window")

    heading = tk.Label(faculty_window, text=f"Welcome, {username}!", font=("Arial", 24, "bold"))
    heading.pack(pady=20)

    availability_var = tk.StringVar(value="Available")

    def set_availability():
        status = availability_var.get()
        status_value = 1 if status == "Available" else 0
        update_query = "UPDATE availability SET available = %s WHERE faculty_id = %s"
        db_cursor.execute(update_query, (status_value, faculty_id))
        db_connection.commit()
        print(f"Status set to: {status} (Value: {status_value})")
        faculty_window.destroy() 

    available_radio = tk.Radiobutton(faculty_window, text="Available", variable=availability_var, value="Available", font=("Arial", 16))
    available_radio.pack(pady=10)

    unavailable_radio = tk.Radiobutton(faculty_window, text="Unavailable", variable=availability_var, value="Unavailable", font=("Arial", 16))
    unavailable_radio.pack(pady=10)

    confirm_button = tk.Button(faculty_window, text="Update", command=set_availability, font=("Arial", 16))
    confirm_button.pack(pady=10)

    faculty_window.mainloop()


def show_success_message():
    success_window = tk.Toplevel(window)
    success_window.title("Success")
    success_label = tk.Label(success_window, text="Updated Successfully", font=("Arial", 24))
    success_label.pack(pady=20)

# main window
window = tk.Tk()
window.title("Login Page")

heading = tk.Label(window, text="FACULTY CABIN QUERIER", font=("Arial", 24, "bold"))
heading.pack(pady=20)

# Username label 
username_label = tk.Label(window, text="Username:", font=("Arial", 16))
username_label.pack()
username_entry = tk.Entry(window, font=("Arial", 16))
username_entry.pack(pady=5)

# Password label 
password_label = tk.Label(window, text="Password:", font=("Arial", 16))
password_label.pack()
password_entry = tk.Entry(window, show="*", font=("Arial", 16))
password_entry.pack(pady=5)

# Login buttons
login_student_button = tk.Button(window, text="Login as Student", command=lambda: validate_login("student"), font=("Arial", 16))
login_student_button.pack(pady=10)

login_faculty_button = tk.Button(window, text="Login as Faculty", command=lambda: validate_login("faculty"), font=("Arial", 16))
login_faculty_button.pack(pady=10)

window.mainloop()