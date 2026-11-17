# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape C — Orchestrator và investigator

Orchestrator đọc claim qua `get_claim_view`, xử lý claim không tồn tại hoặc thiếu mã đơn, rồi tạo handoff bằng `make_handoff` với facts rỗng. Investigator chỉ được gọi `lookup_order`, `lookup_policy`, `compute_compensation`, dùng principal của claim để giới hạn quyền xem đơn. Quote do code tính từ order và policy hiện hành; nội dung ticket không quyết định số tiền. Chỉ orchestrator gọi `issue_refund` với quote đầy đủ; host kiểm approval, giới hạn theo đơn và idempotency. `crash_at` được truyền cho host; crash không bị nuốt và connection đóng trong `finally`.

MockLLM chỉ nhận yêu cầu lập kế hoạch cố định và soạn chữ từ status/quote. Handoff được lọc bằng allowlist, không chuyển parent context. Trace ghi handoff đã sanitize, trạng thái visible của order, quote, kết quả host và quyết định cuối; không ghi ticket, claim/order row thô, secret, header hay PII. Mọi nhánh trả bình thường dùng `finish` để ghi trace mới đúng contract. Chi tiết kiểm thử và benchmark sơ bộ của phần này: [orchestrator_notes.md](orchestrator_notes.md).

### Shape B — Single agent (ReAct)

Code đọc claim qua `get_claim_view` trước vòng lặp. Claim không tồn tại (`failed`) hoặc thiếu mã đơn (`needs_info`) kết thúc ở đây, không tốn bước ReAct. Sau đó `run_react` chạy tối đa 8 bước với `worker=True`, nên dispatcher chỉ nhận tool đọc; `issue_refund`, `append_audit` hay tên tool lạ đều bị `ToolRejected` và shape trả `failed`. Mỗi bước gọi `complete()` một lần để tính cost model. Prompt chỉ chứa số bước và tên tool đã đọc, không chứa ticket. Việc chọn tool do `_policy` đảm nhiệm. Đây là chính sách viết sẵn đóng vai model, vì MockLLM chỉ trả chữ cố định chứ không tự chọn tool được. Thứ tự là `lookup_order` → `compute_compensation` → final, và dừng sớm khi order không visible.

Ranh giới code / model nằm ở ba chỗ:
1. `_lock_args` ghi đè `principal_id`, `order_id`, `claim_id` của mọi tool call bằng giá trị lấy từ claim. `compute_compensation` luôn nhận đúng order mà `lookup_order` trả về, nên model không trỏ được sang đơn khác hay bịa ra một order "béo".
2. `final` của vòng lặp chỉ là tín hiệu "sẵn sàng". Sau vòng lặp, code tự suy ra status từ kết quả tool đã thu thập: chưa có order → `failed`, order không visible → `escalated`, quote 0 → `denied` và không gọi host.
3. Chỉ code sau vòng lặp mới gọi `durability.issue_refund` với quote đầy đủ và `crash_at`, không bắt `InjectedCrash`. Chạm 8 bước thì trả `failed` (`step_cap`) và không ghi gì.

Trace ghi một event cho mỗi bước ReAct: tool vừa chọn, kèm tóm tắt kết quả bước trước (`visible`/`reason` của order, `amount_vnd`/`reason`/`clause_ids` của quote). Ngoài ra trace ghi kết quả host và quyết định cuối. Trace không ghi ticket, order row, claim row hay tham số tool. Mọi nhánh return đi qua `finish`.

### Approval, policy và trần theo đơn (C4)

Nhóm không tự kiểm approval trong shape. Cả ba shape gọi host với quote đầy đủ, và host quyết định. Nhờ vậy mọi lần từ chối đều có audit `policy_denied` và không shape nào bypass được approval. Thành viên 2 rà các nhánh trên cả ba shape bằng `src/tests/test_approval_policy_branches.py` (36 test). Mỗi test sửa một store public mới rồi kiểm status, `proposal_amount`, ledger và audit:

| Nhánh | Claim / thay đổi | Kết quả cả 3 shape |
| --- | --- | --- |
| Approval hết hạn (T07) | C-007 | `denied`, proposal 35.000, `approval_expired`, không ghi ledger |
| Approval bị thu hồi | A-001 → `revoked` | `denied`, 35.000, `approval_revoked` |
| Mượn approval của claim khác | C-001 trỏ tới A-010 | `denied`, 35.000, `approval_claim_mismatch` |
| Thiếu approval / approval không tồn tại | `approval_id` = NULL hoặc A-404 | `denied`, 35.000, `missing_approval` |
| Đơn đã hoàn đủ (T13) | C-013 | `denied`, 35.000, `order_already_refunded` |
| Claim thứ hai cùng đơn | C-001 rồi C-010 (cùng O-107) | C-010 `denied`, ledger O-107 chỉ có dòng 35.000 của C-001 |
| Trần theo approval (T08) | C-008 | `resolved`, proposal 35.000, ledger 20.000 |
| Hoàn phần chênh (T14) | C-014 | `resolved`, proposal 150.000, ledger 120.000 (host tự trừ 30.000) |
| Clause cũ trong ticket (T06) | C-006 cite `SHIP-LATE-OLD` | `denied`, 0, không gọi host |
| Policy tương lai bị bật `is_current` | POL-2027-03 → `is_current = 1` | `denied`, 0: `effective_date` 2027-03-01 > `as_of` nên bị bỏ |
| Policy cũ có ngày hợp lệ nhưng `is_current = 0` | POL-2025-01 đổi ngày 2026-11-10 | `denied`, 0: vẫn bị bỏ vì không còn hiệu lực |

Ba điểm rút ra:
1. `proposal_amount` khi host từ chối luôn là quote đầy đủ, không phải 0.
2. Quote 0 không bao giờ chạm host, nên không có audit thừa.
3. Shape không tự trừ phần đã hoàn trước đó. Nếu trừ thì T14 sẽ bị trừ hai lần.

Policy hiện hành được lọc ở hai lớp: `lookup_policy` (SQL `is_current = 1 AND effective_date <= as_of`), rồi `compensation.quote` kiểm lại cả hai điều kiện. `get_clause` vẫn trả clause cũ, nên không shape nào dùng nó để tính tiền.

Phần mô tả workflow: chờ thành viên phụ trách bổ sung sau khi tích hợp.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
