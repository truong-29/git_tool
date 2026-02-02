import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import threading
from .io_handler import IOHandler
from .scenarios import GitScenarios

class GuiIO(IOHandler):
    def __init__(self, log_widget, root):
        self.log_widget = log_widget
        self.root = root

    def log(self, message, color=None):
        def _update():
            self.log_widget.configure(state='normal')
            self.log_widget.insert(tk.END, f"{message}\n")
            if color:
                # Apply tag if needed (not implemented simple here)
                pass
            self.log_widget.see(tk.END)
            self.log_widget.configure(state='disabled')
        self.root.after(0, _update)

    def error(self, message):
        self.log(f"ERROR: {message}")
        self.root.after(0, lambda: messagebox.showerror("Lỗi", message, parent=self.root))

    def success(self, message):
        self.log(f"SUCCESS: {message}")
        self.root.after(0, lambda: messagebox.showinfo("Thành công", message, parent=self.root))

    def warning(self, message):
        self.log(f"WARNING: {message}")
        self.root.after(0, lambda: messagebox.showwarning("Cảnh báo", message, parent=self.root))

    def input(self, prompt):
        # Use a threading event/queue to get result from main thread
        result = [None]
        event = threading.Event()
        
        def _ask():
            result[0] = simpledialog.askstring("Nhập thông tin", prompt, parent=self.root)
            event.set()
            
        self.root.after(0, _ask)
        event.wait() # Block thread until user inputs
        return result[0]

    def confirm(self, prompt):
        result = [False]
        event = threading.Event()
        
        def _ask():
            result[0] = messagebox.askyesno("Xác nhận", prompt, parent=self.root)
            event.set()
            
        self.root.after(0, _ask)
        event.wait()
        return result[0]

class TaskWindow(tk.Toplevel):
    def __init__(self, parent, title, task_func):
        super().__init__(parent)
        self.title(title)
        self.geometry("700x500")
        
        # Header
        ttk.Label(self, text=title, font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        # Log Area
        log_frame = ttk.LabelFrame(self, text="Tiến trình", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar / Close Button
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(btn_frame, text="Đóng", command=self.destroy).pack(side=tk.RIGHT)

        # Initialize Logic for this window
        self.io = GuiIO(self.log_text, self)
        self.scenarios = GitScenarios(io_handler=self.io)
        self.task_func = task_func
        
        # Auto start task
        self.start_task()

    def start_task(self):
        thread = threading.Thread(target=self.run_scenario)
        thread.daemon = True
        thread.start()

    def run_scenario(self):
        # Execute the passed task function with the local scenarios instance
        try:
            self.task_func(self.scenarios)
            self.io.log("=== HOÀN TẤT ===")
        except Exception as e:
            self.io.error(f"Lỗi không mong muốn: {e}")

class GitGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Assistant - Hỗ trợ Git cho người mới")
        self.root.geometry("600x400") # Main dashboard smaller now

        # Style
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))

        # Header
        header_frame = ttk.Frame(root, padding=20)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Git Assistant Dashboard", style="Header.TLabel").pack()
        ttk.Label(header_frame, text="Chọn tác vụ bạn muốn thực hiện:", font=('Helvetica', 10)).pack(pady=5)

        # Main Content (Buttons Grid)
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        buttons = [
            ("Đẩy code (Push)", self.open_push),
            ("Kéo code (Pull)", self.open_pull),
            ("Đồng bộ an toàn (Sync Main)", self.open_sync),
            ("Tạo tính năng mới (Feature)", self.open_feature),
            ("Xem trạng thái (Status)", self.open_status),
            ("Quản lý Stash (Fix Lost Code)", self.open_stash),
        ]

        # Create 2 columns grid
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(main_frame, text=text, command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Footer
        footer_frame = ttk.Frame(root, padding=10)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(footer_frame, text="Thoát", command=root.quit).pack(side=tk.RIGHT)

    def open_push(self):
        TaskWindow(self.root, "Đẩy code lên Server (Push)", lambda s: s.workflow_push_code())

    def open_pull(self):
        TaskWindow(self.root, "Kéo code về (Pull)", lambda s: s.workflow_pull_code())

    def open_sync(self):
        TaskWindow(self.root, "Đồng bộ an toàn từ Main", lambda s: s.workflow_sync_main())

    def open_feature(self):
        TaskWindow(self.root, "Tạo tính năng mới", lambda s: s.workflow_new_feature())

    def open_status(self):
        def show_status(s):
            s.io.log("=== STATUS ===")
            ok, out = s.git.status()
            s.io.log(out)
        TaskWindow(self.root, "Trạng thái (Status)", show_status)

    def open_stash(self):
        TaskWindow(self.root, "Quản lý Stash", lambda s: s.workflow_fix_conflict_stash())
