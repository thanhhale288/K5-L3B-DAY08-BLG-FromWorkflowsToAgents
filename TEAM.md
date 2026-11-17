# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Tấn Dũng | 2A202603734 | 26ai.dungnt15@vinuni.edu.vn | dungtran16042003-afk | Workflow, crash và idempotency |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Thành viên 1 | Workflow, crash và idempotency | `5cbc979` | `test_public_matrix.py` (workflow: 62/62); `test_workflow_durability.py` (retry, crash-resume: 2/2); crash suite (20/20) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603734_NguyenTanDung

### Phần việc phụ trách

- Shape A `workflow`, kiểm thử retry/crash-resume, crash suite, cập nhật bảng đóng góp và phần Crash & Durability trong báo cáo nhóm.

### Đóng góp cụ thể

- Cài đặt `src/lab8/shapes/workflow.py` theo luồng claim → order/ownership → quote → host; mọi nhánh kết thúc bình thường đi qua `finish()`.
- Chuyển quote đầy đủ và `crash_at` cho `issue_refund`; không xử lý tiền trong model, không tự trừ khoản refund trước và không nuốt `InjectedCrash`.
- Thêm `src/tests/test_workflow_durability.py` cho retry cùng claim và crash rồi resume.
- Commit code/test: `5cbc979`; commit báo cáo và crash evidence: `97124b3`.

### Bằng chứng

- Ma trận student workflow: 62/62.
- Test workflow retry và crash-resume: 2/2; run IDs được kiểm tra: `R-workflow-C-011-s11`, `R-workflow-C-012-s11`.
- Crash suite sinh `src/reports/crash.json`: 20/20.
- Bộ test mặc định tại thời điểm kiểm tra: 67 passed.
- T11/T12 trên workflow và orchestrator đạt; single chưa triển khai ở thời điểm kiểm tra nên hai ca tương ứng chưa đạt cho toàn bộ ba shape.

### Công cụ AI đã dùng

- Dùng Copilot để đọc hướng dẫn, hỗ trợ triển khai workflow, tạo test và rà soát kết quả. Tự kiểm tra bằng pytest trong `src/.venv` và crash suite; cần tự đọc lại code, test và giải thích được ranh giới giữa code, model và host.

### Tự đánh giá

- Phần workflow và crash/durability đã có kiểm thử công khai và bằng chứng 20/20. Chưa thể xác nhận yêu cầu T11/T12 trên cả ba shape cho tới khi single được triển khai và kiểm tra lại.
