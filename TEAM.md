# Team

## Thông tin nhóm

- Tên nhóm: BLG
- Lớp: L3A
- Repo nhóm: `K5-L3B-DAY08-BLG-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/thanhhale288/K5-L3B-DAY08-BLG-FromWorkflowsToAgents, nhánh `main`, commit chốt `b3e7b77`

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
| Thành viên 2 | Single (ReAct), approval và policy, research card, bonus B2 | `632ad7c` (code, test, ablation); `0392ceb`, `018fe7d` (báo cáo); bonus B2 trong commit chốt | `test_single_react.py` (14); `test_approval_policy_branches.py` (36, chạy trên cả ba shape); `test_bonus_mast.py`, `test_bonus_variants.py` (40); `test_public_matrix.py` (single: 62/62) |
| Thành viên 3 | Orchestrator, trace an toàn, benchmark và ADR | `91a39ef` (code, test); `10db862` (benchmark, crash evidence, báo cáo); `ae99623` (hoàn thiện) | `test_orchestrator_safety.py` (11 trường hợp); `test_public_matrix.py` (orchestrator: 62/62) |
