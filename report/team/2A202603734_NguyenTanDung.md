# Báo cáo cá nhân — Nguyễn Tấn Dũng

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tấn Dũng
- MSSV: 2A202603734
- Email: 26ai.dungnt15@vinuni.edu.vn
- GitHub: dungtran16042003-afk

## 2. Phần việc phụ trách

Shape A `workflow`, kiểm thử retry/crash-resume, crash suite, cập nhật bảng đóng góp và phần Crash & Durability trong báo cáo nhóm.

## 3. Đóng góp cụ thể

- Cài đặt `src/lab8/shapes/workflow.py` theo luồng claim → order/ownership → quote → host; mọi nhánh kết thúc bình thường đi qua `finish()`.
- Chuyển quote đầy đủ và `crash_at` cho `issue_refund`; không xử lý tiền trong model, không tự trừ khoản refund trước và không nuốt `InjectedCrash`.
- Thêm `src/tests/test_workflow_durability.py` cho retry cùng claim và crash rồi resume.
- Commit code/test: `5cbc979`.
- Commit crash report và tài liệu đóng góp: `97124b3`.

## 4. Bằng chứng

- Ma trận student workflow: 62/62.
- Test workflow retry và crash-resume: 2/2; run IDs được kiểm tra: `R-workflow-C-011-s11`, `R-workflow-C-012-s11`.
- Crash suite do công cụ sinh trong `src/reports/crash.json`: 20/20.
- Bộ test mặc định tại thời điểm kiểm tra: 67 passed.
- T11/T12 trên workflow và orchestrator đạt; single chưa triển khai tại thời điểm kiểm tra nên chưa thể xác nhận yêu cầu trên cả ba shape.

## 5. Công cụ AI đã dùng

Dùng Copilot để đọc hướng dẫn, hỗ trợ triển khai workflow, tạo test và rà soát kết quả. Tự kiểm tra bằng pytest trong `src/.venv` và crash suite. Cần tự đọc lại code, test và giải thích được ranh giới giữa code, model và host.

## 6. Tự đánh giá

Phần workflow và crash/durability đã có kiểm thử công khai và bằng chứng 20/20. Việc xác nhận T11/T12 trên cả ba shape còn phụ thuộc vào triển khai single và cần chạy lại sau khi tích hợp.
