# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy: lỗi seed 55 của swarm thuộc nhóm MAST nào, và nó do topology nhiều agent hay do thiếu một bước kiểm chứng? |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri và cộng sự (UC Berkeley), *Why Do Multi-Agent LLM Systems Fail?* (MAST), arXiv 2503.13657, NeurIPS 2025 Datasets & Benchmarks track, https://arxiv.org/abs/2503.13657. Loại bằng chứng: phân tích trace có gán nhãn người (empirical taxonomy) cộng dataset MAST-Data, không phải production report |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent gom được vào 14 failure mode thuộc 3 nhóm: system design (specification) issues, inter-agent misalignment, task verification. Taxonomy dựng từ hơn 150 trace, κ giữa người gán nhãn = 0,88. Nhiều lỗi nằm ở thiết kế hệ và kiểm chứng, không chỉ ở năng lực model |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Trace lấy từ 7 framework MAS mã nguồn mở (bản v3: MAST-Data 1600+ trace), chủ yếu task lập trình, toán và hội thoại, chạy với LLM thật. Nhãn mở rộng bằng LLM annotator (o1). Paper không đo hệ có host kiểm tiền cứng như LogiX, không đo MockLLM, và không nói tỉ lệ từng nhóm lỗi trên task tài chính |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Lỗi C-002 seed 55 của swarm là lỗi nhóm **task verification**: số ngày trễ do peer đọc từ ticket không được đối chiếu với `delay_days` của order. Nếu tắt đúng bước kiểm chứng đó trên shape single (một agent), single sẽ fail y như swarm: pass rate 1,000 → ≈ 0,986 (mất 1/70 trial), pass^5 1,000 → ≈ 0,929 (13/14 claim), seed min 1,000 → ≈ 0,929, chỉ seed 55 đổi; cost/success tăng rất nhẹ (cùng số call, chia cho ít success hơn). Nếu lỗi do topology nhiều agent thì single tắt kiểm chứng sẽ vẫn pass 1,000 |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, shape single (cùng thứ tự tool `lookup_order` → `compute_compensation` → final, cùng số model call), host, 14 claim public, seed 11/22/33/44/55, `config/pricing.yaml`, evaluator `lab8.metrics.trial_pass` qua `lab8.benchmark`, mỗi trial một SQLite mới. Biến duy nhất được thay đổi: bước kiểm chứng "order row thắng ticket". Biến thể `src/ablation/single_trusts_ticket.py` ở seed chia hết cho 5 thay `delay_days` bằng số ngày trong ticket khi hai số khác nhau (y hệt `REFERENCE_WEAKNESS` của swarm). Swarm chạy cùng lệnh để đối chiếu |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: trả tiền theo lời ticket (C-002, ticket ghi trễ 5 ngày, order ghi 2 ngày → refund 20.000 thay vì `denied`). Đo bằng pass rate, pass^5, seed min-max và variance theo seed, cost/success, cùng lý do fail trong `trials[].reason`. Approval bypass và leak không đổi (host vẫn chặn, trace không chứa ticket) |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes single,single_trusts_ticket,swarm --extra-shape single_trusts_ticket=ablation.single_trusts_ticket:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_single_ticket_trust.json` (chạy trong `src/`)
- Run id / file report: `src/reports/ablation_single_ticket_trust.json`. Trial fail duy nhất của biến thể: `R-single_trusts_ticket-C-002-s55`; của swarm: `R-swarm-C-002-s55`. Shape single gốc không có trial fail (ví dụ `R-single-C-002-s55` pass).
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.**

  | Shape | pass rate | pass^5 | seed min–max | variance | cost/success (VND mô phỏng) | mean model calls |
  | --- | --- | --- | --- | --- | --- | --- |
  | single (kiểm chứng bật) | 1,000 (70/70) | 1,000 | 1,000–1,000 | 0 | 36,76 | 3,71 |
  | single_trusts_ticket (tắt kiểm chứng) | 0,986 (69/70) | 0,929 | 0,929–1,000 | 0,000816 | 37,44 | 3,71 |
  | swarm (tham chiếu) | 0,986 (69/70) | 0,929 | 0,929–1,000 | 0,000816 | 56,23 | 3,00 |

  Tắt một bước kiểm chứng trên một agent tạo lại **đúng** lỗi của swarm: cùng trial (C-002 seed 55), cùng lý do `status resolved != denied`, cùng pass rate, pass^5 và variance. Trên bộ public, phần pass rate swarm mất so với single được giải thích hoàn toàn bởi lỗi task verification, không phải bởi số agent. Theo MAST, đây là nhóm task verification (kiểm chứng sai hoặc thiếu: chấp nhận dữ kiện của peer mà không đối chiếu nguồn sự thật). Cách sửa đúng nhóm lỗi là kiểm chứng bằng code trước khi tính tiền (lấy `delay_days` từ order row, như workflow và single đang làm), không phải thêm agent hay thêm vòng trao đổi. Cost của swarm cao hơn (56,23 so với 36,76) đến từ peer chatter và tool call, độc lập với lỗi này. Số này đã tính bước `issue_refund` như các shape khác.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi được cài theo luật cố định (seed chia hết cho 5), nên variance ở đây là variance do thiết kế, không phải do model ngẫu nhiên. Bộ public chỉ có một claim mà ticket nói khác order (C-002), nên 1/70 là cỡ mẫu rất nhỏ. Bộ hidden có thêm ticket nói dối và homoglyph, nên tỉ lệ có thể khác. Kết luận "lỗi do verification chứ không do topology" chỉ đúng cho lỗi này trên task này. Với LLM thật, swarm còn có thể gặp lỗi nhóm inter-agent misalignment mà MockLLM không tái hiện được. Metric `steps` đếm số event trong trace, nên phụ thuộc cách mỗi shape ghi trace; đừng so steps giữa các shape như số bước suy luận.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
