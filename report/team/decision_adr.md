# Decision record

- Shape chọn: workflow
- Commit hash: b3e7b7769562d84f12baecd27153c1486acb6114
- Run id dẫn chứng: R-workflow-C-001-s11; R-workflow-C-002-s55; R-workflow-C-014-s11 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000000 / 1.000000 / 1.000000–1.000000 / 0.000000 (70/70 trial public, 14 claim × 5 seed)
- Cost per success (mô phỏng, VND): 34.285714 (cách tính budget hiện tại; xem giới hạn bên dưới)
- Crash safety: 20/20 (src/reports/crash.json); workflow qua T11, T12 và test retry/crash riêng
- Secret leak / approval bypass: Không phát hiện leak chuỗi cấm trên 70 trial public của workflow; các test approval/policy và public matrix đều pass. Chưa có safety counts của grader hidden; không coi kết quả public là bằng chứng an toàn tuyệt đối.

## Vì sao shape này

Chọn workflow vì quy trình claims hiện tại có luật rõ ràng và các bước phụ thuộc tuần tự: đọc claim → đọc order đúng principal → tính entitlement theo policy → gọi host. Trên cùng 14 claim, 5 seed 11/22/33/44/55, as_of 2026-11-15, MockLLM, bảng giá và evaluator, workflow đạt độ đúng bằng single và orchestrator mà không cần gọi model. Đây là kiến trúc ít tự chủ nhất đáp ứng bộ public và các bài kiểm thử hiện có. Host vẫn là nơi kiểm approval, trần theo đơn và idempotency; shape truyền quote đầy đủ, không tự trừ tiền đã hoàn. Lựa chọn sẽ được kiểm tra lại trên hidden khi có kết quả chính thức.

| Shape | Trial đúng | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 70/70 | 1.000000 | 1.000000 | 1–1 | 0 | 34.285714 | 3.50 / 4 |
| single | 70/70 | 1.000000 | 1.000000 | 1–1 | 0 | 36.760000 | 5.36 / 6 |
| orchestrator | 70/70 | 1.000000 | 1.000000 | 1–1 | 0 | 54.465714 | 4.36 / 5 |
| swarm | 69/70 | 0.985714 | 0.928571 | 0.928571–1 | 0.000816327 | 56.233623 | 2.80 / 3 |

Số liệu lấy từ `src/reports/benchmark.json` đã commit cùng source tại hash trên. Báo cáo crash nằm trong cùng commit. Kiểm thử sau tích hợp: bộ mặc định 117 passed; student matrix 248 passed, trong đó workflow 62/62. Student tests của swarm có trường hợp khẳng định lỗi cố ý phải xuất hiện, nên test xanh không đồng nghĩa benchmark swarm đạt 100%.

## Có đáng đổi lấy multi-agent không

Trong setup này, chưa có bằng chứng cần đổi workflow sang multi-agent: orchestrator không tăng pass rate hoặc pass^5, còn swarm sai C-002 seed 55 khi tin ticket thay vì order. Tăng số agent không tự sửa được ranh giới dữ liệu đó. Research card R2 và ablation của thành viên 2 (`src/reports/bonus_benchmark.json`) tái hiện cùng lỗi trên single khi bỏ bước đối chiếu order, cho thấy lỗi verification có thể xảy ra cả ở một agent.

Nhóm sẽ xem xét đổi lựa chọn nếu task có các phần điều tra độc lập cần chạy song song, dữ liệu phi cấu trúc thực sự cần model diễn giải, hoặc benchmark mở rộng/hidden cho thấy workflow không đáp ứng yêu cầu trong khi một shape khác cải thiện độ đúng đáng kể. Điều kiện là cách đo phải được chuẩn hóa, chi phí chấp nhận được, không bypass approval, không lộ dữ liệu và crash vẫn an toàn. Nếu workflow không đạt ngưỡng hidden 0.75, quyết định này phải được đánh giá lại; public 1.0 không thay thế ngưỡng hidden.

## Trace và bằng chứng

Workflow ghi `claim_lookup` (found), `order_lookup` (visible, reason, order_id), `quote` (kết quả tính tiền), `host_result` (ok, reason) và `decision` ở nhánh thiếu mã đơn. Mọi nhánh trả bình thường dùng `finish`, tạo trace mới có run_id khớp kết quả, lấy refund/audit từ ledger thay vì tự khai.

Không ghi claim/order row thô, ticket, parent_secret, raw header, SĐT, địa chỉ, ghi chú nội bộ hoặc tên hàng. Orchestrator dùng handoff allowlist và investigator chỉ đọc; test `src/tests/test_orchestrator_safety.py` kiểm cả envelope thực tế và dữ liệu nhạy cảm được chèn vào ticket/database. Test approval/policy của thành viên 2 chạy trên cả ba shape.

Grader quét trace và file cùng thư mục có tiền tố run_id. Code shape hiện không tạo debug dump ngoài vùng này; việc rà source là bằng chứng bổ sung, không thay thế leak scan. Không coi log ngoài vùng scanner là an toàn vì scanner không thấy. Khi thêm output mới cần đưa nó vào phạm vi kiểm tra, rà stdout/stderr và chạy lại test.

Crash suite 20/20 kiểm host/swarm. Độ bền của workflow được kiểm thêm bằng T11, T12 và `src/tests/test_workflow_durability.py`: retry hoặc resume sau crash vẫn chỉ một refund, một audit committed. Không suy ra shape tự an toàn chỉ từ crash suite có sẵn.

## Giới hạn

- MockLLM không phải model sản xuất; chi phí là VND mô phỏng, latency `unavailable`. Không kết luận về tốc độ thực hoặc hiệu quả LLM thật.
- Budget đã thống nhất giữa các shape: mỗi lần gọi `issue_refund` được đếm là một tool call, ở cả workflow, single, orchestrator và swarm. Trước đó orchestrator và swarm không đếm bước này, nên cost thấp hơn thực tế; số liệu trong bảng đã được chạy lại sau khi sửa. Vẫn là chi phí mô phỏng từ `config/pricing.yaml`, không phải hóa đơn API.
- Lần sửa budget chỉ thay đổi cost/success của orchestrator và swarm (từ 48,04 và 49,57 lên 54,47 và 56,23). Pass rate, variance và thứ hạng cost không đổi.
- Steps là số event trace; cách ghi trace khác nhau ảnh hưởng mean/p95, không phải số bước suy luận hay thời gian thực.
- Public chỉ có 14 claim; swarm có điểm yếu được cài theo seed. Các shape còn khác nhau về prompt, số lần đọc và cách điều phối, nên không quy mọi chênh lệch cho số agent.
- Chưa có kết quả grader hidden hoặc student_drop self-check. Không tự khai pass rate hidden, leak count hidden hoặc approval bypass count hidden bằng 0.

## Lệnh tái lập

Chạy trong `src/`, dùng Python 3.11–3.13 và dependencies trong requirements.txt:

```powershell
python -m pytest -q
python -m pytest -q -m student -o addopts=
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.crash_test --count 20 --out reports/crash.json
```

Hash ở đầu là commit chứa source và report làm bằng chứng, trước commit bổ sung ADR này. Nếu code hoặc cách tính budget thay đổi thì phải chạy lại bằng chứng và cập nhật hash; không sửa JSON để giữ số cũ.
