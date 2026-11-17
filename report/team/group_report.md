# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: nhóm BLG
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `1869bd0`

## 2. Mục tiêu và cách tiếp cận

Bài toán là xử lý claim hoàn tiền vận chuyển của LogiX-VN theo bốn kiến trúc (workflow, single, orchestrator, swarm) với cùng chữ ký `run_claim`. Nhóm phải chứng minh bằng số đo chứ không chọn theo cảm tính: kiến trúc nào ít tự chủ nhất mà vẫn đạt pass rate yêu cầu thì được chọn. Ranh giới được giữ cố định: code tính tiền bằng `compute_compensation`, host (`durability.issue_refund`) kiểm approval, trần theo đơn và idempotency, còn model (MockLLM) chỉ soạn chữ.

Việc chia theo ba thành viên, mỗi người một shape cùng một mảng kiểm tra:
- Thành viên 1: workflow, crash và idempotency. Được merge sớm để làm khung cho hai người còn lại.
- Thành viên 2: single (ReAct), approval và policy, research card.
- Thành viên 3: orchestrator, trace an toàn, benchmark và ADR.

Thứ tự thực hiện: workflow trước; single và orchestrator song song, sau đó rà lại cả ba shape trên các trường hợp chung (T11, T12, approval, trace). Bộ test công khai (`src/tests/test_public_matrix.py`, 14 claim × 4 shape) và crash suite được dùng làm thước đo trung gian. Swarm có sẵn làm đối chứng.

## 3. Giải pháp

Ba shape nhóm viết (workflow, single, orchestrator) đều đi qua host để ghi tiền và đều trả `RunResult` qua `finish`. Khác nhau ở chỗ ai quyết định bước đọc dữ liệu: workflow dùng code cố định, single dùng vòng ReAct có tool đọc, orchestrator dùng investigator nhận handoff đã lọc. Ranh giới code / model tham khảo [docs/architecture.md](../../docs/architecture.md).

### Shape A — Workflow (code cố định)

Workflow không gọi model. Các bước theo thứ tự:
1. Đọc claim bằng `get_claim_view`, không `SELECT *`. Claim không tồn tại thì trả `failed`, không ghi ledger.
2. Thiếu `order_id` thì trả `needs_info`. Không lấy mã đơn từ chữ trong ticket.
3. `lookup_order(order_id, principal_id)`. Đơn không visible (không tồn tại hoặc khác principal) thì trả `escalated`.
4. `compute_compensation` trên order row. Số ngày trễ trong ticket bị bỏ qua.
5. Quote bằng 0 thì trả `denied` và không gọi host.
6. Quote dương: gọi `durability.issue_refund` với quote đầy đủ và `crash_at`, không bắt `InjectedCrash`. Host từ chối thì `denied` (conflict thì `failed`), host chấp nhận thì `resolved`.

Trace ghi các event `claim_lookup`, `order_lookup`, `quote`, `host_result`. Workflow không ghi ticket, order row hay claim row. Hàm `finish` tự lấy refund và audit từ ledger, nên `refund_effects` và `committed_audit_count` không do shape khai.

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

## 4. Kết quả

Bảng dưới lấy từ `src/reports/benchmark.json`: 14 claim public × 5 seed (11, 22, 33, 44, 55), mỗi trial một SQLite riêng. Số trial đúng là 70 mỗi shape.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1,000 | 1,000 | 1,000–1,000 | 0 | 34,29 | 3,50 / 4 |
| single | 1,000 | 1,000 | 1,000–1,000 | 0 | 36,76 | 5,36 / 6 |
| orchestrator | 1,000 | 1,000 | 1,000–1,000 | 0 | 54,47 | 4,36 / 5 |
| swarm (đối chứng) | 0,986 | 0,929 | 0,929–1,000 | 0,000816 | 56,23 | 2,80 / 3 |

Swarm sai đúng một trial: C-002 seed 55, tin số ngày trễ trong ticket (5 ngày) thay vì order (2 ngày), nên trả 20.000 VND thay vì `denied`. Ba shape nhóm viết đều pass trial này.

Crash safety: `src/reports/crash.json` đạt 20/20.

Tự kiểm trên bộ hidden không nhãn (`student_drop/`, 40 claim × 5 seed, chạy cho workflow, single, orchestrator): mỗi shape 200 trial, không có trial lỗi và không có cờ rò rỉ. Phân bố trạng thái giống nhau ở cả ba shape: 90 `resolved`, 95 `denied`, 10 `escalated`, 5 `needs_info`. Bộ này không có nhãn nên không tính được pass rate. Kết quả nằm ở `src/reports/hidden_selfcheck.json`, lúc viết báo cáo chưa được commit.

Kiểm thử sau tích hợp trên `main`: bộ mặc định 117 passed; ma trận student 248 passed (workflow, single, orchestrator mỗi shape 62/62).

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Lọc test theo shape.** `pytest -k single` khớp cả tên hàm `test_public_single_run_cases` của mọi shape, nên ra 242 test thay vì 62. Cách xử lý: khi báo cáo số test của một shape, đếm theo tham số shape trong tên test, không dùng `-k` đơn thuần.
- **Lỗi swarm không rõ nguyên nhân.** Nhóm cần biết lỗi C-002 seed 55 thuộc nhóm nào. Thành viên 2 làm một ablation một biến: tắt bước đối chiếu ticket với order trên shape single. Lỗi tái hiện đúng trial đó, với cùng lý do `status resolved != denied`. Kết quả: `src/reports/ablation_single_ticket_trust.json` và research card R2.
- **Chi phí không đồng nhất giữa các shape.** Khi đối chiếu code, workflow và single cộng một tool call cho `issue_refund`, còn orchestrator và swarm thì không. Nhóm đã thống nhất theo cách của workflow và single: orchestrator và swarm cũng đếm bước này, rồi chạy lại toàn bộ benchmark và bằng chứng liên quan.
- **Repo đổi tên.** GitHub báo repo đã chuyển sang tên `K5-L3B-DAY08-BLG-FromWorkflowsToAgents`. Có một lần `fetch` từ GitHub lỗi kết nối, lần sau chạy được. Tên repo hiện không khớp `SUBMISSION.md` (xem mục 7).
- **Test ánh xạ sai claim.** Thành viên 3 ghi nhận trong báo cáo cá nhân rằng hai mã claim ban đầu bị gán nhầm tình huống; đã đối chiếu fixture public, sửa mã test và chạy lại.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp nằm trong `TEAM.md` (bảng đóng góp, theo commit và test) và trong báo cáo cá nhân của từng người:
- Thành viên 1 (Nguyễn Tấn Dũng, 2A202603734): workflow, crash và idempotency; `test_workflow_durability.py`; crash suite 20/20.
- Thành viên 2 (Lê Thanh Hà, 2A202603901): shape single, `test_single_react.py`, `test_approval_policy_branches.py`, research card và ablation R2.
- Thành viên 3 (Lê Huy Anh, 2A202603786): orchestrator, `test_orchestrator_safety.py`, benchmark, crash evidence và ADR.

## 7. Hạn chế và hướng cải thiện

- MockLLM không phải model sản xuất; chi phí là VND mô phỏng và latency là `unavailable`. Không kết luận được về tốc độ hay chi phí của LLM thật.
- Chi phí là mô phỏng theo `config/pricing.yaml` và đã thống nhất cách đếm giữa các shape. Với swarm, sửa cách đếm là chỉnh file tham chiếu do giảng viên cung cấp; nhóm ghi lại việc này để người đọc biết số swarm không còn đúng với bản gốc.
- **Steps là số event trace**, không phải số bước suy luận. Cách ghi trace của mỗi shape ảnh hưởng đến metric này.
- Bộ public chỉ có 14 claim, trong đó chỉ C-002 có ticket nói khác order. Swarm có điểm yếu được cài theo seed, nên variance ở đây là do thiết kế, không do model ngẫu nhiên. Cỡ mẫu nhỏ, chưa đủ để khẳng định xu hướng tổng quát.
- **Chưa có kết quả hidden chính thức.** Pass rate hidden, leak count hidden và approval bypass count hidden do grader của giảng viên chấm. Không khai các số này trong báo cáo.
- **Tên repo và lớp.** `SUBMISSION.md` yêu cầu tên dạng `K5-L3A-DAY08-TenNhom-...`, còn repo hiện là `K5-L3B-DAY08-BLG-...`. Nhóm cần quyết định trước khi nộp.
- Điều kiện làm kết luận thay đổi: nếu grader hidden cho workflow dưới 0,75, hoặc chi phí được tính lại theo quy ước khác làm thứ hạng cost đổi, quyết định chọn workflow phải được xem lại.

## 8. Tài liệu tham khảo

- MAST: Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?*, arXiv 2503.13657 (NeurIPS 2025 Datasets & Benchmarks). https://arxiv.org/abs/2503.13657 — dùng để phân loại lỗi trong research card R2. Nhóm đối chiếu tóm tắt trên trang arXiv, chưa đọc toàn văn.
- Tài liệu của starter: `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `docs/architecture.md`.
- Các nguồn còn lại trong research card (R1, R3, R4) chưa được nhóm đối chiếu trong báo cáo này.
