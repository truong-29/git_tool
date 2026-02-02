from .core import GitCore
from .io_handler import IOHandler, ConsoleIO

class GitScenarios:
    def __init__(self, io_handler: IOHandler = None):
        self.io = io_handler if io_handler else ConsoleIO()
        self.git = GitCore(io_handler=self.io)

    def workflow_push_code(self):
        """Luồng đẩy code cơ bản: Add -> Commit -> Push"""
        self.io.log("=== QUY TRÌNH ĐẨY CODE (PUSH) ===")
        
        # 1. Check Status
        s_ok, s_out = self.git.status()
        self.io.log(s_out)
        
        if "nothing to commit, working tree clean" in s_out:
            self.io.warning("Không có thay đổi nào để đẩy lên.")
            return

        # 2. Add All
        if self.io.confirm("Bạn có muốn thêm tất cả thay đổi (git add .)?"):
            self.git.add_all()
        else:
            self.io.log("Đã hủy bước add.")
            return

        # 3. Commit
        msg = self.io.input("Nhập nội dung commit (commit message)")
        if not msg:
            self.io.error("Nội dung commit không được để trống!")
            return
            
        c_ok, c_out = self.git.commit(msg)
        if c_ok:
            self.io.success("Đã commit thành công.")
        else:
            self.io.error(f"Lỗi commit: {c_out}")
            return

        # 4. Push
        current_branch = self.git.current_branch()
        if self.io.confirm(f"Bạn có muốn đẩy lên nhánh '{current_branch}' không?"):
            p_ok, p_out = self.git.push(current_branch)
            if p_ok:
                self.io.success("Đã đẩy code lên thành công!")
                self.io.log(p_out)
            else:
                self.io.error(f"Lỗi push: {p_out}")
                self.io.log("Gợi ý: Nếu bị từ chối, có thể bạn cần pull code mới về trước.")

    def workflow_pull_code(self):
        """Luồng kéo code: Fetch -> Pull"""
        self.io.log("=== QUY TRÌNH KÉO CODE (PULL) ===")
        
        # 1. Fetch
        self.git.fetch()
        
        # 2. Check changes local
        if self.git.has_changes():
            self.io.warning("Bạn đang có các thay đổi chưa commit!")
            if self.io.confirm("Bạn có muốn lưu tạm (stash) trước khi pull không?"):
                self.git.stash(f"Auto stash before pull {self.git.current_branch()}")
                self.io.success("Đã stash thay đổi.")
        
        # 3. Pull
        ok, out = self.git.pull()
        if ok:
            self.io.success("Cập nhật code thành công!")
            self.io.log(out)
        else:
            self.io.error(f"Lỗi pull: {out}")
            self.io.log("Có thể xảy ra xung đột (conflict). Hãy kiểm tra thủ công.")

    def workflow_sync_main(self):
        """Luồng đồng bộ: Stash -> Checkout Main -> Pull -> Checkout Back -> Merge Main -> Pop Stash"""
        self.io.log("=== QUY TRÌNH ĐỒNG BỘ TỪ MAIN (SAFE SYNC) ===")
        
        current_branch = self.git.current_branch()
        main_branch = "main" # Hoặc master, nên check
        
        # Hỏi user tên nhánh chính
        user_main = self.io.input(f"Nhập tên nhánh chính (mặc định: {main_branch})")
        if user_main: main_branch = user_main
        
        if current_branch == main_branch:
            self.io.warning("Bạn đang ở nhánh chính rồi. Chỉ cần Pull.")
            self.workflow_pull_code()
            return

        # 1. Stash changes
        has_changes = self.git.has_changes()
        if has_changes:
            self.io.log("Phát hiện thay đổi, đang lưu tạm (Stash)...")
            self.git.stash(f"Sync main stash {current_branch}")

        # 2. Checkout Main & Pull
        self.io.log(f"Chuyển sang {main_branch} để cập nhật...")
        self.git.checkout(main_branch)
        self.git.pull()

        # 3. Checkout Back
        self.io.log(f"Quay lại nhánh {current_branch}...")
        self.git.checkout(current_branch)

        # 4. Merge Main
        self.io.log(f"Gộp code từ {main_branch} vào {current_branch}...")
        m_ok, m_out = self.git.merge(main_branch)
        if m_ok:
            self.io.success("Merge thành công.")
        else:
            self.io.error(f"Merge thất bại (Conflict): {m_out}")
            self.io.warning("Vui lòng giải quyết xung đột thủ công trước khi tiếp tục.")
            return # Dừng ở đây nếu conflict

        # 5. Pop Stash
        if has_changes:
            self.io.log("Khôi phục thay đổi đã lưu (Pop Stash)...")
            p_ok, p_out = self.git.stash_pop()
            if p_ok:
                self.io.success("Khôi phục thành công.")
            else:
                self.io.warning("Có xung đột khi khôi phục stash. Hãy kiểm tra file.")

    def workflow_new_feature(self):
        """Tạo nhánh mới: Pull Main -> Checkout -b New -> Làm việc"""
        self.io.log("=== BẮT ĐẦU TÍNH NĂNG MỚI ===")
        
        # 1. Update Main first
        self.io.log("Nên cập nhật nhánh chính trước khi tạo nhánh mới.")
        main_branch = "main"
        user_main = self.io.input(f"Nhập tên nhánh chính (mặc định: {main_branch})")
        if user_main: main_branch = user_main
        
        self.git.checkout(main_branch)
        self.git.pull()
        
        # 2. Create Branch
        new_branch = self.io.input("Nhập tên nhánh mới (VD: feature/login-page)")
        if not new_branch:
            self.io.error("Tên nhánh không được trống.")
            return
            
        self.git.checkout_new(new_branch)
        self.io.success(f"Đã chuyển sang nhánh {new_branch}. Bạn có thể bắt đầu code!")

    def workflow_fix_conflict_stash(self):
        """Hỗ trợ xử lý khi kéo code về bị mất code (do stash chưa pop)"""
        self.io.log("=== KHÔI PHỤC CODE TẠM LƯU (STASH LIST) ===")
        
        ok, out = self.git.stash_list()
        self.io.log(out)
        
        if not out:
            self.io.log("Không có bản lưu tạm nào.")
            return
            
        self.io.log("Sử dụng lệnh 'git stash pop' hoặc 'git stash apply stash@{n}' để khôi phục.")
        idx = self.io.input("Nhập chỉ số stash muốn khôi phục (0 là mới nhất, để trống để chọn 0)")
        if not idx: idx = "0"
        
        cmd = ['stash', 'apply', f'stash@{{{idx}}}']
        ok, out = self.git.run_command(cmd)
        if ok:
            self.io.success("Khôi phục thành công!")
            # Hỏi có muốn drop không
            if self.io.confirm("Bạn có muốn xóa bản lưu này khỏi danh sách không?"):
                self.git.run_command(['stash', 'drop', f'stash@{{{idx}}}'])
        else:
            self.io.error(f"Lỗi khi khôi phục: {out}")
