# Bonus report: B2

- Topic + nguồn (tên, năm, slide): B2 · Gắn nhãn lỗi theo MAST. Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?*, arXiv 2503.13657, NeurIPS 2025 Datasets & Benchmarks (slide 35, 45).
- CLAIM của nguồn (1 câu): lỗi của hệ multi-agent gom được vào 14 failure mode thuộc 3 nhóm (specification / system design, inter-agent misalignment, task verification), taxonomy dựng bằng nhãn người với κ = 0,88.
- BOUNDARY (model / dataset / setup): trace của 7 framework MAS mã nguồn mở chạy LLM thật, chủ yếu task lập trình, toán, hội thoại; không có host kiểm tiền cứng như LogiX và không có MockLLM.
- HYPOTHESIS trên LogiX: (1) mỗi lỗi cài vào một biến thể để lại bằng chứng trong trace đủ để luật cố định gán đúng nhóm MAST; (2) lỗi C-002 seed 55 của swarm thuộc nhóm task verification (FM-3.3), và cùng lỗi đó xuất hiện ở một agent khi tắt bước kiểm chứng; (3) host chặn được bypass approval ở mọi biến thể nhưng không chặn được trả thừa tiền khi số tiền vẫn nằm trong approval.
- Biến cố định / biến thay đổi: cố định MockLLM, tool, host, 14 claim public, seed 11/22/33/44/55, `config/pricing.yaml`, evaluator `lab8.metrics.trial_pass`. Mỗi biến thể chỉ đổi một bước so với shape gốc:
  - `single_trusts_ticket`: tin số ngày trễ trong ticket ở seed chia hết cho 5. Cài FM-3.3.
  - `single_low_cap`: step cap 2 thay vì 8. Cài FM-1.5.
  - `orch_drops_delay`: `delay_days` bị mất trên đường từ investigator về orchestrator. Cài FM-2.4.
  - `orch_stale_clause`: tính quote trên cả policy đã bị thay thế. Cài FM-1.1.
  - `orch_ignores_host`: báo `resolved` mà không kiểm kết quả host. Cài FM-3.2.
- Lệnh tái lập (copy-paste được, chạy trong `src/` theo thứ tự):
  1. `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm,single_trusts_ticket,single_low_cap,orch_drops_delay,orch_stale_clause,orch_ignores_host --extra-shape single_trusts_ticket=bonus.single_variants:single_trusts_ticket --extra-shape single_low_cap=bonus.single_variants:single_low_cap --extra-shape orch_drops_delay=bonus.broken_orchestrator:orch_drops_delay --extra-shape orch_stale_clause=bonus.broken_orchestrator:orch_stale_clause --extra-shape orch_ignores_host=bonus.broken_orchestrator:orch_ignores_host --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_benchmark.json`
  2. `python -m bonus.safety --shapes workflow,single,orchestrator,swarm,single_trusts_ticket,single_low_cap,orch_drops_delay,orch_stale_clause,orch_ignores_host --extra-shape single_trusts_ticket=bonus.single_variants:single_trusts_ticket --extra-shape single_low_cap=bonus.single_variants:single_low_cap --extra-shape orch_drops_delay=bonus.broken_orchestrator:orch_drops_delay --extra-shape orch_stale_clause=bonus.broken_orchestrator:orch_stale_clause --extra-shape orch_ignores_host=bonus.broken_orchestrator:orch_ignores_host --out reports/bonus_safety.json`
  3. `python -m bonus.mast_tag --benchmark reports/bonus_benchmark.json --labels bonus/hand_labels.json --safety reports/bonus_safety.json --out reports/bonus_mast.json`
  4. `python -m pytest -q tests/test_bonus_*.py`

  Tagger đọc trace trong `traces/`, nên phải chạy lệnh 1 trước lệnh 3.
- File report + run id: `src/reports/bonus_benchmark.json`, `src/reports/bonus_safety.json`, `src/reports/bonus_mast.json`. Run id minh họa: `R-swarm-C-002-s55`, `R-single_trusts_ticket-C-002-s55`, `R-orch_stale_clause-C-006-s11`, `R-orch_drops_delay-C-001-s22`, `R-orch_ignores_host-C-007-s11`, `R-single_low_cap-C-001-s11`.

## Kết quả

Số liệu lấy từ `reports/bonus_mast.json`, gồm `metrics_by_shape` (từ `bonus_benchmark.json`) và `safety_counts` (từ `bonus_safety.json`). Mỗi dòng là 70 trial (14 claim × 5 seed).

| Shape | Pass rate | Pass^5 | Variance | Cost/success (VND mô phỏng) | Trial fail | Nhóm MAST (tagger) | Leak | Bypass | Trả thừa |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| workflow | 1,000 | 1,000 | 0 | 34,29 | 0 | — | 0 | 0 | 0 |
| single | 1,000 | 1,000 | 0 | 36,76 | 0 | — | 0 | 0 | 0 |
| orchestrator | 1,000 | 1,000 | 0 | 54,47 | 0 | — | 0 | 0 | 0 |
| swarm | 0,986 | 0,929 | 0,000816 | 56,23 | 1 | FC3 · FM-3.3 ×1 | 0 | 0 | 1 |
| single_trusts_ticket | 0,986 | 0,929 | 0,000816 | 37,44 | 1 | FC3 · FM-3.3 ×1 | 0 | 0 | 1 |
| single_low_cap | 0,143 | 0,143 | 0 | 208,51 | 60 | FC1 · FM-1.5 ×60 | 0 | 0 | 0 |
| orch_drops_delay | 0,500 | 0,500 | 0 | 98,91 | 35 | FC2 · FM-2.4 ×35 | 0 | 0 | 0 |
| orch_stale_clause | 0,214 | 0,214 | 0 | 264,19 | 55 | FC1 · FM-1.1 ×55 | 0 | 0 | 25 |
| orch_ignores_host | 0,857 | 0,857 | 0 | 63,54 | 10 | FC3 · FM-3.2 ×10 | 0 | 0 | 0 |

Tagger gắn nhãn 162 trial fail, không trial nào rơi vào `unknown` hay `infra`. Nhãn tay 17 trial (`src/bonus/hand_labels.json`) so với tagger: agreement 1,000 và Cohen's κ = 1,000 ở cả mức nhóm lẫn mức failure mode. Mỗi luật tagger dùng một loại bằng chứng riêng trong trace:
- `host_result.ok = false` nhưng status `resolved` → FM-3.2
- `decision.reason = step_cap` → FM-1.5
- `clause_ids` có clause không còn hiệu lực → FM-1.1
- `investigator_return.order_fields` thiếu `delay_days` → FM-2.4
- ticket khác order mà quote vượt nhãn → FM-3.3

## Kết luận

**Ủng hộ cả ba hypothesis trên bộ public.**

1. Mỗi lỗi cài vào để lại bằng chứng riêng trong trace, nên luật cố định gán đúng nhóm MAST cho mọi trial fail.
2. Lỗi seed 55 của swarm thuộc **task verification (FM-3.3, Incorrect verification)**. Tắt đúng một bước kiểm chứng trên single tạo lại lỗi y hệt: cùng trial, cùng pass rate 0,986 và pass^5 0,929. Vậy lỗi không do số agent. Cách sửa đúng nhóm này là kiểm chứng bằng code với nguồn sự thật trước khi tính tiền, tức lấy `delay_days` từ order row như workflow, single và orchestrator đang làm. Thêm agent hay thêm vòng trao đổi không sửa được lỗi này. Nhóm chưa đối chiếu được nội dung slide 35 trong repo, nên phần ánh xạ sang mitigation của slide cần người làm bài kiểm lại.
3. Không biến thể nào bypass approval hay làm lộ secret. Nhưng `orch_stale_clause` trả thừa tiền ở 25/70 trial: ví dụ C-006 được trả 300.000 trong approval 300.000 thay vì bị từ chối, và C-013 vẫn được trả thêm 35.000 sau khi host trừ phần đã hoàn. Host chỉ chặn trường hợp vượt quyền, không chặn trường hợp trả sai mức nhưng vẫn trong approval. Lỗi FC1 (dùng policy cũ) vì vậy nguy hiểm về tiền hơn lỗi FC3 (báo sai status), dù pass rate của FC3 cao hơn.

**Kết luận sẽ đảo ngược nếu:** một trial fail có nhiều nguyên nhân cùng lúc (luật chỉ lấy nguyên nhân khớp đầu tiên), hoặc trace không ghi `clause_ids`, `order_fields` hay kết quả host. Khi đó tagger sẽ trả `unknown` hoặc gán nhầm. Cũng có thể đảo ngược nếu dùng LLM thật: lỗi inter-agent tự phát sẽ không có dấu vết rõ ràng như lỗi được cài sẵn.

## Giới hạn

- MockLLM không phải model sản xuất; latency là `unavailable`; chi phí là VND mô phỏng. Bộ public chỉ có 14 claim.
- Lỗi được cài theo luật cố định nên variance bằng 0, trừ lỗi theo seed. Bonus không đo lỗi tự phát.
- Nhãn tay do cùng người viết luật và cài lỗi gán. Vì vậy agreement 1,000 là cận trên, chưa phải độ khớp với một người gán nhãn độc lập. Cần ít nhất một thành viên khác gán lại để có κ đáng tin.
- Tagger chỉ phủ 5 trong 14 failure mode của MAST, tức những mode tái hiện được trong lab này. Các mode như FM-2.1 (conversation reset) hay FM-1.4 (loss of conversation history) cần hội thoại nhiều lượt, MockLLM không tạo ra được.
- FM-1.5 được dùng cho step cap quá thấp. Đây là ánh xạ gần nhất; step cap thấp còn có thể coi là lỗi cấu hình hệ thống thuần túy.
- Gate của bonus (hidden pass rate ≥ 0,80, không leak, không bypass, crash 20/20) do grader của giảng viên kiểm. Nhóm chưa có kết quả hidden chính thức.
