# Git Assistant Tool

Công cụ hỗ trợ Git workflows chuẩn cho người mới bắt đầu. Được thiết kế lại theo mô hình module hóa.

## Cấu trúc dự án

- **github_tool.py**: File chạy chính của chương trình.
- **git_assistant/**: Thư mục chứa mã nguồn (Package).
  - `core.py`: Xử lý các lệnh Git cơ bản (wrapper cho git command line).
  - `scenarios.py`: Các kịch bản/quy trình làm việc (Workflows) như Sync, Push, Pull an toàn.
  - `ui.py`: Giao diện menu dòng lệnh.
  - `utils.py`: Các hàm tiện ích (màu sắc, in ấn).

## Cách sử dụng

Mở terminal tại thư mục này và chạy:

```bash
python github_tool.py
```

## Các tính năng chính

1. **Quy trình Đẩy code (Push)**: Tự động Add -> Commit -> Push.
2. **Quy trình Kéo code (Pull)**: Tự động Fetch -> Check thay đổi -> Pull.
3. **Đồng bộ an toàn (Safe Sync)**: 
   - Tự động Stash thay đổi hiện tại.
   - Pull code mới nhất từ Main.
   - Merge vào nhánh hiện tại.
   - Pop Stash để khôi phục thay đổi đang làm dở.
4. **Tạo tính năng mới**: Update Main -> Checkout nhánh mới.

## Yêu cầu

- Python 3.x
- Git đã được cài đặt và cấu hình trong PATH.
