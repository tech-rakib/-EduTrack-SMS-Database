import tkinter as tk 
from tkinter import ttk, messagebox 
from contextlib import contextmanager 
import pymysql 
import hashlib 

 
DB_CONFIG = { 
    "host": "localhost", 
    "user": "root", 
    "password": "Rakib 125043",   # change if your MySQL root has a password 
    "database": "student_db", 
    "charset": "utf8mb4", 
    "cursorclass": pymysql.cursors.DictCursor 
} 

# ------------------------- 
# Utilities 
# ------------------------- 
def hash_password(plain: str) -> str: 
    """Simple SHA-256 hashing for stored passwords (no salt for simplicity).""" 
    return hashlib.sha256(plain.encode("utf-8")).hexdigest() 

@contextmanager 
def db_connection(): 
    """Context manager for DB connections. Commits on success, rollbacks on exception.""" 
    con = pymysql.connect(**DB_CONFIG) 
    try: 
        cur = con.cursor() 
        yield con, cur 
        con.commit() 
    except Exception: 
        con.rollback() 
        raise 
    finally: 
        con.close() 

# ------------------------- 
# Initialize DB and seed users 
# ------------------------- 
def init_db(): 
    """ 
    Ensures the database exists, creates tables if missing, and seeds the three user accounts. 
    """ 
    try:
        # First try to connect to MySQL server (without database)
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            charset="utf8mb4"
        )
        
        with conn.cursor() as c:
            # Create database if not exists
            c.execute("CREATE DATABASE IF NOT EXISTS student_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        
        conn.commit()
        conn.close()
        print("✓ Database created or already exists")
    except Exception as e:
        print(f"⚠ Warning: Could not create database: {e}")
        # Continue - database might already exist

    # Now connect to the database and create tables
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            # users table 
            cur.execute(""" 
            CREATE TABLE IF NOT EXISTS users ( 
                id INT AUTO_INCREMENT PRIMARY KEY, 
                username VARCHAR(100) UNIQUE NOT NULL, 
                password_hash VARCHAR(255) NOT NULL, 
                role ENUM('admin','teacher','student') NOT NULL, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 
            """) 
            # student table 
            cur.execute(""" 
            CREATE TABLE IF NOT EXISTS student ( 
                rollNo VARCHAR(50) PRIMARY KEY, 
                name VARCHAR(255) NOT NULL, 
                fname VARCHAR(255) NOT NULL, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 
            """) 
            # courses table 
            cur.execute(""" 
            CREATE TABLE IF NOT EXISTS courses ( 
                course_id INT AUTO_INCREMENT PRIMARY KEY, 
                course_name VARCHAR(255) UNIQUE NOT NULL, 
                teacher VARCHAR(255), 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 
            """) 
            # enrollments 
            cur.execute(""" 
            CREATE TABLE IF NOT EXISTS enrollments ( 
                enroll_id INT AUTO_INCREMENT PRIMARY KEY, 
                rollNo VARCHAR(50) NOT NULL, 
                course_id INT NOT NULL, 
                grade VARCHAR(10), 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                FOREIGN KEY (rollNo) REFERENCES student(rollNo) ON DELETE CASCADE ON UPDATE CASCADE, 
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE, 
                UNIQUE KEY unique_enroll (rollNo, course_id) 
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 
            """) 

            # seed users if not exists (three accounts) 
            seeds = [ 
                ("admin", "admin123", "admin"), 
                ("teacher", "teacher123", "teacher"), 
                ("student", "student123", "student"), 
            ] 
            for username, pwd, role in seeds: 
                cur.execute("SELECT id FROM users WHERE username=%s", (username,)) 
                if not cur.fetchone(): 
                    cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", 
                                (username, hash_password(pwd), role))
            
            # Add some sample courses if not exists
            sample_courses = [
                ("Mathematics", "Dr. Smith"),
                ("Physics", "Dr. Johnson"),
                ("Chemistry", "Dr. Williams"),
                ("Biology", "Dr. Brown"),
                ("English", "Dr. Davis"),
                ("Computer Science", "Dr. Miller"),
            ]
            for course_name, teacher in sample_courses:
                cur.execute("SELECT course_id FROM courses WHERE course_name=%s", (course_name,))
                if not cur.fetchone():
                    cur.execute("INSERT INTO courses (course_name, teacher) VALUES (%s, %s)", 
                               (course_name, teacher))
            
            conn.commit()
        conn.close()
        print("✓ Tables created and seeded successfully")
        return True
    except pymysql.err.OperationalError as e:
        print(f"✗ Database connection error: {e}")
        print("\nPlease make sure:")
        print("1. MySQL server is running (start XAMPP/WAMP)")
        print("2. Database credentials are correct")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

# ------------------------- 
# Application 
# ------------------------- 
class StudentProApp: 
    def __init__(self, root): 
        self.root = root 
        self.root.title("Professional Student Management System") 
        self.root.geometry("1200x720") 
        self.root.configure(bg="#f5f6fa") 
        self.root.minsize(1000, 600) 

        self.current_user = None  # will store {'id', 'username', 'role'} 

        # Initialize all frames 
        self.setup_frames() 
         
        # Show login screen 
        self.show_login() 

    def setup_frames(self): 
        """Setup all UI frames - called once at initialization""" 
        # Top bar 
        self.top_bar = tk.Frame(self.root, bg="#2f3640", height=60) 
        self.top_bar.pack(side="top", fill="x") 
        self.title_label = tk.Label(self.top_bar, text="Student Management System",  
                                   bg="#2f3640", fg="white", font=("Helvetica", 18, "bold")) 
        self.title_label.pack(pady=12) 

        # Container frames 
        self.container = tk.Frame(self.root, bg="#f5f6fa") 
        self.container.pack(fill="both", expand=True) 

        self.sidebar = tk.Frame(self.container, bg="#353b48", width=220) 
        self.sidebar.pack(side="left", fill="y") 

        self.main_area = tk.Frame(self.container, bg="#f5f6fa") 
        self.main_area.pack(side="right", fill="both", expand=True) 

        # inside main area: controls on top and table area below 
        self.controls_frame = tk.Frame(self.main_area, bg="#f5f6fa") 
        self.controls_frame.pack(side="top", fill="x") 

        self.table_frame = tk.Frame(self.main_area, bg="#f5f6fa") 
        self.table_frame.pack(side="top", fill="both", expand=True, padx=10, pady=6) 

        # create Treeview initially 
        self._create_treeview() 

    # ------------------------- 
    # Treeview helpers 
    # ------------------------- 
    def _create_treeview(self): 
        for w in self.table_frame.winfo_children(): 
            w.destroy() 
        columns = ("Roll No", "Name", "Father Name", "Courses & Grades") 
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings") 
        for col in columns: 
            self.tree.heading(col, text=col) 
            if col == "Courses & Grades": 
                self.tree.column(col, width=450, anchor="w") 
            else: 
                self.tree.column(col, width=150, anchor="center") 
        self.tree.pack(side="left", fill="both", expand=True) 
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview) 
        scrollbar.pack(side="right", fill="y") 
        self.tree.configure(yscroll=scrollbar.set) 

    def clear_tree(self): 
        for iid in self.tree.get_children(): 
            self.tree.delete(iid) 

    # ------------------------- 
    # Login Screen 
    # ------------------------- 
    def show_login(self): 
        """Show login screen - hide sidebar and show login form""" 
        # Hide sidebar and clear everything 
        self.sidebar.pack_forget() 
        self.clear_controls() 
        self.clear_tree() 
         
        # Clear table frame and show login 
        for w in self.table_frame.winfo_children(): 
            w.destroy() 
         
        # Create login card 
        card = tk.Frame(self.table_frame, bg="white", bd=1, relief="solid", padx=20, pady=18) 
        card.place(relx=0.5, rely=0.4, anchor="center") 
         
        tk.Label(card, text="Login", bg="white", font=("Helvetica", 16, "bold")).pack(pady=(0,12)) 
        tk.Label(card, text="Username", bg="white").pack(anchor="w") 
        self.login_user_entry = tk.Entry(card, font=("Helvetica", 12), width=25) 
        self.login_user_entry.pack(fill="x", pady=(2,6)) 
        self.login_user_entry.focus_set() 
         
        tk.Label(card, text="Password", bg="white").pack(anchor="w") 
        self.login_pwd_entry = tk.Entry(card, show="*", font=("Helvetica", 12), width=25) 
        self.login_pwd_entry.pack(fill="x", pady=(2,8)) 
         
        # Bind Enter key to login 
        self.login_user_entry.bind('<Return>', lambda e: self.login_action()) 
        self.login_pwd_entry.bind('<Return>', lambda e: self.login_action()) 
         
        tk.Button(card, text="Login", bg="#44bd32", fg="white", font=("Helvetica", 12, "bold"), 
                  command=self.login_action, width=20).pack(fill="x", pady=(4,6)) 
        tk.Button(card, text="Quit", bg="#e84118", fg="white",  
                  command=self.root.quit, width=20).pack(fill="x") 

    def login_action(self): 
        username = self.login_user_entry.get().strip() 
        pwd = self.login_pwd_entry.get().strip() 
        if not username or not pwd: 
            messagebox.showerror("Error", "Enter username and password") 
            return 
        pwd_hash = hash_password(pwd) 
        try: 
            with db_connection() as (con, cur): 
                cur.execute("SELECT id, username, role FROM users WHERE username=%s AND password_hash=%s", (username, pwd_hash)) 
                user = cur.fetchone() 
        except Exception as e: 
            messagebox.showerror("DB Error", f"{e}") 
            return 

        if not user: 
            messagebox.showerror("Login failed", "Invalid credentials") 
            return 

        # success: set current user and build main UI 
        self.current_user = user 
        self._show_main_interface() 

    def _show_main_interface(self): 
        """Show the main interface after successful login""" 
        # Clear the table frame (removes login card) 
        for w in self.table_frame.winfo_children(): 
            w.destroy() 
         
        # Show sidebar and recreate treeview 
        self.sidebar.pack(side="left", fill="y") 
        self._create_treeview() 
         
        # Build sidebar and show dashboard 
        self.build_sidebar() 
        self.show_dashboard() 

    # ------------------------- 
    # Sidebar (role-based) 
    # ------------------------- 
    def build_sidebar(self): 
        for w in self.sidebar.winfo_children(): 
            w.destroy() 

        role = self.current_user["role"] 
        tk.Label(self.sidebar, text=f"User: {self.current_user['username']}",  
                bg="#353b48", fg="white", font=("Helvetica", 12, "bold")).pack(pady=(12,6)) 
        tk.Label(self.sidebar, text=f"Role: {role.title()}",  
                bg="#353b48", fg="white", font=("Helvetica", 10)).pack() 

        btn_cfg = {"font": ("Helvetica", 11, "bold"), "fg": "white", "bg": "#353b48", 
                   "activebackground": "#40739e", "bd": 0, "width": 22, "anchor": "w",  
                   "cursor": "hand2", "padx": 8} 

        # Common actions 
        tk.Button(self.sidebar, text="🏠 Dashboard", command=self.show_dashboard, **btn_cfg).pack(pady=8) 
        tk.Button(self.sidebar, text="🔍 Search Student", command=self.show_search, **btn_cfg).pack(pady=4) 
        tk.Button(self.sidebar, text="📄 View Courses & Teachers", command=self.show_courses_teachers, **btn_cfg).pack(pady=4) 

        if role in ("admin", "teacher"): 
            tk.Button(self.sidebar, text="➕ Add Student", command=self.show_add_student, **btn_cfg).pack(pady=4) 
            tk.Button(self.sidebar, text="🗑 Remove Student", command=self.show_remove_student, **btn_cfg).pack(pady=4) 
            tk.Button(self.sidebar, text="📝 Update Grades", command=self.show_update_grades, **btn_cfg).pack(pady=4) 

        if role == "admin": 
            tk.Button(self.sidebar, text="📚 Add Course", command=self.show_add_course, **btn_cfg).pack(pady=4) 
            tk.Button(self.sidebar, text="🎓 Assign Courses", command=self.show_assign_start, **btn_cfg).pack(pady=4) 
            tk.Button(self.sidebar, text="👩‍🏫 Manage Teachers", command=self.show_manage_teachers, **btn_cfg).pack(pady=4) 

        tk.Button(self.sidebar, text="🔒 Logout", command=self.logout, **btn_cfg).pack(side="bottom", pady=16) 

    def logout(self): 
        self.current_user = None 
        self.show_login() 

    # ------------------------- 
    # Dashboard 
    # ------------------------- 
    def show_dashboard(self): 
        # clear controls and repopulate tree 
        self.clear_controls() 
        self.clear_tree() 

        # optional: show small summary controls 
        summary_frame = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        summary_frame.pack(fill="x", padx=10, pady=6) 
        tk.Label(summary_frame, text=f"Logged in as: {self.current_user['username']} ({self.current_user['role']})", 
                 bg="#f5f6fa", font=("Helvetica", 11)).pack(side="left") 

        # fetch students and enrollments efficiently 
        try: 
            with db_connection() as (con, cur): 
                cur.execute("SELECT rollNo, name, fname FROM student ORDER BY created_at DESC") 
                students = cur.fetchall() 
                cur.execute("SELECT e.rollNo, c.course_name, e.grade FROM enrollments e JOIN courses c ON e.course_id=c.course_id") 
                enrolls = cur.fetchall() 
        except Exception as e: 
            messagebox.showerror("DB Error", str(e)) 
            return 

        enroll_map = {} 
        for row in enrolls: 
            enroll_map.setdefault(row["rollNo"], []).append(f"{row['course_name']} - Grade: {row['grade'] if row['grade'] else 'N/A'}") 

        for s in students: 
            courses_str = "\n".join(enroll_map.get(s["rollNo"], ["No courses enrolled"])) 
            self.tree.insert("", "end", values=(s["rollNo"], s["name"], s["fname"], courses_str)) 

    # ------------------------- 
    # Add Student (admin & teacher) 
    # ------------------------- 
    def show_add_student(self): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text="Add Student", bg="#f5f6fa", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w") 
        tk.Label(frm, text="Roll No", bg="#f5f6fa").grid(row=1, column=0, sticky="e", pady=4) 
        roll = tk.Entry(frm) 
        roll.grid(row=1, column=1, sticky="w", pady=4) 
        tk.Label(frm, text="Name", bg="#f5f6fa").grid(row=2, column=0, sticky="e", pady=4) 
        name = tk.Entry(frm) 
        name.grid(row=2, column=1, sticky="w", pady=4) 
        tk.Label(frm, text="Father Name", bg="#f5f6fa").grid(row=3, column=0, sticky="e", pady=4) 
        fname = tk.Entry(frm) 
        fname.grid(row=3, column=1, sticky="w", pady=4) 

        def action(): 
            r = roll.get().strip() 
            n = name.get().strip() 
            f = fname.get().strip() 
            if not (r and n and f): 
                messagebox.showerror("Error", "All fields required") 
                return 
            try: 
                with db_connection() as (con, cur): 
                    cur.execute("SELECT rollNo FROM student WHERE rollNo=%s", (r,)) 
                    if cur.fetchone(): 
                        messagebox.showerror("Error", "Roll already exists") 
                        return 
                    cur.execute("INSERT INTO student (rollNo, name, fname) VALUES (%s, %s, %s)", (r, n, f)) 
                messagebox.showinfo("Success", "Student added") 
                roll.delete(0, "end"); name.delete(0, "end"); fname.delete(0, "end") 
                self.show_dashboard() 
            except Exception as e: 
                messagebox.showerror("DB Error", str(e)) 

        tk.Button(frm, text="Add Student", bg="#44bd32", fg="white", command=action).grid(row=4, column=0, columnspan=2, pady=8) 

    # ------------------------- 
    # Remove Student (admin & teacher) 
    # ------------------------- 
    def show_remove_student(self): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text="Remove Student", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 
        tk.Label(frm, text="Roll No", bg="#f5f6fa").pack(anchor="w", pady=(6,2)) 
        roll = tk.Entry(frm) 
        roll.pack(anchor="w") 

        def action(): 
            r = roll.get().strip() 
            if not r: 
                messagebox.showerror("Error", "Enter roll") 
                return 
            if not messagebox.askyesno("Confirm", f"Delete student {r} and their enrollments?"): 
                return 
            try: 
                with db_connection() as (con, cur): 
                    cur.execute("DELETE FROM student WHERE rollNo=%s", (r,)) 
                    if cur.rowcount == 0: 
                        messagebox.showinfo("Info", "Student not found") 
                        return 
                messagebox.showinfo("Success", "Student removed") 
                roll.delete(0, "end") 
                self.show_dashboard() 
            except Exception as e: 
                messagebox.showerror("DB Error", str(e)) 

        tk.Button(frm, text="Remove", bg="#e84118", fg="white", command=action).pack(pady=8) 

    # ------------------------- 
    # Add Course (admin) 
    # ------------------------- 
    def show_add_course(self): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text="Add Course", bg="#f5f6fa", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w") 
        tk.Label(frm, text="Course Name", bg="#f5f6fa").grid(row=1, column=0, sticky="e", pady=4) 
        cname = tk.Entry(frm, width=40) 
        cname.grid(row=1, column=1, sticky="w", pady=4) 
        tk.Label(frm, text="Teacher (optional)", bg="#f5f6fa").grid(row=2, column=0, sticky="e", pady=4) 
        tname = tk.Entry(frm) 
        tname.grid(row=2, column=1, sticky="w", pady=4) 

        def action(): 
            c = cname.get().strip() 
            t = tname.get().strip() or None 
            if not c: 
                messagebox.showerror("Error", "Course name required") 
                return 
            try: 
                with db_connection() as (con, cur): 
                    cur.execute("INSERT INTO courses (course_name, teacher) VALUES (%s, %s)", (c, t)) 
                messagebox.showinfo("Success", "Course added") 
                cname.delete(0, "end"); tname.delete(0, "end") 
                self.show_dashboard() 
            except pymysql.err.IntegrityError: 
                messagebox.showerror("Error", "Course already exists") 
            except Exception as e: 
                messagebox.showerror("DB Error", str(e)) 

        tk.Button(frm, text="Add Course", bg="#8c7ae6", fg="white", command=action).grid(row=3, column=0, columnspan=2, pady=8) 

    # ------------------------- 
    # Assign courses (admin) - step 1: choose student 
    # ------------------------- 
    def show_assign_start(self): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text="Assign Courses - Select Student", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 
        try: 
            with db_connection() as (con, cur): 
                cur.execute("SELECT rollNo FROM student ORDER BY rollNo") 
                students = [r["rollNo"] for r in cur.fetchall()] 
        except Exception as e: 
            messagebox.showerror("DB Error", str(e)) 
            return 

        cmb = ttk.Combobox(frm, values=students, state="readonly") 
        cmb.pack(anchor="w", pady=6) 

        def nxt(): 
            sel = cmb.get() 
            if not sel: 
                messagebox.showerror("Error", "Select student") 
                return 
            self.show_assign_for_student(sel) 

        tk.Button(frm, text="Next", bg="#44bd32", fg="white", command=nxt).pack(pady=4) 

    def show_assign_for_student(self, roll): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text=f"Assign Courses for {roll}", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 

        try: 
            with db_connection() as (con, cur): 
                cur.execute("SELECT course_id, course_name FROM courses ORDER BY course_name") 
                courses = cur.fetchall() 
                cur.execute("SELECT course_id FROM enrollments WHERE rollNo=%s", (roll,)) 
                enrolled = {r["course_id"] for r in cur.fetchall()} 
        except Exception as e: 
            messagebox.showerror("DB Error", str(e)) 
            return 

        vars_map = {} 
        for row in courses: 
            v = tk.IntVar(value=1 if row["course_id"] in enrolled else 0) 
            cb = tk.Checkbutton(frm, text=row["course_name"], variable=v, bg="#f5f6fa") 
            cb.pack(anchor="w") 
            vars_map[row["course_id"]] = v 

        def save(): 
            try: 
                with db_connection() as (con, cur): 
                    for cid, var in vars_map.items(): 
                        if var.get() == 1: 
                            cur.execute("INSERT IGNORE INTO enrollments (rollNo, course_id, grade) VALUES (%s, %s, NULL)", (roll, cid)) 
                        else: 
                            cur.execute("DELETE FROM enrollments WHERE rollNo=%s AND course_id=%s", (roll, cid)) 
                messagebox.showinfo("Success", "Assignments updated") 
                self.show_dashboard() 
            except Exception as e: 
                messagebox.showerror("DB Error", str(e)) 

        tk.Button(frm, text="Save Assignments", bg="#44bd32", fg="white", command=save).pack(pady=8) 

    # ------------------------- 
    # Update grades (admin & teacher) 
    # ------------------------- 
    def show_update_grades(self): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text="Update Grades - Select Student", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 

        try: 
            with db_connection() as (con, cur): 
                cur.execute("SELECT rollNo FROM student ORDER BY rollNo") 
                students = [r["rollNo"] for r in cur.fetchall()] 
        except Exception as e: 
            messagebox.showerror("DB Error", str(e)) 
            return 

        cmb = ttk.Combobox(frm, values=students, state="readonly") 
        cmb.pack(anchor="w", pady=6) 

        def nxt(): 
            s = cmb.get() 
            if not s: 
                messagebox.showerror("Error", "Select student") 
                return 
            self.show_grade_form(s) 

        tk.Button(frm, text="Next", bg="#44bd32", fg="white", command=nxt).pack(pady=4) 

    def show_grade_form(self, roll): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text=f"Update Grades for {roll}", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 

        try: 
            with db_connection() as (con, cur): 
                cur.execute(""" 
                    SELECT e.enroll_id, c.course_name, e.grade 
                    FROM enrollments e 
                    JOIN courses c ON e.course_id=c.course_id 
                    WHERE e.rollNo=%s 
                    ORDER BY c.course_name 
                """, (roll,)) 
                rows = cur.fetchall() 
        except Exception as e: 
            messagebox.showerror("DB Error", str(e)) 
            return 

        if not rows: 
            messagebox.showinfo("Info", "Student has no enrolled courses") 
            return 

        entry_map = {} 
        for r in rows: 
            container = tk.Frame(frm, bg="#f5f6fa") 
            container.pack(fill="x", anchor="w", pady=2) 
            tk.Label(container, text=r["course_name"], bg="#f5f6fa").pack(side="left", padx=(0,8)) 
            ent = tk.Entry(container, width=10) 
            ent.pack(side="left") 
            if r["grade"]: 
                ent.insert(0, r["grade"]) 
            entry_map[r["enroll_id"]] = ent 

        def save(): 
            try: 
                with db_connection() as (con, cur): 
                    for eid, ent in entry_map.items(): 
                        g = ent.get().strip() or None 
                        if g and len(g) > 10: 
                            messagebox.showerror("Error", "Grade too long") 
                            return 
                        cur.execute("UPDATE enrollments SET grade=%s WHERE enroll_id=%s", (g, eid)) 
                messagebox.showinfo("Success", "Grades updated") 
                self.show_dashboard() 
            except Exception as e: 
                messagebox.showerror("DB Error", str(e)) 

        tk.Button(frm, text="Save Grades", bg="#44bd32", fg="white", command=save).pack(pady=8) 

    # ------------------------- 
    # View courses & teachers (all roles) 
    # ------------------------- 
    def show_courses_teachers(self): 
        self.clear_controls() 
        self.clear_tree() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="both", padx=10, pady=8) 
        tk.Label(frm, text="Courses & Teachers", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 

        try: 
            with db_connection() as (con, cur): 
                cur.execute("SELECT course_name, teacher FROM courses ORDER BY course_name") 
                rows = cur.fetchall() 
        except Exception as e: 
            messagebox.showerror("DB Error", str(e)) 
            return 

        # Create a text widget to display courses and teachers 
        text_frame = tk.Frame(frm, bg="#f5f6fa") 
        text_frame.pack(fill="both", expand=True, pady=6) 
         
        text_widget = tk.Text(text_frame, width=80, height=12, wrap="word", font=("Helvetica", 10)) 
        text_widget.pack(side="left", fill="both", expand=True) 
         
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview) 
        scrollbar.pack(side="right", fill="y") 
        text_widget.configure(yscrollcommand=scrollbar.set) 
         
        text_widget.insert("1.0", "Course Name\t\tTeacher\n") 
        text_widget.insert("2.0", "-" * 60 + "\n") 
         
        for idx, r in enumerate(rows, start=3): 
            teacher = r['teacher'] if r['teacher'] else 'N/A' 
            text_widget.insert(f"{idx}.0", f"{r['course_name']}\t\t{teacher}\n") 
         
        text_widget.config(state="disabled") 

    # ------------------------- 
    # Manage teachers (admin only) 
    # ------------------------- 
    def show_manage_teachers(self): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="both", padx=10, pady=8) 
        tk.Label(frm, text="Manage Teachers (Admin)", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 

        try: 
            with db_connection() as (con, cur): 
                cur.execute("SELECT course_id, course_name, teacher FROM courses ORDER BY course_name") 
                courses = cur.fetchall() 
        except Exception as e: 
            messagebox.showerror("DB Error", str(e)) 
            return 

        tk.Label(frm, text="Select Course", bg="#f5f6fa").pack(anchor="w") 
        course_map = {r["course_name"]: r for r in courses} 
        combo = ttk.Combobox(frm, values=list(course_map.keys()), state="readonly") 
        combo.pack(anchor="w", pady=4) 

        tk.Label(frm, text="Teacher Name (blank to remove)", bg="#f5f6fa").pack(anchor="w") 
        tentry = tk.Entry(frm) 
        tentry.pack(anchor="w", pady=4) 

        def load(): 
            sel = combo.get() 
            if not sel: 
                return 
            tentry.delete(0, "end") 
            tentry.insert(0, course_map[sel]["teacher"] or "") 

        def save(): 
            sel = combo.get() 
            if not sel: 
                messagebox.showerror("Error", "Select course") 
                return 
            name = tentry.get().strip() or None 
            try: 
                with db_connection() as (con, cur): 
                    cur.execute("UPDATE courses SET teacher=%s WHERE course_name=%s", (name, sel)) 
                    if cur.rowcount == 0: 
                        messagebox.showerror("Error", "Course not found") 
                        return 
                messagebox.showinfo("Success", "Teacher updated") 
                # reload view 
                self.show_manage_teachers() 
            except Exception as e: 
                messagebox.showerror("DB Error", str(e)) 

        tk.Button(frm, text="Load", command=load).pack(anchor="w", pady=(4,2)) 
        tk.Button(frm, text="Save", bg="#44bd32", fg="white", command=save).pack(anchor="w") 

    # ------------------------- 
    # Search student (all roles) 
    # ------------------------- 
    def show_search(self): 
        self.clear_controls() 
        frm = tk.Frame(self.controls_frame, bg="#f5f6fa") 
        frm.pack(fill="x", padx=10, pady=8) 
        tk.Label(frm, text="Search Student by Roll No", bg="#f5f6fa", font=("Helvetica", 14, "bold")).pack(anchor="w") 
        ent = tk.Entry(frm) 
        ent.pack(anchor="w", pady=6) 

        def do_search(): 
            r = ent.get().strip() 
            if not r: 
                messagebox.showerror("Error", "Enter roll") 
                return 
            self.clear_tree() 
            try: 
                with db_connection() as (con, cur): 
                    cur.execute("SELECT rollNo, name, fname FROM student WHERE rollNo=%s", (r,)) 
                    s = cur.fetchone() 
                    if not s: 
                        messagebox.showinfo("Info", "Student not found") 
                        return 
                    cur.execute("SELECT c.course_name, e.grade FROM enrollments e JOIN courses c ON e.course_id=c.course_id WHERE e.rollNo=%s", (r,)) 
                    rows = cur.fetchall() 
            except Exception as e: 
                messagebox.showerror("DB Error", str(e)) 
                return 
            
            if rows:
                courses = "\n".join([f"{row['course_name']} - Grade: {row['grade'] if row['grade'] else 'N/A'}" for row in rows])
            else:
                courses = "No courses enrolled"
            
            self.tree.insert("", "end", values=(s["rollNo"], s["name"], s["fname"], courses)) 

        tk.Button(frm, text="Search", bg="#44bd32", fg="white", command=do_search).pack(pady=6) 

    # ------------------------- 
    # Helper: clear controls area 
    # ------------------------- 
    def clear_controls(self): 
        for w in self.controls_frame.winfo_children(): 
            w.destroy() 

# ------------------------- 
# Entry point 
# ------------------------- 
if __name__ == "__main__": 
    print("=" * 50)
    print("Student Management System - Starting...")
    print("=" * 50)
    
    try: 
        if init_db():
            print("\n✓ Application starting...")
            root = tk.Tk() 
            app = StudentProApp(root) 
            root.mainloop()
        else:
            print("\n✗ Application failed to start!")
            print("\nPlease fix the database connection issue.")
            print("Common solutions:")
            print("1. Start MySQL server (XAMPP/WAMP)")
            print("2. Check if password is required")
            print("3. Install pymysql: pip install pymysql")
            input("\nPress Enter to exit...")
            
    except Exception as e: 
        print(f"\n✗ Fatal Error: {e}")
        input("Press Enter to exit...")