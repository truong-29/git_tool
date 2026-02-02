# -*- coding: utf-8 -*-
"""
Gitea Tool - Ung dung GUI ho tro cac lenh Gitea voi Access Token
Ho tro Gitea self-hosted (git.icomm.vn)
Author: Kiro Assistant
Version: 2.0.0

Yeu cau cai dat:
    pip install requests

Cach su dung:
    python github_tool.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import json
import webbrowser
from datetime import datetime
import os
import subprocess
import urllib.parse
import threading

# ============== CAU HINH MAC DINH ==============
DEFAULT_GITEA_URL = "https://git.icomm.vn"

# ============== CAU HINH LENH GITEA API ==============
GITEA_API_COMMANDS = {
    "repos": {
        "name": "Danh sach Repositories",
        "description": "Lay danh sach tat ca repositories cua ban",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/user/repos",
        "method": "GET",
        "params": {"limit": 50},
        "guide": "Hien thi tat ca repos ban so huu. Quyen can: Token voi quyen repo hoac All."
    },
    "user_info": {
        "name": "Thong tin User",
        "description": "Xem thong tin tai khoan Gitea cua ban",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/user",
        "method": "GET",
        "params": {},
        "guide": "Hien thi thong tin tai khoan Gitea. Dung de kiem tra token co hop le khong."
    },
    "list_branches": {
        "name": "Danh sach Branches (API)",
        "description": "Xem tat ca branches cua mot repository",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/repos/{owner}/{repo}/branches",
        "method": "GET",
        "params": {},
        "requires_input": ["owner", "repo_name"],
        "guide": "Liet ke tat ca branches trong repo. Tham so: Owner, Ten repo."
    },
    "list_commits": {
        "name": "Lich su Commits (API)",
        "description": "Xem lich su commits cua repository",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/repos/{owner}/{repo}/commits",
        "method": "GET",
        "params": {"limit": 30},
        "requires_input": ["owner", "repo_name"],
        "guide": "Xem 30 commits gan nhat. Tham so: Owner, Ten repo."
    },
    "repo_info": {
        "name": "Thong tin Repository",
        "description": "Xem chi tiet mot repository (bao gom clone URLs)",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/repos/{owner}/{repo}",
        "method": "GET",
        "params": {},
        "requires_input": ["owner", "repo_name"],
        "guide": "Xem chi tiet repo + Clone URLs. Tham so: Owner, Ten repo."
    },
    "list_orgs": {
        "name": "Danh sach Organizations",
        "description": "Xem tat ca organizations ban la thanh vien",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/user/orgs",
        "method": "GET",
        "params": {},
        "guide": "Liet ke tat ca orgs ban thuoc ve."
    },
    "org_repos": {
        "name": "Repos cua Organization",
        "description": "Xem tat ca repos trong mot organization",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/orgs/{org}/repos",
        "method": "GET",
        "params": {"limit": 100},
        "requires_input": ["org_name"],
        "guide": "Liet ke repos trong org. Tham so: Ten Org (VD: erp)"
    },
    "search_repos": {
        "name": "Tim kiem Repositories",
        "description": "Tim kiem repos theo tu khoa",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc du lieu",
        "endpoint": "/api/v1/repos/search",
        "method": "GET",
        "params": {"limit": 50},
        "requires_input": ["search_query"],
        "guide": "Tim repos theo tu khoa. Tham so: Tu khoa tim kiem."
    },
}

# ============== CAU HINH LENH GIT CLI ==============
GIT_CLI_COMMANDS = {
    "git_config_token": {
        "name": "Cau hinh Git voi Token",
        "description": "Luu token vao Git credential de khong can nhap mat khau",
        "danger_level": "warning",
        "danger_note": "Luu token vao may local",
        "command_type": "config",
        "guide": "Luu token de Git tu dong xac thuc. Lenh: git config --global credential.helper store"
    },
    "git_clone": {
        "name": "Clone Repository",
        "description": "Clone repo ve may local voi token xac thuc",
        "danger_level": "safe",
        "danger_note": "An toan - Tai code ve may",
        "command_type": "clone",
        "requires_input": ["owner", "repo_name", "local_path"],
        "guide": "Clone repo ve thu muc local. Tham so: Owner, Ten repo, Thu muc luu."
    },
    "git_pull": {
        "name": "Pull Code moi nhat",
        "description": "Lay code moi nhat tu remote ve local",
        "danger_level": "safe",
        "danger_note": "An toan - Cap nhat code",
        "command_type": "pull",
        "requires_input": ["local_path"],
        "guide": "Lay code moi nhat tu remote. Lenh: git pull origin <branch>"
    },
    "git_fetch": {
        "name": "Fetch tu Remote",
        "description": "Lay thong tin moi tu remote (khong merge)",
        "danger_level": "safe",
        "danger_note": "An toan - Chi lay thong tin",
        "command_type": "fetch",
        "requires_input": ["local_path"],
        "guide": "Lay thong tin branches/commits moi. Lenh: git fetch --all"
    },
    "git_status": {
        "name": "Git Status",
        "description": "Xem trang thai thay doi trong repo local",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc",
        "command_type": "status",
        "requires_input": ["local_path"],
        "guide": "Xem files da thay doi. Lenh: git status"
    },
    "git_branch_list": {
        "name": "Danh sach Branches (Local)",
        "description": "Xem tat ca branches trong repo local",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc",
        "command_type": "branch_list",
        "requires_input": ["local_path"],
        "guide": "Liet ke branches local + remote. Lenh: git branch -a"
    },
    "git_checkout": {
        "name": "Chuyen Branch",
        "description": "Chuyen sang branch khac",
        "danger_level": "warning",
        "danger_note": "Can than - Chuyen branch",
        "command_type": "checkout",
        "requires_input": ["local_path", "branch_name"],
        "guide": "Chuyen sang branch khac. Lenh: git checkout <branch_name>"
    },
    "git_checkout_new": {
        "name": "Tao va Chuyen Branch moi",
        "description": "Tao branch moi va chuyen sang do",
        "danger_level": "warning",
        "danger_note": "Tao branch moi",
        "command_type": "checkout_new",
        "requires_input": ["local_path", "branch_name"],
        "guide": "Tao branch moi tu branch hien tai. Lenh: git checkout -b <new_branch>"
    },
    "git_add_all": {
        "name": "Add tat ca thay doi",
        "description": "Stage tat ca files da thay doi",
        "danger_level": "safe",
        "danger_note": "An toan - Chuan bi commit",
        "command_type": "add",
        "requires_input": ["local_path"],
        "guide": "Stage tat ca files de commit. Lenh: git add -A"
    },
    "git_commit": {
        "name": "Commit thay doi",
        "description": "Commit cac thay doi da stage",
        "danger_level": "warning",
        "danger_note": "Tao commit moi",
        "command_type": "commit",
        "requires_input": ["local_path", "commit_message"],
        "guide": "Luu thay doi vao lich su Git. Lenh: git commit -m <message>"
    },
    "git_push": {
        "name": "Push len Remote",
        "description": "Day commits len remote repository",
        "danger_level": "warning",
        "danger_note": "Day code len server",
        "command_type": "push",
        "requires_input": ["local_path"],
        "guide": "Day commits local len remote. Lenh: git push origin <branch>"
    },
    "git_push_new_branch": {
        "name": "Push Branch moi len Remote",
        "description": "Day branch moi len remote va set upstream",
        "danger_level": "warning",
        "danger_note": "Tao branch moi tren server",
        "command_type": "push_new",
        "requires_input": ["local_path", "branch_name"],
        "guide": "Day branch moi len remote. Lenh: git push -u origin <branch>"
    },
    "git_log": {
        "name": "Xem lich su Commits (Local)",
        "description": "Xem lich su commits trong repo local",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc",
        "command_type": "log",
        "requires_input": ["local_path"],
        "guide": "Xem 20 commits gan nhat. Lenh: git log --oneline -20"
    },
    "git_stash": {
        "name": "Stash thay doi",
        "description": "Luu tam thay doi chua commit",
        "danger_level": "safe",
        "danger_note": "An toan - Luu tam",
        "command_type": "stash",
        "requires_input": ["local_path"],
        "guide": "Luu tam thay doi de chuyen branch. Lenh: git stash"
    },
    "git_stash_pop": {
        "name": "Khoi phuc Stash",
        "description": "Khoi phuc thay doi da stash",
        "danger_level": "safe",
        "danger_note": "An toan - Khoi phuc",
        "command_type": "stash_pop",
        "requires_input": ["local_path"],
        "guide": "Khoi phuc thay doi da stash. Lenh: git stash pop"
    },
    "git_reset_hard": {
        "name": "Reset ve commit gan nhat",
        "description": "Huy tat ca thay doi chua commit",
        "danger_level": "danger",
        "danger_note": "NGUY HIEM - Mat thay doi!",
        "command_type": "reset_hard",
        "requires_input": ["local_path"],
        "guide": "Huy TAT CA thay doi chua commit. KHONG THE KHOI PHUC!"
    },
    "git_merge": {
        "name": "Merge Branch",
        "description": "Merge branch khac vao branch hien tai",
        "danger_level": "warning",
        "danger_note": "Merge code",
        "command_type": "merge",
        "requires_input": ["local_path", "branch_name"],
        "guide": "Merge branch khac vao branch hien tai. Lenh: git merge <branch>"
    },
    "git_diff": {
        "name": "Xem thay doi (Diff)",
        "description": "Xem chi tiet cac thay doi chua commit",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc",
        "command_type": "diff",
        "requires_input": ["local_path"],
        "guide": "Xem chi tiet thay doi. Lenh: git diff"
    },
    "git_remote_info": {
        "name": "Thong tin Remote",
        "description": "Xem thong tin remote repository",
        "danger_level": "safe",
        "danger_note": "An toan - Chi doc",
        "command_type": "remote",
        "requires_input": ["local_path"],
        "guide": "Xem URL remote. Lenh: git remote -v"
    },
    "git_set_remote": {
        "name": "Cau hinh Remote URL",
        "description": "Thay doi URL remote voi token",
        "danger_level": "warning",
        "danger_note": "Thay doi cau hinh",
        "command_type": "set_remote",
        "requires_input": ["local_path", "owner", "repo_name"],
        "guide": "Cap nhat remote URL voi token. Dung khi clone bang HTTPS nhung chua co token."
    },
}


# ============== LOP CHINH ==============
class GiteaToolApp:
    """Ung dung GUI quan ly Gitea voi Access Token"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gitea Tool v2.0 - Quan ly Git nhanh chong (git.icomm.vn)")
        self.root.geometry("1350x900")
        self.root.minsize(1200, 800)
        
        self.gitea_url = tk.StringVar(value=DEFAULT_GITEA_URL)
        self.access_token = tk.StringVar()
        self.selected_command = tk.StringVar()
        self.current_user = None
        self.command_type = tk.StringVar(value="api")
        
        self._create_styles()
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
        self._load_saved_config()
    
    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Safe.TLabel', foreground='#1b5e20', font=('Segoe UI', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='#e65100', font=('Segoe UI', 10, 'bold'))
        style.configure('Danger.TLabel', foreground='#b71c1c', font=('Segoe UI', 10, 'bold'))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Exec.TButton', font=('Segoe UI', 10, 'bold'))
    
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Luu cau hinh", command=self._save_config)
        file_menu.add_command(label="Xoa cau hinh da luu", command=self._clear_saved_config)
        file_menu.add_separator()
        file_menu.add_command(label="Xuat ket qua", command=self._export_result)
        file_menu.add_separator()
        file_menu.add_command(label="Thoat", command=self.root.quit)
        
        git_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Git", menu=git_menu)
        git_menu.add_command(label="Chon thu muc repo", command=self._browse_local_path)
        git_menu.add_command(label="Mo terminal tai thu muc", command=self._open_terminal)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tro giup", menu=help_menu)
        help_menu.add_command(label="Huong dan tao Token", command=self._show_token_guide)
        help_menu.add_command(label="Mo Gitea Settings", 
                              command=lambda: webbrowser.open(f"{self.gitea_url.get()}/user/settings/applications"))
        help_menu.add_separator()
        help_menu.add_command(label="Ve ung dung", command=self._show_about)
    
    def _create_main_layout(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # PHAN TREN: Gitea URL va Token
        top_frame = ttk.LabelFrame(main_frame, text="KET NOI GITEA (git.icomm.vn)", padding="10")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        url_frame = ttk.Frame(top_frame)
        url_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(url_frame, text="Gitea URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, textvariable=self.gitea_url, width=40)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(url_frame, text="(VD: https://git.icomm.vn)", foreground='gray').pack(side=tk.LEFT)
        
        token_frame = ttk.Frame(top_frame)
        token_frame.pack(fill=tk.X)
        ttk.Label(token_frame, text="Access Token:").pack(side=tk.LEFT)
        self.token_entry = ttk.Entry(token_frame, textvariable=self.access_token, width=50, show="*")
        self.token_entry.pack(side=tk.LEFT, padx=5)
        
        self.show_token_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(token_frame, text="Hien", variable=self.show_token_var,
                        command=self._toggle_token_visibility).pack(side=tk.LEFT)
        ttk.Button(token_frame, text="Kiem tra ket noi", command=self._verify_token).pack(side=tk.LEFT, padx=5)
        ttk.Button(token_frame, text="Huong dan tao Token", command=self._show_token_guide).pack(side=tk.LEFT)
        
        self.user_info_label = ttk.Label(top_frame, text="Chua ket noi", style='Header.TLabel')
        self.user_info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # PHAN GIUA
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cot trai
        left_frame = ttk.Frame(middle_frame, width=420)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tab_frame = ttk.LabelFrame(left_frame, text="CHON LOAI LENH", padding="5")
        tab_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Radiobutton(tab_frame, text="API (Gitea)", variable=self.command_type, 
                        value="api", command=self._refresh_command_list).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(tab_frame, text="Git CLI (Local)", variable=self.command_type, 
                        value="cli", command=self._refresh_command_list).pack(side=tk.LEFT, padx=10)
        
        list_frame = ttk.LabelFrame(left_frame, text="DANH SACH LENH", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.command_listbox = tk.Listbox(list_frame, height=20, font=('Segoe UI', 10),
                                           selectmode=tk.SINGLE, activestyle='dotbox',
                                           selectbackground='#0078d4', selectforeground='white')
        self.command_listbox.pack(fill=tk.BOTH, expand=True)
        self.command_listbox.bind('<<ListboxSelect>>', self._on_command_select)
        
        legend_frame = ttk.Frame(list_frame)
        legend_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(legend_frame, text="[OK]=An toan", bg='#c8e6c9', fg='#1b5e20', 
                 font=('Segoe UI', 8), padx=3).pack(side=tk.LEFT, padx=2)
        tk.Label(legend_frame, text="[!!]=Can than", bg='#ffe082', fg='#e65100', 
                 font=('Segoe UI', 8), padx=3).pack(side=tk.LEFT, padx=2)
        tk.Label(legend_frame, text="[XX]=Nguy hiem", bg='#ef9a9a', fg='#b71c1c', 
                 font=('Segoe UI', 8), padx=3).pack(side=tk.LEFT, padx=2)
        
        # Cot phai
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        guide_frame = ttk.LabelFrame(right_frame, text="HUONG DAN", padding="10")
        guide_frame.pack(fill=tk.X, pady=(0, 10))
        self.guide_text = scrolledtext.ScrolledText(guide_frame, height=4, font=('Consolas', 10), wrap=tk.WORD)
        self.guide_text.pack(fill=tk.X)
        self.guide_text.insert(tk.END, "Chon mot lenh tu danh sach ben trai de xem huong dan")
        self.guide_text.config(state=tk.DISABLED)
        
        self.params_frame = ttk.LabelFrame(right_frame, text="THAM SO", padding="10")
        self.params_frame.pack(fill=tk.X, pady=(0, 10))
        self.param_widgets = {}
        self._create_param_inputs()
        
        exec_frame = ttk.Frame(right_frame)
        exec_frame.pack(fill=tk.X, pady=(0, 10))
        self.exec_button = ttk.Button(exec_frame, text=">>> THUC THI LENH <<<", 
                                       command=self._execute_command, state=tk.DISABLED,
                                       style='Exec.TButton')
        self.exec_button.pack(side=tk.LEFT)
        self.danger_label = ttk.Label(exec_frame, text="")
        self.danger_label.pack(side=tk.LEFT, padx=10)
        
        result_frame = ttk.LabelFrame(right_frame, text="KET QUA", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        self.result_text = scrolledtext.ScrolledText(result_frame, font=('Consolas', 9), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        self._refresh_command_list()

    def _create_param_inputs(self):
        ttk.Label(self.params_frame, text="Owner (user/org):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.param_widgets['owner'] = ttk.Entry(self.params_frame, width=25)
        self.param_widgets['owner'].grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.params_frame, text="Ten Repo:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(15, 0))
        self.param_widgets['repo_name'] = ttk.Entry(self.params_frame, width=25)
        self.param_widgets['repo_name'].grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(self.params_frame, text="Ten Org:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.param_widgets['org_name'] = ttk.Entry(self.params_frame, width=25)
        self.param_widgets['org_name'].grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(self.params_frame, text="Tu khoa tim:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(15, 0))
        self.param_widgets['search_query'] = ttk.Entry(self.params_frame, width=25)
        self.param_widgets['search_query'].grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(self.params_frame, text="Thu muc Local:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.param_widgets['local_path'] = ttk.Entry(self.params_frame, width=45)
        self.param_widgets['local_path'].grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky=tk.W)
        ttk.Button(self.params_frame, text="...", width=3, 
                   command=self._browse_local_path).grid(row=2, column=3, sticky=tk.W, pady=2)
        
        ttk.Label(self.params_frame, text="Ten Branch:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.param_widgets['branch_name'] = ttk.Entry(self.params_frame, width=25)
        self.param_widgets['branch_name'].grid(row=3, column=1, padx=5, pady=2)
        self.param_widgets['branch_name'].insert(0, "main")
        
        ttk.Label(self.params_frame, text="Commit Message:").grid(row=3, column=2, sticky=tk.W, pady=2, padx=(15, 0))
        self.param_widgets['commit_message'] = ttk.Entry(self.params_frame, width=25)
        self.param_widgets['commit_message'].grid(row=3, column=3, padx=5, pady=2)
    
    def _create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="San sang - Nhap token va kiem tra ket noi", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _refresh_command_list(self):
        self.command_listbox.delete(0, tk.END)
        commands = GITEA_API_COMMANDS if self.command_type.get() == "api" else GIT_CLI_COMMANDS
        
        for i, (cmd_key, cmd_info) in enumerate(commands.items()):
            danger_level = cmd_info["danger_level"]
            danger_prefix = {"safe": "[OK]", "warning": "[!!]", "danger": "[XX]"}[danger_level]
            self.command_listbox.insert(tk.END, f"  {danger_prefix}  {cmd_info['name']}")
            
            if danger_level == "safe":
                self.command_listbox.itemconfig(i, bg='#c8e6c9', fg='#1b5e20')
            elif danger_level == "warning":
                self.command_listbox.itemconfig(i, bg='#ffe082', fg='#e65100')
            else:
                self.command_listbox.itemconfig(i, bg='#ef9a9a', fg='#b71c1c')
    
    def _toggle_token_visibility(self):
        self.token_entry.config(show="" if self.show_token_var.get() else "*")
    
    def _browse_local_path(self):
        path = filedialog.askdirectory(title="Chon thu muc chua repo")
        if path:
            self.param_widgets['local_path'].delete(0, tk.END)
            self.param_widgets['local_path'].insert(0, path)
    
    def _open_terminal(self):
        path = self.param_widgets['local_path'].get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showwarning("Canh bao", "Vui long chon thu muc repo hop le!")
            return
        try:
            if os.name == 'nt':
                subprocess.Popen(f'start cmd /K cd /d "{path}"', shell=True)
            else:
                subprocess.Popen(['gnome-terminal', f'--working-directory={path}'])
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the mo terminal: {str(e)}")
    
    def _on_command_select(self, event):
        selection = self.command_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        commands = GITEA_API_COMMANDS if self.command_type.get() == "api" else GIT_CLI_COMMANDS
        cmd_key = list(commands.keys())[index]
        cmd_info = commands[cmd_key]
        
        self.selected_command.set(cmd_key)
        
        self.guide_text.config(state=tk.NORMAL)
        self.guide_text.delete(1.0, tk.END)
        self.guide_text.insert(tk.END, cmd_info['guide'])
        self.guide_text.config(state=tk.DISABLED)
        
        danger_level = cmd_info['danger_level']
        self.danger_label.config(text=cmd_info['danger_note'])
        style_map = {'safe': 'Safe.TLabel', 'warning': 'Warning.TLabel', 'danger': 'Danger.TLabel'}
        self.danger_label.config(style=style_map[danger_level])
        
        if self.command_type.get() == "cli" or self.access_token.get():
            self.exec_button.config(state=tk.NORMAL)
        
        self._update_status(f"Da chon: {cmd_info['name']}")

    def _verify_token(self):
        token = self.access_token.get().strip()
        gitea_url = self.gitea_url.get().strip().rstrip('/')
        
        if not token:
            messagebox.showwarning("Canh bao", "Vui long nhap Access Token!")
            return
        if not gitea_url:
            messagebox.showwarning("Canh bao", "Vui long nhap Gitea URL!")
            return
        
        self._update_status("Dang kiem tra ket noi...")
        headers = {"Authorization": f"token {token}", "Accept": "application/json"}
        
        try:
            response = requests.get(f"{gitea_url}/api/v1/user", headers=headers, timeout=15, verify=True)
            
            if response.status_code == 200:
                user_data = response.json()
                self.current_user = user_data
                self.param_widgets['owner'].delete(0, tk.END)
                self.param_widgets['owner'].insert(0, user_data['login'])
                self.user_info_label.config(text=f"Da ket noi: {user_data['login']} | Email: {user_data.get('email', 'N/A')}")
                self.exec_button.config(state=tk.NORMAL)
                self._update_status(f"Ket noi thanh cong - User: {user_data['login']}")
                messagebox.showinfo("Thanh cong", f"Ket noi thanh cong!\nUser: {user_data['login']}")
            elif response.status_code == 401:
                self.user_info_label.config(text="Token khong hop le")
                messagebox.showerror("Loi", "Token khong hop le hoac da het han!")
            else:
                messagebox.showerror("Loi", f"Loi API: {response.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Loi", f"Khong the ket noi den: {gitea_url}")
        except Exception as e:
            messagebox.showerror("Loi", f"Loi: {str(e)}")

    def _execute_command(self):
        cmd_key = self.selected_command.get()
        if not cmd_key:
            messagebox.showwarning("Canh bao", "Vui long chon mot lenh!")
            return
        
        if self.command_type.get() == "api":
            self._execute_api_command(cmd_key)
        else:
            self._execute_cli_command(cmd_key)
    
    def _execute_api_command(self, cmd_key):
        token = self.access_token.get().strip()
        if not token:
            messagebox.showwarning("Canh bao", "Vui long nhap Access Token!")
            return
        
        cmd_info = GITEA_API_COMMANDS[cmd_key]
        
        if cmd_info['danger_level'] == 'danger':
            if not messagebox.askyesno("CANH BAO", "Ban dang thuc hien lenh NGUY HIEM!\nTiep tuc?"):
                return
        elif cmd_info['danger_level'] == 'warning':
            if not messagebox.askyesno("Xac nhan", f"Tiep tuc thuc hien: {cmd_info['name']}?"):
                return
        
        self._update_status(f"Dang thuc thi: {cmd_info['name']}...")
        self._call_gitea_api(cmd_key, cmd_info, token)
    
    def _execute_cli_command(self, cmd_key):
        cmd_info = GIT_CLI_COMMANDS[cmd_key]
        
        if cmd_info['danger_level'] == 'danger':
            if not messagebox.askyesno("CANH BAO NGUY HIEM", 
                f"Ban dang thuc hien lenh NGUY HIEM!\n{cmd_info['danger_note']}\nTiep tuc?"):
                return
            if not messagebox.askyesno("XAC NHAN LAN 2", "DAY LA HANH DONG KHONG THE HOAN TAC!\nTiep tuc?"):
                return
        elif cmd_info['danger_level'] == 'warning':
            if not messagebox.askyesno("Xac nhan", f"Tiep tuc thuc hien: {cmd_info['name']}?"):
                return
        
        self._update_status(f"Dang thuc thi: {cmd_info['name']}...")
        thread = threading.Thread(target=self._run_git_command, args=(cmd_key, cmd_info))
        thread.start()
    
    def _run_git_command(self, cmd_key, cmd_info):
        local_path = self.param_widgets['local_path'].get().strip()
        token = self.access_token.get().strip()
        gitea_url = self.gitea_url.get().strip().rstrip('/')
        owner = self.param_widgets['owner'].get().strip()
        repo = self.param_widgets['repo_name'].get().strip()
        branch = self.param_widgets['branch_name'].get().strip()
        commit_msg = self.param_widgets['commit_message'].get().strip()
        
        parsed = urllib.parse.urlparse(gitea_url)
        host = parsed.netloc
        
        try:
            result = ""
            cmd_type = cmd_info['command_type']
            
            if cmd_type == 'config':
                result = self._run_cmd(['git', 'config', '--global', 'credential.helper', 'store'])
                result += "\n\nDa cau hinh credential helper!\n"
                result += f"Khi clone/pull/push lan dau, nhap:\n"
                result += f"  Username: {owner or '<your_username>'}\n"
                result += f"  Password: <your_token>\n"
            
            elif cmd_type == 'clone':
                if not owner or not repo:
                    self._show_result_safe("Vui long nhap Owner va Ten Repo!")
                    return
                if not local_path:
                    self._show_result_safe("Vui long chon thu muc luu code!")
                    return
                
                clone_url = f"https://{token}@{host}/{owner}/{repo}.git" if token else f"https://{host}/{owner}/{repo}.git"
                target_dir = os.path.join(local_path, repo)
                result = self._run_cmd(['git', 'clone', clone_url, target_dir])
                result += f"\n\nDa clone repo vao: {target_dir}"
            
            elif cmd_type == 'pull':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'pull'], cwd=local_path)
            
            elif cmd_type == 'fetch':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'fetch', '--all'], cwd=local_path)
            
            elif cmd_type == 'status':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'status'], cwd=local_path)
            
            elif cmd_type == 'branch_list':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'branch', '-a'], cwd=local_path)
            
            elif cmd_type == 'checkout':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                if not branch:
                    self._show_result_safe("Vui long nhap ten branch!")
                    return
                result = self._run_cmd(['git', 'checkout', branch], cwd=local_path)
            
            elif cmd_type == 'checkout_new':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                if not branch:
                    self._show_result_safe("Vui long nhap ten branch moi!")
                    return
                result = self._run_cmd(['git', 'checkout', '-b', branch], cwd=local_path)
            
            elif cmd_type == 'add':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'add', '-A'], cwd=local_path)
                result += "\nDa add tat ca thay doi!"
            
            elif cmd_type == 'commit':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                if not commit_msg:
                    self._show_result_safe("Vui long nhap commit message!")
                    return
                result = self._run_cmd(['git', 'commit', '-m', commit_msg], cwd=local_path)
            
            elif cmd_type == 'push':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                current_branch = self._run_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=local_path).strip()
                result = self._run_cmd(['git', 'push', 'origin', current_branch], cwd=local_path)
            
            elif cmd_type == 'push_new':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                if not branch:
                    self._show_result_safe("Vui long nhap ten branch!")
                    return
                result = self._run_cmd(['git', 'push', '-u', 'origin', branch], cwd=local_path)
            
            elif cmd_type == 'log':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'log', '--oneline', '-20'], cwd=local_path)
            
            elif cmd_type == 'stash':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'stash'], cwd=local_path)
            
            elif cmd_type == 'stash_pop':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'stash', 'pop'], cwd=local_path)
            
            elif cmd_type == 'reset_hard':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'reset', '--hard', 'HEAD'], cwd=local_path)
            
            elif cmd_type == 'merge':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                if not branch:
                    self._show_result_safe("Vui long nhap ten branch can merge!")
                    return
                result = self._run_cmd(['git', 'merge', branch], cwd=local_path)
            
            elif cmd_type == 'diff':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'diff'], cwd=local_path)
                if not result.strip():
                    result = "Khong co thay doi nao."
            
            elif cmd_type == 'remote':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                result = self._run_cmd(['git', 'remote', '-v'], cwd=local_path)
            
            elif cmd_type == 'set_remote':
                if not local_path or not os.path.isdir(local_path):
                    self._show_result_safe("Thu muc khong hop le!")
                    return
                if not owner or not repo:
                    self._show_result_safe("Vui long nhap Owner va Ten Repo!")
                    return
                
                new_url = f"https://{token}@{host}/{owner}/{repo}.git" if token else f"https://{host}/{owner}/{repo}.git"
                result = self._run_cmd(['git', 'remote', 'set-url', 'origin', new_url], cwd=local_path)
                result += f"\nDa cap nhat remote URL!"
            
            else:
                result = f"Lenh chua duoc ho tro: {cmd_type}"
            
            self._show_result_safe(result)
            
        except Exception as e:
            self._show_result_safe(f"Loi: {str(e)}")
    
    def _run_cmd(self, cmd, cwd=None):
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, 
                                    timeout=120, encoding='utf-8', errors='replace')
            output = result.stdout + result.stderr
            return output if output else "Lenh thuc thi thanh cong (khong co output)"
        except subprocess.TimeoutExpired:
            return "Lenh bi timeout (qua 120 giay)"
        except Exception as e:
            return f"Loi khi chay lenh: {str(e)}"
    
    def _show_result_safe(self, text):
        self.root.after(0, lambda: self._display_cli_result(text))
    
    def _display_cli_result(self, text):
        self.result_text.delete(1.0, tk.END)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.result_text.insert(tk.END, f"{'='*60}\n")
        self.result_text.insert(tk.END, f"Thoi gian: {timestamp}\n")
        self.result_text.insert(tk.END, f"{'='*60}\n\n")
        self.result_text.insert(tk.END, text)
        self._update_status("Hoan thanh!")

    def _call_gitea_api(self, cmd_key, cmd_info, token):
        gitea_url = self.gitea_url.get().strip().rstrip('/')
        headers = {"Authorization": f"token {token}", "Accept": "application/json", "Content-Type": "application/json"}
        
        endpoint = cmd_info['endpoint']
        method = cmd_info['method']
        params = dict(cmd_info.get('params', {}))
        
        owner = self.param_widgets['owner'].get().strip()
        repo = self.param_widgets['repo_name'].get().strip()
        org = self.param_widgets['org_name'].get().strip()
        
        if '{owner}' in endpoint:
            if not owner:
                messagebox.showwarning("Canh bao", "Vui long nhap Owner!")
                return
            endpoint = endpoint.replace('{owner}', owner)
        
        if '{repo}' in endpoint:
            if not repo:
                messagebox.showwarning("Canh bao", "Vui long nhap ten Repository!")
                return
            endpoint = endpoint.replace('{repo}', repo)
        
        if '{org}' in endpoint:
            if not org:
                messagebox.showwarning("Canh bao", "Vui long nhap ten Organization!")
                return
            endpoint = endpoint.replace('{org}', org)
        
        if cmd_key == 'search_repos':
            search_query = self.param_widgets['search_query'].get().strip()
            if search_query:
                params['q'] = search_query
        
        url = f"{gitea_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json={}, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                messagebox.showerror("Loi", f"Method khong ho tro: {method}")
                return
            
            self._display_api_result(cmd_key, response)
            
        except requests.exceptions.Timeout:
            messagebox.showerror("Loi", "Ket noi timeout!")
        except Exception as e:
            messagebox.showerror("Loi", f"Loi: {str(e)}")
    
    def _display_api_result(self, cmd_key, response):
        self.result_text.delete(1.0, tk.END)
        status_code = response.status_code
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.result_text.insert(tk.END, f"{'='*60}\n")
        self.result_text.insert(tk.END, f"Thoi gian: {timestamp}\n")
        self.result_text.insert(tk.END, f"Status Code: {status_code}\n")
        self.result_text.insert(tk.END, f"{'='*60}\n\n")
        
        if status_code in [200, 201]:
            self._update_status("Thanh cong!")
            try:
                data = response.json()
                self._format_api_result(cmd_key, data)
            except:
                self.result_text.insert(tk.END, "Thuc hien thanh cong!")
        elif status_code == 204:
            self._update_status("Thanh cong!")
            self.result_text.insert(tk.END, "Thuc hien thanh cong!")
        elif status_code == 401:
            self.result_text.insert(tk.END, "Loi 401: Token khong hop le")
        elif status_code == 403:
            self.result_text.insert(tk.END, "Loi 403: Khong co quyen")
        elif status_code == 404:
            self.result_text.insert(tk.END, "Loi 404: Khong tim thay")
        else:
            self.result_text.insert(tk.END, f"Loi {status_code}:\n")
            try:
                self.result_text.insert(tk.END, json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                self.result_text.insert(tk.END, response.text)

    def _format_api_result(self, cmd_key, data):
        if cmd_key == 'repos':
            self.result_text.insert(tk.END, f"Tong so repositories: {len(data)}\n\n")
            for i, repo in enumerate(data, 1):
                visibility = "Private" if repo.get('private') else "Public"
                self.result_text.insert(tk.END, f"{i}. {repo['name']} ({visibility})\n")
                self.result_text.insert(tk.END, f"   Full: {repo['full_name']}\n")
                self.result_text.insert(tk.END, f"   URL: {repo['html_url']}\n")
                self.result_text.insert(tk.END, f"   Mo ta: {repo.get('description', 'Khong co') or 'Khong co'}\n\n")
        
        elif cmd_key == 'user_info':
            self.result_text.insert(tk.END, f"Username: {data['login']}\n")
            self.result_text.insert(tk.END, f"Full name: {data.get('full_name', 'N/A')}\n")
            self.result_text.insert(tk.END, f"Email: {data.get('email', 'N/A')}\n")
            self.result_text.insert(tk.END, f"ID: {data['id']}\n")
        
        elif cmd_key == 'list_branches':
            self.result_text.insert(tk.END, f"Tong so branches: {len(data)}\n\n")
            for branch in data:
                protected = "[Protected]" if branch.get('protected') else ""
                self.result_text.insert(tk.END, f"  - {branch['name']} {protected}\n")
        
        elif cmd_key == 'list_commits':
            self.result_text.insert(tk.END, f"Commits gan nhat ({len(data)}):\n\n")
            for commit in data:
                sha = commit.get('sha', commit.get('id', 'N/A'))[:8]
                commit_data = commit.get('commit', commit)
                msg = commit_data.get('message', 'N/A').split('\n')[0][:55]
                author = commit_data.get('author', {}).get('name', 'N/A')
                self.result_text.insert(tk.END, f"  {sha} - {msg}\n")
                self.result_text.insert(tk.END, f"         Author: {author}\n\n")
        
        elif cmd_key == 'repo_info':
            self.result_text.insert(tk.END, f"Thong tin Repository: {data['name']}\n\n")
            self.result_text.insert(tk.END, f"Full name: {data['full_name']}\n")
            self.result_text.insert(tk.END, f"ID: {data['id']}\n")
            self.result_text.insert(tk.END, f"Mo ta: {data.get('description', 'N/A') or 'N/A'}\n")
            self.result_text.insert(tk.END, f"Private: {data.get('private', False)}\n")
            self.result_text.insert(tk.END, f"Default branch: {data.get('default_branch', 'N/A')}\n\n")
            self.result_text.insert(tk.END, f"Web URL:\n   {data['html_url']}\n\n")
            self.result_text.insert(tk.END, f"Clone HTTP:\n   {data.get('clone_url', 'N/A')}\n\n")
            self.result_text.insert(tk.END, f"Clone SSH:\n   {data.get('ssh_url', 'N/A')}\n")
        
        elif cmd_key == 'list_orgs':
            self.result_text.insert(tk.END, f"Tong so organizations: {len(data)}\n\n")
            for org in data:
                self.result_text.insert(tk.END, f"  - {org['username']} (ID: {org['id']})\n")
                self.result_text.insert(tk.END, f"    Mo ta: {org.get('description', 'Khong co') or 'Khong co'}\n\n")
        
        elif cmd_key == 'org_repos':
            self.result_text.insert(tk.END, f"Repos trong organization: {len(data)}\n\n")
            for repo in data:
                visibility = "Private" if repo.get('private') else "Public"
                self.result_text.insert(tk.END, f"  - {repo['name']} ({visibility})\n")
                self.result_text.insert(tk.END, f"    URL: {repo['html_url']}\n\n")
        
        elif cmd_key == 'search_repos':
            repos = data.get('data', data) if isinstance(data, dict) else data
            self.result_text.insert(tk.END, f"Ket qua tim kiem: {len(repos)} repos\n\n")
            for repo in repos:
                visibility = "Private" if repo.get('private') else "Public"
                self.result_text.insert(tk.END, f"  - {repo['full_name']} ({visibility})\n")
                self.result_text.insert(tk.END, f"    URL: {repo['html_url']}\n\n")
        
        else:
            self.result_text.insert(tk.END, json.dumps(data, indent=2, ensure_ascii=False))

    def _update_status(self, message):
        self.status_bar.config(text=f"{message}")
        self.root.update_idletasks()
    
    def _save_config(self):
        token = self.access_token.get().strip()
        gitea_url = self.gitea_url.get().strip()
        local_path = self.param_widgets['local_path'].get().strip()
        
        if not token:
            messagebox.showwarning("Canh bao", "Khong co token de luu!")
            return
        
        if not messagebox.askyesno("Xac nhan", "Token se duoc luu dang text thuan.\nChi luu tren may ca nhan an toan!\nTiep tuc?"):
            return
        
        try:
            config_dir = os.path.expanduser("~/.gitea_tool")
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, "config.json")
            config = {"gitea_url": gitea_url, "token": token, "local_path": local_path}
            with open(config_file, 'w') as f:
                json.dump(config, f)
            messagebox.showinfo("Thanh cong", "Cau hinh da duoc luu!")
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the luu: {str(e)}")
    
    def _load_saved_config(self):
        try:
            config_file = os.path.expanduser("~/.gitea_tool/config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('gitea_url'):
                        self.gitea_url.set(config['gitea_url'])
                    if config.get('token'):
                        self.access_token.set(config['token'])
                    if config.get('local_path'):
                        self.param_widgets['local_path'].delete(0, tk.END)
                        self.param_widgets['local_path'].insert(0, config['local_path'])
                    self._update_status("Da load cau hinh tu file")
        except:
            pass
    
    def _clear_saved_config(self):
        try:
            config_file = os.path.expanduser("~/.gitea_tool/config.json")
            if os.path.exists(config_file):
                os.remove(config_file)
                messagebox.showinfo("Thanh cong", "Da xoa cau hinh da luu!")
            else:
                messagebox.showinfo("Thong bao", "Khong co cau hinh nao duoc luu!")
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the xoa: {str(e)}")
    
    def _export_result(self):
        content = self.result_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Canh bao", "Khong co ket qua de xuat!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"gitea_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Thanh cong", "Da xuat ket qua!")
            except Exception as e:
                messagebox.showerror("Loi", f"Khong the xuat file: {str(e)}")

    def _show_token_guide(self):
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Huong dan tao Gitea Access Token")
        guide_window.geometry("700x550")
        guide_window.transient(self.root)
        
        text = scrolledtext.ScrolledText(guide_window, font=('Consolas', 10), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        gitea_url = self.gitea_url.get().strip().rstrip('/')
        
        guide_content = f"""
HUONG DAN TAO GITEA ACCESS TOKEN
================================

BUOC 1: Truy cap Gitea Settings
-------------------------------
1. Dang nhap vao Gitea: {gitea_url}
2. Click vao avatar goc phai tren -> Settings
3. Trong menu trai, chon "Applications"
4. Hoac truy cap truc tiep:
   {gitea_url}/user/settings/applications

BUOC 2: Tao Token moi
---------------------
1. Trong phan "Manage Access Tokens"
2. Nhap "Token Name" (VD: "Gitea Tool App")
3. Chon quyen truy cap:
   - All (public, private, and limited) - TAT CA (khuyen nghi)
   - Tick tat ca permissions: repo, issue, organization, user

BUOC 3: Tao va Luu Token
------------------------
1. Click "Generate Token"
2. QUAN TRONG: Copy token NGAY LAP TUC!
3. Token chi hien thi MOT LAN duy nhat!
4. Dan token vao ung dung nay

CANH BAO BAO MAT
----------------
- KHONG chia se token voi bat ky ai
- KHONG commit token vao code
- KHONG gui token qua chat/email

MUC DO NGUY HIEM CUA CAC LENH
-----------------------------
[OK] SAFE (An toan): Chi doc du lieu
[!!] WARNING (Can than): Tao moi du lieu
[XX] DANGER (Nguy hiem): Xoa du lieu vinh vien

Link tao token:
{gitea_url}/user/settings/applications
        """
        
        text.insert(tk.END, guide_content)
        text.config(state=tk.DISABLED)
        
        btn_frame = ttk.Frame(guide_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Mo Gitea Settings", 
                   command=lambda: webbrowser.open(f"{gitea_url}/user/settings/applications")).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Dong", command=guide_window.destroy).pack(side=tk.RIGHT)
    
    def _show_about(self):
        about_text = """
Gitea Tool v2.0.0

Ung dung GUI ho tro quan ly Gitea
thong qua Access Token va Git CLI.

Ho tro Gitea self-hosted (git.icomm.vn)

Tinh nang API:
- Xem danh sach repos, orgs
- Tim kiem repositories
- Xem branches, commits

Tinh nang Git CLI:
- Clone repo voi token
- Pull/Push code
- Chuyen branch
- Commit thay doi
- Stash/Reset
- Merge branches

Developed by Kiro Assistant
        """
        messagebox.showinfo("Ve ung dung", about_text)


# ============== MAIN ==============
def main():
    root = tk.Tk()
    app = GiteaToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
