# Team

## Thông tin nhóm

- Tên nhóm: BLG
- Lớp: L3A
- Repo nhóm: `K5-L3B-DAY08-BLG-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/thanhhale288/K5-L3B-DAY08-BLG-FromWorkflowsToAgents, nhánh `main`, commit chốt `1869bd0`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Tấn Dũng | 2A202603734 | 26ai.dungnt15@vinuni.edu.vn | dungtran16042003-afk | Workflow, crash và idempotency |
|   2 | Lê Thanh Hà | 2A202603901 | haroman2808@gmail.com | thanhhale288 | Single (ReAct), approval và policy, research card |
|   3 | Lê Huy Anh | 2A202603786 | hanhfpt2226@gmail.com | hann1holic | Orchestrator, trace an toàn, benchmark và ADR |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Thành viên 1 | Workflow, crash và idempotency | `5cbc979` (code); `f1a1590`, `340ba34`, `151c338` (bằng chứng, báo cáo) | `test_public_matrix.py` (workflow: 62/62); `test_workflow_durability.py` (retry, crash-resume: 2/2); crash suite (20/20) |
| Thành viên 2 | Single (ReAct), approval và policy, research card | `632ad7c` (code, test, ablation); `0392ceb`, `018fe7d` (báo cáo) | `test_single_react.py` (14); `test_approval_policy_branches.py` (36, chạy trên cả ba shape); `test_public_matrix.py` (single: 62/62) |
| Thành viên 3 | Orchestrator, trace an toàn, benchmark và ADR | `91a39ef` (code, test); `10db862` (benchmark, crash evidence, báo cáo); `ae99623` (hoàn thiện) | `test_orchestrator_safety.py` (11 trường hợp); `test_public_matrix.py` (orchestrator: 62/62) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603734_NguyenTanDung

### Phần việc phụ trách

- Shape A `workflow`, kiểm thử retry/crash-resume, crash suite và cập nhật bảng đóng góp.

### Đóng góp cụ thể

- Cài đặt `src/lab8/shapes/workflow.py` theo luồng claim → order/ownership → quote → host; mọi nhánh kết thúc bình thường đi qua `finish()`.
- Chuyển quote đầy đủ và `crash_at` cho `issue_refund`; không xử lý tiền trong model, không tự trừ khoản refund trước và không nuốt `InjectedCrash`.
- Thêm `src/tests/test_workflow_durability.py` cho retry cùng claim và crash rồi resume.
- Commit code/test: `5cbc979`; commit báo cáo và crash evidence: `97124b3`.

### Bằng chứng

- Ma trận student workflow: 62/62.
- Test workflow retry và crash-resume: 2/2; run IDs được kiểm tra: `R-workflow-C-011-s11`, `R-workflow-C-012-s11`.
- Crash suite sinh `src/reports/crash.json`: 20/20.
- Bộ test mặc định tại thời điểm kiểm tra: 117 passed.
- Ma trận student hiện tại: 248 passed; T11/T12 đạt trên các shape workflow, single và orchestrator.

### Công cụ AI đã dùng

- Dùng Copilot để đọc hướng dẫn, hỗ trợ triển khai workflow, tạo test và rà soát kết quả. Tự kiểm tra bằng pytest trong `src/.venv` và crash suite; cần tự đọc lại code, test và giải thích được ranh giới giữa code, model và host.

### Tự đánh giá

- Phần workflow và crash/durability đã có kiểm thử công khai; sau khi tích hợp single, cả ba shape đều đạt T11/T12 và crash suite đạt 20/20.
