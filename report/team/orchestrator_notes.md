# Phần việc người 3 — Orchestrator và bảo mật

Đây là ghi chú bàn giao kỹ thuật, không thay báo cáo cá nhân theo MSSV hoặc ADR cuối cùng.

## Triển khai

`src/lab8/shapes/orchestrator.py` đọc claim qua `get_claim_view`. Claim không tồn tại trả `failed`; thiếu mã đơn trả `needs_info`. Orchestrator tạo `make_handoff` với facts rỗng và ba tool đọc theo thứ tự: `lookup_order`, `lookup_policy`, `compute_compensation`. Worker chạy qua `run_readonly_investigators`, dùng principal của claim để giới hạn quyền xem đơn.

MockLLM nhận một yêu cầu lập kế hoạch cố định và soạn phản hồi từ status/quote. Code cố định quyền tool, tính tiền và quyết định ghi; model không tạo approval hoặc chọn số tiền. Nếu order không visible thì trả `escalated`; quote bằng 0 thì `denied`. Quote dương được truyền nguyên vẹn vào `issue_refund`, để host kiểm approval và tự trừ khoản hoàn trước đó theo đơn. Conflict trả `failed`; host từ chối trả `denied`; host chấp nhận trả `resolved`.

Mọi nhánh trả bình thường qua `finish`. Connection luôn đóng trong `finally`. `crash_at` được chuyển nguyên cho host và `InjectedCrash` được truyền ra ngoài để runner mô phỏng crash/resume.

## Handoff và trace

Handoff dùng allowlist của host; worker không nhận registry ghi tiền. Không đưa ticket, secret, raw header hoặc parent context vào facts. Trace ghi các event `handoff`, `investigator` (chỉ trạng thái visible), `quote` (amount và reason), `host` (ok và reason), `decision` (status, proposal và reason). Nhánh trả sớm vẫn có event `decision` và trace mới đúng run ID.

Trace không ghi order row, claim row, ticket, số điện thoại, địa chỉ, tên hàng hoặc ghi chú nội bộ. `safe_dump` chỉ sao chép handoff đã sanitize, không phải hàm tự lọc dữ liệu tùy ý. Khi crash xảy ra, exception truyền ra ngoài; lần resume ghi trace của lần chạy mới.

## Test và số liệu đã chạy

Chạy trong `src/`, dùng Python 3.13.2 và môi trường `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= -k orchestrator
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/orchestrator_public.json
```

- Orchestrator student matrix: **62 passed**.
- Bộ mặc định sau khi thêm test: **65 passed, 248 deselected**.
- Test mới: `src/tests/test_orchestrator_safety.py` (11 trường hợp): chèn secret/PII vào cả ticket và database; kiểm envelope thực tế tới investigator; trace ở các nhánh trả; crash/resume/retry tại ba crash window; approval mượn từ claim khác phải bị host từ chối và ghi audit.
- Kết quả benchmark dưới đây lấy từ `src/reports/orchestrator_public.json`, do công cụ sinh ra, không chỉnh tay.

| Metric | Orchestrator | Swarm reference |
| --- | ---: | ---: |
| Trial đúng / tổng | 70/70 | 69/70 |
| Pass rate | 1.000000 | 0.985714 |
| Pass^5 | 1.000000 | 0.928571 |
| Seed min–max | 1.000000–1.000000 | 0.928571–1.000000 |
| Seed variance | 0 | 0.000816327 |
| Cost/success (VND mô phỏng) | 54.465714 | 56.233623 |
| Mean steps | 4.357143 | 2.800000 |
| P95 steps | 5 | 3 |

Ví dụ run ID: `R-orchestrator-C-001-s11`. Swarm sai tại C-002 seed 55 như điểm yếu có chủ đích của đề bài. Bộ test student có kiểm retry/crash; benchmark ở trên chủ yếu đo từng lần chạy, không thay cho test crash.

## Giới hạn và phần còn lại

Chưa kết luận orchestrator là shape tốt nhất: workflow và single vẫn là stub tại thời điểm đo. MockLLM không phải model sản xuất; chi phí là mô phỏng, latency `unavailable`. Steps là số event trace, nên cách ghi trace khác nhau ảnh hưởng metric này. Public pass không chứng minh hidden pass. Chưa có student_drop để tự kiểm hidden.

Khi tích hợp code của hai thành viên còn lại:

1. Rà trace của cả ba shape; chạy bộ student đầy đủ và bộ mặc định.
2. Chạy benchmark chính thức đủ bốn shape vào `reports/benchmark.json` và crash suite vào `reports/crash.json` theo SUBMISSION.md.
3. Tự kiểm student_drop khi được giảng viên phát. Bộ không nhãn không cung cấp pass rate hidden.
4. Cùng nhóm chọn shape theo số đo, điền ADR và cập nhật bảng kết quả báo cáo nhóm. Sau khi commit code/bằng chứng mới lấy hash thật để điền ADR; không dùng hash cũ cho code chưa commit.
5. Điền thông tin cá nhân thật, tạo báo cáo `MSSV_HoTen.md`, ghi việc dùng Codex để hỗ trợ code/test và cách đã kiểm chứng; đưa commit/test cho người phụ trách TEAM.md.
6. Chạy `python -m lab8.check_submission` và sửa hết FAIL trước khi push/nộp.

Nguồn tham khảo triển khai: docstring orchestrator, `runtime.py`, `handoff.py`, `shapes/common.py`, `swarm_reference.py`, `docs/contracts.md`, `docs/business_rules.md` trong starter. Không sử dụng khối `REFERENCE_WEAKNESS` của swarm.
