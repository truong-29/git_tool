from .scenarios import GitScenarios
from .core import GitCore
from .utils import print_header, print_info, get_input, clear_screen, Colors

class GitUI:
    def __init__(self):
        self.scenarios = GitScenarios()
        self.core = GitCore()

    def show_main_menu(self):
        clear_screen()
        print_header("GIT ASSISTANT - CÔNG CỤ HỖ TRỢ GIT CHO NGƯỜI MỚI")
        print(f"Thư mục hiện tại: {self.core.working_dir}")
        current_branch = self.core.current_branch()
        print(f"Nhánh hiện tại: {Colors.GREEN}{current_branch}{Colors.ENDC}")
        print("-" * 50)
        print("1. [Quy trình] Đẩy code lên Server (Add -> Commit -> Push)")
        print("2. [Quy trình] Kéo code mới về (Pull)")
        print("3. [Quy trình] Đồng bộ an toàn từ Main (Stash -> Pull Main -> Pop)")
        print("4. [Quy trình] Bắt đầu tính năng mới (Tạo nhánh chuẩn)")
        print("5. [Công cụ] Xem trạng thái (Status)")
        print("6. [Công cụ] Quản lý lưu tạm (Stash/Pop)")
        print("0. Thoát")
        print("-" * 50)

    def run(self):
        while True:
            self.show_main_menu()
            choice = get_input("Chọn chức năng")
            
            if choice == '1':
                self.scenarios.workflow_push_code()
            elif choice == '2':
                self.scenarios.workflow_pull_code()
            elif choice == '3':
                self.scenarios.workflow_sync_main()
            elif choice == '4':
                self.scenarios.workflow_new_feature()
            elif choice == '5':
                s_ok, s_out = self.core.status()
                print(s_out)
            elif choice == '6':
                self.scenarios.workflow_fix_conflict_stash()
            elif choice == '0':
                print("Tạm biệt!")
                break
            else:
                print_info("Lựa chọn không hợp lệ.")
            
            get_input("Nhấn Enter để quay lại menu...")
