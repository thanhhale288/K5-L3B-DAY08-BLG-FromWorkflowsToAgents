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

Phần mô tả workflow và single: chờ thành viên phụ trách bổ sung sau khi tích hợp.

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
