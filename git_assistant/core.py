import subprocess
import os

class GitCore:
    def __init__(self, working_dir=None, io_handler=None):
        self.working_dir = working_dir if working_dir else os.getcwd()
        self.io = io_handler
        
    def _log(self, msg):
        if self.io:
            self.io.log(f"ℹ {msg}")

    def run_command(self, args, show_output=True):
        """Chạy lệnh git và trả về (success, output)"""
        try:
            full_cmd = ['git'] + args
            
            # Run command
            # Trên Windows, nếu không set encoding='utf-8', output có thể bị lỗi font
            # Tuy nhiên, một số git client cũ có thể dùng encoding khác, nên ta handle exception
            try:
                result = subprocess.run(
                    full_cmd, 
                    cwd=self.working_dir, 
                    text=True, 
                    capture_output=True,
                    encoding='utf-8'
                )
            except UnicodeDecodeError:
                # Fallback nếu utf-8 lỗi (ví dụ git trả về cp1252)
                result = subprocess.run(
                    full_cmd, 
                    cwd=self.working_dir, 
                    text=True, 
                    capture_output=True
                )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)

    def status(self):
        return self.run_command(['status'], show_output=False)

    def fetch(self):
        self._log("Đang lấy dữ liệu mới từ remote (fetch)...")
        return self.run_command(['fetch', '--all'])

    def pull(self):
        self._log("Đang kéo code mới về (pull)...")
        return self.run_command(['pull'])

    def push(self, branch=None):
        cmd = ['push']
        if branch:
            cmd.extend(['origin', branch])
        self._log(f"Đang đẩy code lên (push) {branch if branch else ''}...")
        return self.run_command(cmd)

    def add_all(self):
        self._log("Đang thêm tất cả thay đổi (git add .)...")
        return self.run_command(['add', '.'])

    def commit(self, message):
        self._log(f"Đang commit với nội dung: {message}")
        return self.run_command(['commit', '-m', message])

    def stash(self, message=None):
        cmd = ['stash']
        if message:
            cmd.extend(['save', message])
        self._log("Đang lưu tạm thay đổi (stash)...")
        return self.run_command(cmd)

    def stash_pop(self):
        self._log("Đang lấy lại thay đổi từ stash (stash pop)...")
        return self.run_command(['stash', 'pop'])
    
    def stash_list(self):
        return self.run_command(['stash', 'list'])

    def get_branches(self):
        """Lấy danh sách tất cả các branch local và remote"""
        # Fetch trước để cập nhật danh sách remote
        self.run_command(['fetch', '--all'], show_output=False)
        
        # Lấy danh sách branch
        success, output = self.run_command(['branch', '-a'], show_output=False)
        if not success:
            return []
            
        branches = []
        for line in output.split('\n'):
            line = line.strip()
            if not line: continue
            
            # Bỏ qua con trỏ HEAD detached
            if "HEAD detached" in line: continue
            
            # Xóa dấu * và khoảng trắng (đánh dấu branch hiện tại)
            clean_name = line.replace('*', '').strip()
            
            # Xử lý remote branch (remotes/origin/main -> main)
            # Tuy nhiên, để checkout, ta nên giữ nguyên tên nếu nó là local, 
            # hoặc chỉ lấy phần tên sau remotes/origin nếu muốn checkout tracking.
            # Đơn giản nhất: Lấy list local branches. Nếu muốn remote, user nên checkout -b.
            # Nhưng để switch, ta ưu tiên list local trước.
            
            if clean_name.startswith('remotes/'):
                continue # Tạm thời chỉ list local branches để switch cho đơn giản
            
            branches.append(clean_name)
            
        return sorted(list(set(branches)))

    def current_branch(self):
        success, output = self.run_command(['rev-parse', '--abbrev-ref', 'HEAD'], show_output=False)
        if success:
            return output
        return None

    def checkout(self, branch):
        self._log(f"Đang chuyển sang nhánh {branch}...")
        return self.run_command(['checkout', branch])

    def checkout_new(self, branch):
        self._log(f"Đang tạo và chuyển sang nhánh mới {branch}...")
        return self.run_command(['checkout', '-b', branch])
        
    def merge(self, branch):
        self._log(f"Đang merge nhánh {branch} vào hiện tại...")
        return self.run_command(['merge', branch])

    def has_changes(self):
        success, output = self.status()
        if not success: return False
        return "nothing to commit, working tree clean" not in output
