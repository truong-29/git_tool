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
        self.root.after(0, lambda: messagebox.showerror("Lỗi", message))

    def success(self, message):
        self.log(f"SUCCESS: {message}")
        self.root.after(0, lambda: messagebox.showinfo("Thành công", message))

    def warning(self, message):
        self.log(f"WARNING: {message}")
        self.root.after(0, lambda: messagebox.showwarning("Cảnh báo", message))

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

class GitGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Assistant - Hỗ trợ Git cho người mới")
        self.root.geometry("800x600")

        # Style
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))

        # Header
        header_frame = ttk.Frame(root, padding=10)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Git Assistant Tools", style="Header.TLabel").pack(side=tk.LEFT)

        # Main Content
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar (Buttons)
        btn_frame = ttk.LabelFrame(main_frame, text="Chức năng", padding=10)
        btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        buttons = [
            ("Đẩy code (Push)", self.run_push),
            ("Kéo code (Pull)", self.run_pull),
            ("Đồng bộ an toàn (Sync Main)", self.run_sync),
            ("Tạo tính năng mới (Feature)", self.run_feature),
            ("Xem trạng thái (Status)", self.run_status),
            ("Quản lý Stash (Fix Lost Code)", self.run_stash),
        ]

        for text, command in buttons:
            btn = ttk.Button(btn_frame, text=text, command=lambda c=command: self.run_thread(c), width=30)
            btn.pack(pady=5, fill=tk.X)
        
        ttk.Separator(btn_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Button(btn_frame, text="Thoát", command=root.quit).pack(side=tk.BOTTOM, fill=tk.X)

        # Right Area (Log)
        log_frame = ttk.LabelFrame(main_frame, text="Nhật ký hoạt động (Logs)", padding=10)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Initialize Logic
        self.io = GuiIO(self.log_text, self.root)
        self.scenarios = GitScenarios(io_handler=self.io)
        
        # Initial info
        self.io.log(f"Thư mục làm việc: {self.scenarios.git.working_dir}")
        self.io.log("Sẵn sàng.")

    def run_thread(self, target_func):
        """Run tasks in a separate thread to keep UI responsive"""
        thread = threading.Thread(target=target_func)
        thread.daemon = True
        thread.start()

    def run_push(self):
        self.scenarios.workflow_push_code()

    def run_pull(self):
        self.scenarios.workflow_pull_code()

    def run_sync(self):
        self.scenarios.workflow_sync_main()

    def run_feature(self):
        self.scenarios.workflow_new_feature()

    def run_status(self):
        self.io.log("=== STATUS ===")
        ok, out = self.scenarios.git.status()
        self.io.log(out)

    def run_stash(self):
        self.scenarios.workflow_fix_conflict_stash()
