import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="language_center",
            user="postgres",
            password="123456",
            host="localhost"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"Error connecting to database: {e}")
        return None

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Đăng nhập")
        self.root.geometry("300x150")
        
        # Username
        tk.Label(self.root, text="Tên đăng nhập:").pack(pady=5)
        self.username = tk.Entry(self.root)
        self.username.pack(pady=5)
        # Password
        tk.Label(self.root, text="Mật khẩu:").pack(pady=5)
        self.password = tk.Entry(self.root, show="*")
        self.password.pack(pady=5)  
        # Login button
        tk.Button(self.root, text="Đăng nhập", command=self.login).pack(pady=10)
        self.conn = connect_to_db()
        self.cur = self.conn.cursor() if self.conn else None

    def login(self):
        if self.cur:
            try:
                self.cur.execute("""
                    SELECT * FROM users 
                    WHERE username = %s AND password = %s
                """, (self.username.get(), self.password.get()))
                
                if self.cur.fetchone():
                    self.root.destroy()
                    root = tk.Tk()
                    app = LanguageCenterApp(root)
                    root.mainloop()
                else:
                    messagebox.showerror("Error", "Sai tên đăng nhập hoặc mật khẩu!")
            except Exception as e:
                messagebox.showerror("Error", f"Lỗi đăng nhập: {e}")

class LanguageCenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý trung tâm ngoại ngữ")
        self.root.geometry("800x600")

        self.conn = connect_to_db()
        self.cur = self.conn.cursor() if self.conn else None

        # Tạo các tab quản lý
        tab_control = ttk.Notebook(self.root)

        # Tab Quản lý Học viên
        self.student_tab = ttk.Frame(tab_control)
        tab_control.add(self.student_tab, text="Quản lý Học viên")
        self.create_student_tab()

        # Tab Quản lý Giảng viên
        self.teacher_tab = ttk.Frame(tab_control)
        tab_control.add(self.teacher_tab, text="Quản lý Giảng viên")
        self.create_teacher_tab()

        # Tab Quản lý Lớp học
        self.class_tab = ttk.Frame(tab_control)
        tab_control.add(self.class_tab, text="Quản lý Lớp học")
        self.create_class_tab()

        # Tab Thống kê
        self.stats_tab = ttk.Frame(tab_control)
        tab_control.add(self.stats_tab, text="Thống kê")
        self.create_stats_tab()

        tab_control.pack(expand=1, fill="both")

        # Load dữ liệu ban đầu
        self.load_students()
        self.load_teachers()
        self.load_classes()

    def create_search_frame(self, parent, table, load_func, search_columns):
        search_frame = ttk.Frame(parent)
        search_frame.pack(pady=5)

        ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, padx=5)

        search_by = ttk.Combobox(search_frame, values=search_columns)
        search_by.set(search_columns[0])
        search_by.pack(side=tk.LEFT, padx=5)

        def search():
            search_term = search_entry.get()
            column = search_by.get()
            
            for item in table.get_children():
                table.delete(item)

            if search_term:
                query = f"SELECT * FROM {table._name} WHERE LOWER({column}) LIKE LOWER(%s)"
                self.cur.execute(query, (f'%{search_term}%',))
            else:
                load_func()
                return

            for row in self.cur.fetchall():
                table.insert("", "end", values=row)

        ttk.Button(search_frame, text="Tìm", command=search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Đặt lại", command=load_func).pack(side=tk.LEFT, padx=5)

    def create_student_tab(self):
        label = ttk.Label(self.student_tab, text="Danh sách Học viên", font=("Arial", 16))
        label.pack(pady=10)

        # Thêm khung tìm kiếm
        columns = ("ID", "Họ", "Tên", "Email", "Điện thoại")
        search_columns = ["first_name", "last_name", "email", "phone"]
        
        self.student_table = ttk.Treeview(self.student_tab, columns=columns, show='headings')
        self.student_table._name = "Students"  # Thêm tên bảng cho tìm kiếm
        
        for col in columns:
            self.student_table.heading(col, text=col)
            self.student_table.column(col, minwidth=0, width=100)
            
        self.create_search_frame(self.student_tab, self.student_table, self.load_students, search_columns)
        self.student_table.pack(pady=10)

        add_button = ttk.Button(self.student_tab, text="Thêm học viên", command=self.add_student)
        add_button.pack(pady=10)

    def create_teacher_tab(self):
        label = ttk.Label(self.teacher_tab, text="Danh sách Giảng viên", font=("Arial", 16))
        label.pack(pady=10)

        columns = ("ID", "Họ", "Tên", "Email", "Điện thoại")
        search_columns = ["first_name", "last_name", "email", "phone"]
        
        self.teacher_table = ttk.Treeview(self.teacher_tab, columns=columns, show='headings')
        self.teacher_table._name = "Teachers"
        
        for col in columns:
            self.teacher_table.heading(col, text=col)
            self.teacher_table.column(col, minwidth=0, width=100)
            
        self.create_search_frame(self.teacher_tab, self.teacher_table, self.load_teachers, search_columns)
        self.teacher_table.pack(pady=10)

        add_button = ttk.Button(self.teacher_tab, text="Thêm giảng viên", command=self.add_teacher)
        add_button.pack(pady=10)

    def create_class_tab(self):
        label = ttk.Label(self.class_tab, text="Quản lý Lớp học", font=("Arial", 16))
        label.pack(pady=10)

        columns = ("ID", "Tên lớp", "Giảng viên ID", "Lịch học", "Phòng")
        search_columns = ["class_name", "teacher_id", "schedule", "room"]
        
        self.class_table = ttk.Treeview(self.class_tab, columns=columns, show='headings')
        self.class_table._name = "Classes"
        
        for col in columns:
            self.class_table.heading(col, text=col)
            self.class_table.column(col, minwidth=0, width=100)
            
        self.create_search_frame(self.class_tab, self.class_table, self.load_classes, search_columns)
        self.class_table.pack(pady=10)

        add_button = ttk.Button(self.class_tab, text="Thêm lớp học", command=self.add_class)
        add_button.pack(pady=10)

    def load_students(self):
        for row in self.student_table.get_children():
            self.student_table.delete(row)
        self.cur.execute("SELECT * FROM Students")
        for row in self.cur.fetchall():
            self.student_table.insert("", "end", values=row)

    def load_teachers(self):
        for row in self.teacher_table.get_children():
            self.teacher_table.delete(row)
        self.cur.execute("SELECT * FROM Teachers")
        for row in self.cur.fetchall():
            self.teacher_table.insert("", "end", values=row)

    def load_classes(self):
        for row in self.class_table.get_children():
            self.class_table.delete(row)
        self.cur.execute("SELECT * FROM Classes")
        for row in self.cur.fetchall():
            self.class_table.insert("", "end", values=row)


    def add_student(self):
        # Hiển thị form để nhập thông tin học viên
        top = tk.Toplevel(self.root)
        top.title("Thêm học viên")

        tk.Label(top, text="Họ").grid(row=0, column=0)
        first_name = tk.Entry(top)
        first_name.grid(row=0, column=1)

        tk.Label(top, text="Tên").grid(row=1, column=0)
        last_name = tk.Entry(top)
        last_name.grid(row=1, column=1)

        tk.Label(top, text="Email").grid(row=2, column=0)
        email = tk.Entry(top)
        email.grid(row=2, column=1)

        tk.Label(top, text="Điện thoại").grid(row=3, column=0)
        phone = tk.Entry(top)
        phone.grid(row=3, column=1)

        def save_student():
            try:
                self.cur.execute("""INSERT INTO Students (first_name, last_name, email, phone)
                                    VALUES (%s, %s, %s, %s)""",
                                  (first_name.get(), last_name.get(), email.get(), phone.get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Thêm học viên thành công")
                self.load_students()  # Làm mới bảng học viên
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Lỗi khi thêm học viên: {e}")

        tk.Button(top, text="Lưu", command=save_student).grid(row=4, column=0, columnspan=2)

    def add_teacher(self):
        # Hiển thị form để nhập thông tin giảng viên
        top = tk.Toplevel(self.root)
        top.title("Thêm giảng viên")

        tk.Label(top, text="Họ").grid(row=0, column=0)
        first_name = tk.Entry(top)
        first_name.grid(row=0, column=1)

        tk.Label(top, text="Tên").grid(row=1, column=0)
        last_name = tk.Entry(top)
        last_name.grid(row=1, column=1)

        tk.Label(top, text="Email").grid(row=2, column=0)
        email = tk.Entry(top)
        email.grid(row=2, column=1)

        tk.Label(top, text="Điện thoại").grid(row=3, column=0)
        phone = tk.Entry(top)
        phone.grid(row=3, column=1)

        def save_teacher():
            try:
                self.cur.execute("""INSERT INTO Teachers (first_name, last_name, email, phone)
                                    VALUES (%s, %s, %s, %s)""",
                                  (first_name.get(), last_name.get(), email.get(), phone.get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Thêm giảng viên thành công")
                self.load_teachers()  # Làm mới bảng giảng viên
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Lỗi khi thêm giảng viên: {e}")

        tk.Button(top, text="Lưu", command=save_teacher).grid(row=4, column=0, columnspan=2)

    def add_class(self):
        # Hiển thị form để nhập thông tin lớp học
        top = tk.Toplevel(self.root)
        top.title("Thêm lớp học")

        tk.Label(top, text="Tên lớp").grid(row=0, column=0)
        self.class_name_entry = tk.Entry(top)
        self.class_name_entry.grid(row=0, column=1)

        tk.Label(top, text="Giảng viên ID").grid(row=1, column=0)
        self.teacher_id_entry = tk.Entry(top)
        self.teacher_id_entry.grid(row=1, column=1)

        tk.Label(top, text="Lịch học").grid(row=2, column=0)
        self.schedule_entry = tk.Entry(top)
        self.schedule_entry.grid(row=2, column=1)

        tk.Label(top, text="Phòng").grid(row=3, column=0)
        self.room_entry = tk.Entry(top)
        self.room_entry.grid(row=3, column=1)

        def save_class():
            try:
                self.cur.execute("""INSERT INTO Classes (class_name, teacher_id, schedule, room)
                                    VALUES (%s, %s, %s, %s)""",
                                  (self.class_name_entry.get(), self.teacher_id_entry.get(),
                                   self.schedule_entry.get(), self.room_entry.get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Thêm lớp học thành công")
                self.load_classes()  # Làm mới bảng lớp học
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Lỗi khi thêm lớp học: {e}")

        tk.Button(top, text="Lưu", command=save_class).grid(row=4, column=0, columnspan=2)

    def create_stats_tab(self):
        label = ttk.Label(self.stats_tab, text="Thống kê", font=("Arial", 16))
        label.pack(pady=10)

        # Thêm các thống kê vào đây
        self.stats_text = tk.Text(self.stats_tab, height=15, width=50)
        self.stats_text.pack(pady=10)

        self.load_statistics()

    def load_statistics(self):
        # Làm mới thông tin thống kê
        self.stats_text.delete(1.0, tk.END)
        self.cur.execute("SELECT COUNT(*) FROM Students")
        total_students = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM Teachers")
        total_teachers = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM Classes")
        total_classes = self.cur.fetchone()[0]

        statistics = f"Tổng số học viên: {total_students}\n" \
                     f"Tổng số giảng viên: {total_teachers}\n" \
                     f"Tổng số lớp học: {total_classes}\n"

        self.stats_text.insert(tk.END, statistics)

    def __del__(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    login = LoginWindow()
    login.root.mainloop()
    def __del__(self):
        if self.conn:
            self.conn.close()
