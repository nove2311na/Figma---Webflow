# Implementation Plan — Hoàn thiện flow Figma → HTML → Webflow

## 0. Mục tiêu cuối

Đưa repo từ trạng thái “có architecture nhưng còn blocker runtime” sang trạng thái:

```text
1. Repo sạch path sai, không còn local secret/config bị track.
2. Script chạy được từ repo root và từ bất kỳ working directory nào.
3. Design system sync chạy deterministic:
   Client-First CSS baseline → Figma contract → Webflow contract.
4. HTML architect chạy deterministic:
   raw Figma HTML → validated semantic HTML → Client-First classes.
5. Webflow write có preview/approval/audit, không ghi thẳng bừa.
6. Có fixture E2E để test flow từ đầu tới cuối.
```

---

# Phase 1 — Fix blocker repo/runtime trước

## Mục tiêu

Sửa các lỗi khiến pipeline “chạy là fail” trước khi đụng vào logic Figma/Webflow sâu.

## Task 1. Remove `.claude/settings.local.json` khỏi repo

### Việc cần làm

1. Remove `.claude/settings.local.json` khỏi Git tracking.
2. Add `.claude/settings.local.json` vào `.gitignore`.
3. Tạo `.claude/settings.example.json`.
4. Scan secret/token/path local còn sót.
5. Rotate/revoke token nếu token thật từng bị commit.

### Agent/dev tự làm được

Agent/dev có thể tự:

```text
- git rm --cached .claude/settings.local.json
- update .gitignore
- tạo settings.example.json
- update README/CLAUDE.md về local setup
- scan token bằng grep
```

### Bạn cần tham gia mức độ: CAO

### Bạn tham gia để làm gì?

Bạn cần tham gia vì đây là phần liên quan tới **security và credentials**.

Bạn cần:

```text
1. Xác nhận token trong settings.local.json là token thật hay placeholder.
2. Nếu là token thật, vào provider tương ứng để revoke/rotate.
3. Xác nhận sau này repo sẽ dùng cách nào để lưu local secret:
   - file local ignored
   - environment variable
   - secret manager
```

### Bạn tham gia như nào?

Bạn chỉ cần trả lời/ra quyết định:

```text
- Token đó có phải token thật không?
- Có cần rotate ngay không?
- Muốn dùng `.claude/settings.example.json` hay `.env.example` làm template local setup?
```

### Output cần có

```text
.gitignore
.claude/settings.example.json
README.md hoặc CLAUDE.md update
settings.local.json không còn tracked
```

---

## Task 2. Fix repo-root resolution trong shared scripts

### Việc cần làm

Sửa các script:

```text
.claude/skills/_shared/scripts/validate_artifacts.py
.claude/skills/_shared/scripts/utils.py
.claude/skills/_shared/scripts/resolve_client_first.py
```

Các script này phải tìm đúng repo root bằng helper kiểu:

```python
def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".claude").exists() and (parent / "knowledge-base").exists():
            return parent
    raise RuntimeError("Could not locate repo root")
```

### Agent/dev tự làm được

Agent/dev có thể tự sửa code và chạy smoke test.

### Bạn cần tham gia mức độ: THẤP

### Bạn tham gia để làm gì?

Bạn chỉ cần review nếu agent phát hiện repo root marker không chắc chắn.

Ví dụ repo hiện có thể dùng marker:

```text
.claude/
knowledge-base/
agentic/
source-css/
```

### Bạn tham gia như nào?

Bạn chọn marker chính để detect repo root:

```text
Option A: .claude + knowledge-base
Option B: .claude + agentic
Option C: .claude + source-css
```

Mình khuyên:

```text
.claude + knowledge-base + source-css
```

vì sát với repo hiện tại.

### Output cần có

```text
3 scripts resolve đúng repo root
Không còn path runtime kiểu .claude/knowledge-base hoặc .claude/agentic
```

---

## Task 3. Fix `map_variables.py` CLI mismatch

### Việc cần làm

Hiện orchestrator gọi:

```bash
map_variables.py --workspace <ws>
```

nhưng script lại yêu cầu nhiều args như:

```text
--input
--output
--mapping
--report
--baseline
```

Cần chọn một strategy.

### Option đề xuất

Cho `map_variables.py` support default thông minh:

```bash
python .claude/skills/design-system-sync/scripts/map_variables.py \
  --workspace <workspace-name> \
  --strict
```

Script tự resolve:

```text
input    = workspace/<ws>/design-system/figma-design-system.json
baseline = workspace/<ws>/design-system/client-first-baseline-contract.json
mapping  = .claude/skills/design-system-sync/references/figma-webflow-mapping.md
output   = workspace/<ws>/design-system/webflow-design-system.json
report   = workspace/<ws>/design-system/validations/mapping-report.json
```

### Agent/dev tự làm được

Agent/dev tự sửa script, SKILL.md và orchestrator.

### Bạn cần tham gia mức độ: TRUNG BÌNH

### Bạn tham gia để làm gì?

Bạn cần quyết định **baseline source** và **fallback policy**.

Cụ thể:

```text
1. Nếu workspace baseline chưa tồn tại, script nên fail hay fallback sang template?
2. Mapping file nên luôn lấy từ skill reference hay copy vào workspace?
3. Có cho phép project extension ngoài Client-First baseline không?
```

### Khuyến nghị của mình

```text
1. Nếu thiếu workspace baseline → fail rõ CLIENT_FIRST_BASELINE_NOT_FOUND.
2. Mapping canonical nằm ở .claude/skills/design-system-sync/references/figma-webflow-mapping.md.
3. Chỉ cho project extension nếu có field projectExtension: true và ghi warning.
```

### Bạn tham gia như nào?

Bạn confirm 3 policy trên. Agent/dev sau đó tự implement.

### Output cần có

```text
map_variables.py --workspace <ws> --strict chạy được
orchestrator không gọi thiếu args
SKILL.md document command đúng
mapping report sinh ra rõ ràng
```

---

## Task 4. Fix orchestrator CSS input path

### Việc cần làm

Hiện CSS thật ở:

```text
source-css/client-first-v2-2.webflow.css
```

nhưng orchestrator đang trỏ:

```text
workspace/<ws>/source-css/client-first-v2-2.webflow.css
```

Cần chọn:

```text
Option A: Orchestrator đọc trực tiếp từ source-css/
Option B: Copy CSS vào workspace trước khi chạy
```

### Agent/dev tự làm được

Agent/dev tự sửa orchestrator.

### Bạn cần tham gia mức độ: TRUNG BÌNH

### Bạn tham gia để làm gì?

Bạn cần quyết định **mô hình source CSS**.

### Khuyến nghị

Dùng Option A:

```text
source-css/ là baseline source folder của repo.
workspace/ chỉ chứa output runtime.
```

Lý do:

```text
- Ít copy file thừa
- Dễ kiểm soát baseline version
- Workspace chỉ chứa artifact theo project/run
```

### Bạn tham gia như nào?

Bạn chỉ cần confirm:

```text
Dùng source-css/ làm canonical baseline source.
```

### Output cần có

```text
orchestrate.py input-css trỏ đúng source-css/client-first-v2-2.webflow.css
extract_client_first_baseline.py chạy được từ orchestrator
```

---

## Task 5. Fix `validate_figma_extraction.py` mapping default

### Việc cần làm

Default mapping path không nên là:

```text
workspace/<ws>/design-system/figma-webflow-mapping.md
```

nếu không có bước copy.

Nên dùng:

```text
.claude/skills/design-system-sync/references/figma-webflow-mapping.md
```

### Agent/dev tự làm được

Có thể tự sửa.

### Bạn cần tham gia mức độ: THẤP

### Bạn tham gia để làm gì?

Chỉ cần confirm mapping canonical nằm trong skill references.

### Output cần có

```text
validate_figma_extraction.py không fail vì thiếu workspace mapping
```

---

# Phase 2 — Làm pipeline design-system sync chạy ổn

## Mục tiêu

Biến flow design-system thành chuỗi deterministic:

```text
Client-First CSS baseline
→ client-first-baseline-contract.json
→ figma-design-system.json
→ validate
→ webflow-design-system.json
→ mapping-report.json
```

---

## Task 6. Hoàn thiện Client-First baseline extraction

### Việc cần làm

Chạy script:

```bash
python .claude/skills/design-system-sync/scripts/extract_client_first_baseline.py \
  --input-css source-css/client-first-v2-2.webflow.css \
  --output-contract workspace/test/design-system/client-first-baseline-contract.json \
  --report workspace/test/design-system/validations/client-first-extraction-report.json \
  --strict
```

Script phải:

```text
- Include Client-First variables/classes
- Exclude Webflow native .w-* classes
- Exclude reset/native element selectors
- Output baseline contract
- Output extraction report
```

### Agent/dev tự làm được

Agent/dev có thể tự chạy và sửa script nếu report fail.

### Bạn cần tham gia mức độ: CAO

### Bạn tham gia để làm gì?

Bạn cần review **baseline contract có đúng với thư viện FS Client-First mà bạn muốn clone sang Figma không**.

Vì đây là điểm quyết định kiến trúc Figma library.

Bạn cần check:

```text
1. Có đủ variables chưa?
2. Có class nào đáng ra là Client-First nhưng bị exclude không?
3. Có class Webflow native .w-* nào bị include nhầm không?
4. Có nhóm class nào bạn không muốn clone sang Figma không?
5. Có project extension nào muốn cho phép không?
```

### Bạn tham gia như nào?

Agent/dev xuất:

```text
client-first-baseline-contract.json
client-first-extraction-report.json
client-first-extraction-report.md
```

Bạn review bằng checklist:

```text
[ ] Variables đúng nhóm: theme, typography, layout, sizes, brand, neutral, font-family, font-weight, focus
[ ] Classes đúng nhóm: heading-style, text-size, text-weight, max-width, margin, padding, container, button, form...
[ ] Không có .w-button, .w-input, .w-nav, .w-tabs...
[ ] Không có native h1/body/p/img styles
[ ] Không thiếu class quan trọng mà Figma cần clone
```

### Output cần có

```text
workspace/<ws>/design-system/client-first-baseline-contract.json
workspace/<ws>/design-system/validations/client-first-extraction-report.json
```

---

## Task 7. Chốt Figma design-system extraction strategy

### Việc cần làm

Cần quyết định cách lấy full Figma variables/styles.

Không nên chỉ dựa vào `get_variable_defs` nếu nó chỉ selection-scoped.

### Options

```text
Option A: Figma REST Variables API
- Lấy full local/published variables.
- Phù hợp cho design-system sync.

Option B: Figma MCP/tool wrapper có full variable library extraction
- Chỉ dùng nếu tool thật sự support full file/library scope.

Option C: Manual exported JSON từ Figma
- Dùng tạm để test pipeline.
```

### Agent/dev tự làm được

Agent/dev có thể implement wrapper nếu bạn chọn option.

### Bạn cần tham gia mức độ: RẤT CAO

### Bạn tham gia để làm gì?

Bạn cần chọn **tool/source thật** để lấy Figma design-system.

Đây là phần không thể tự đoán vì phụ thuộc setup Figma/MCP/token của bạn.

Bạn cần xác nhận:

```text
1. Có dùng Figma REST API được không?
2. Có Figma file key không?
3. Token Figma lưu ở đâu?
4. Figma variables/styles đang local trong file hay published library?
5. Có mode/light-dark/responsive variable không?
```

### Bạn tham gia như nào?

Bạn cung cấp/confirm:

```text
- Figma file key hoặc workflow lấy file key
- Cách auth Figma
- Tool MCP/API được phép dùng
- Format output mong muốn
```

### Output cần có

```text
workspace/<ws>/design-system/figma-design-system.json
```

Contract phải có:

```text
variables
styles
type
value
resolvedValue
unit
mode
collection
aliasOf nếu có
```

---

## Task 8. Validate Figma contract against Client-First baseline

### Việc cần làm

Sau khi có `figma-design-system.json`, chạy:

```bash
python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py \
  --workspace <ws> \
  --baseline workspace/<ws>/design-system/client-first-baseline-contract.json
```

Validation phải check:

```text
- required variable/style tồn tại
- type đúng
- unit hợp lệ
- no placeholder [VALUE]
- mapping target tồn tại trong Client-First baseline
- không map sang .w-* hoặc native selector
```

### Agent/dev tự làm được

Có thể tự chạy và fix script.

### Bạn cần tham gia mức độ: CAO

### Bạn tham gia để làm gì?

Bạn cần xử lý những lỗi thuộc về **Figma library setup**.

Ví dụ report báo thiếu:

```text
Theme / Background / Primary
Typography / H1 / H1 Font Size
Heading Style / H1
```

Agent/dev không thể tự tạo/sửa trong Figma nếu không có access hoặc quyết định design.

### Bạn tham gia như nào?

Bạn mở Figma và:

```text
1. Tạo/sửa variable/style còn thiếu.
2. Đổi tên variable/style theo mapping contract.
3. Chốt value đúng nếu value sai.
4. Rerun extraction.
```

### Output cần có

```text
validation_report.json
validation_report.md
status = passed hoặc passed_with_warnings
```

---

## Task 9. Map Figma contract → Webflow contract

### Việc cần làm

Chạy:

```bash
python .claude/skills/design-system-sync/scripts/map_variables.py \
  --workspace <ws> \
  --strict
```

Output:

```text
workspace/<ws>/design-system/webflow-design-system.json
workspace/<ws>/design-system/validations/mapping-report.json
```

### Agent/dev tự làm được

Script chạy và tạo report.

### Bạn cần tham gia mức độ: TRUNG BÌNH

### Bạn tham gia để làm gì?

Bạn cần review các case:

```text
- unmapped variable/style
- project extension
- type mismatch
- value mismatch nhưng intentional
```

### Bạn tham gia như nào?

Bạn review `mapping-report.md` và quyết định:

```text
1. Add mapping mới?
2. Rename Figma variable/style?
3. Cho phép project extension?
4. Giữ warning hay biến thành error?
```

### Output cần có

```text
webflow-design-system.json hợp lệ
mapping-report.json không có error
```

---

# Phase 3 — Làm HTML Architect chạy ổn

## Mục tiêu

Biến raw Figma HTML thành final Webflow-ready HTML:

```text
raw-figma.html
→ validate naming
→ semantic rewrite
→ class matching
→ accessibility warnings
→ final-webflow.html
```

---

## Task 10. Fix semantic rule matching

### Việc cần làm

Hiện rule kiểu `contains` có nguy cơ map nhầm:

```text
button_wrapper → button
```

Cần chuyển sang:

```text
exact_keyword
tokenized matching
longer keyword priority
```

### Agent/dev tự làm được

Có thể tự sửa `html-semantic-mapping.json` và `process_html.py`.

### Bạn cần tham gia mức độ: CAO

### Bạn tham gia để làm gì?

Bạn cần chốt **Figma naming convention**.

Agent/dev không thể tự biết team bạn muốn đặt tên layer như nào.

Bạn cần quyết định:

```text
1. Keyword nào bắt buộc?
2. Keyword nào là semantic?
3. Keyword nào chỉ là layout wrapper?
4. Có cho phép tên kiểu Header / nav_menu không?
5. Có cho phép button_wrapper, button_group, button_link không?
6. Với link styled as button, dùng <a> hay <button>?
```

### Bạn tham gia như nào?

Bạn review và chốt bảng rules:

```text
button         → <button type="button">
button_link    → <a>
button_wrapper → <div>
form_submit    → <button type="submit">
image          → <img>
heading_h1     → <h1>
paragraph      → <p>
```

### Output cần có

```text
html-semantic-mapping.json chuẩn rule-based
process_html.py không map nhầm contains
fixture test button_wrapper pass
```

---

## Task 11. Validate Figma HTML naming convention

### Việc cần làm

Chạy:

```bash
python .claude/skills/figma-to-html-architect/scripts/validate_figma_html.py \
  --workspace <ws> \
  --node-id <node-id> \
  --mode warn
```

Validation nên có 3 modes:

```text
strict
warn
ignore
```

### Agent/dev tự làm được

Có thể chạy và tạo report.

### Bạn cần tham gia mức độ: CAO

### Bạn tham gia để làm gì?

Bạn cần sửa layer names trong Figma nếu report báo naming chưa đạt.

Ví dụ:

```text
Frame 123
Group 1
Rectangle 4
```

Nếu những layer đó là semantic-critical, bạn cần rename.

### Bạn tham gia như nào?

Bạn mở Figma và sửa tên layer theo naming guide:

```text
section_pricing
heading_h2
paragraph_intro
button_link_primary
image_avatar
form_input_email
```

Sau đó rerun extraction + validation.

### Output cần có

```text
html_validation_report.json
status = passed hoặc passed_with_warnings
```

---

## Task 12. Process HTML với Client-First class matching

### Việc cần làm

Chạy:

```bash
python .claude/skills/figma-to-html-architect/scripts/process_html.py \
  --workspace <ws> \
  --node-id <node-id> \
  --baseline workspace/<ws>/design-system/client-first-baseline-contract.json
```

Processor phải:

```text
- đọc raw-figma.html
- rewrite semantic tags
- match classes từ webflow-contract/client-first baseline
- preserve class order
- giữ inline style chưa map được
- output final-webflow.html
- output html_processing_report.json
```

### Agent/dev tự làm được

Có thể sửa script và test fixtures.

### Bạn cần tham gia mức độ: TRUNG BÌNH

### Bạn tham gia để làm gì?

Bạn cần review output HTML có đúng kỳ vọng không:

```text
- tag có đúng semantic không?
- class có đúng Client-First không?
- inline style còn lại có hợp lý không?
- layout có cần manual Webflow class không?
```

### Bạn tham gia như nào?

Bạn mở:

```text
final-webflow.html
html_processing_report.md/json
```

Review 3 nhóm:

```text
1. Wrong semantic tag
2. Wrong/missing class
3. Unmapped inline styles
```

Sau đó quyết định:

```text
- sửa Figma naming
- sửa semantic rule
- sửa class matching rule
- bổ sung mapping
```

### Output cần có

```text
final-webflow.html
html_processing_report.json
status = passed hoặc passed_with_warnings
```

---

# Phase 4 — Webflow apply/write

## Mục tiêu

Không ghi Webflow trực tiếp. Luôn có preview → approval → apply → audit.

---

## Task 13. Build Webflow write preview

### Việc cần làm

Trước khi gọi Webflow MCP write tools, sinh preview:

```text
webflow-sync-preview.json
architect-diff-preview.json
```

Preview cần gồm:

```text
- variables sẽ update
- classes/style props sẽ update
- elements sẽ create/update
- properties sẽ remove/keep
- risky operations
```

### Agent/dev tự làm được

Có thể implement preview generator.

### Bạn cần tham gia mức độ: RẤT CAO

### Bạn tham gia để làm gì?

Bạn là người approve thay đổi vào Webflow.

Agent không nên tự ghi Webflow khi chưa có approval vì có thể làm hỏng site.

Bạn cần quyết định:

```text
1. Variable nào update được?
2. Class nào update được?
3. Có cho phép tạo class mới không?
4. Có cho phép ghi đè style prop không?
5. Có cần branch/staging Webflow site không?
```

### Bạn tham gia như nào?

Bạn review preview report và approve:

```text
APPROVE WEBFLOW PATCH
```

hoặc yêu cầu sửa:

```text
SKIP variable X
DO NOT update class Y
Only update variables, not classes
```

### Output cần có

```text
webflow-sync-preview.json
architect-diff-preview.json
approval status
```

---

## Task 14. Implement Webflow apply step

### Việc cần làm

Sau approval, gọi Webflow MCP:

```text
variable_tool → update/create variables
style_tool    → update CSS props của class
element tool  → create/apply DOM structure nếu có
```

### Agent/dev tự làm được

Có thể implement tool invocation flow nếu MCP available.

### Bạn cần tham gia mức độ: CAO

### Bạn tham gia để làm gì?

Bạn cần cung cấp/confirm Webflow environment:

```text
- site/project nào
- staging/branch nào
- MCP bridge có connect không
- có quyền write không
- có backup/rollback chưa
```

### Bạn tham gia như nào?

Bạn:

```text
1. Mở Webflow project đúng.
2. Kết nối Webflow MCP.
3. Chọn staging/branch nếu có.
4. Confirm apply.
5. Check visual result sau apply.
```

### Output cần có

```text
write-audit-log.jsonl
webflow-apply-report.json
post-apply verification report
```

---

# Phase 5 — E2E fixture và production hardening

## Task 15. Tạo E2E fixture

### Việc cần làm

Tạo fixture:

```text
tests/fixtures/e2e/basic-card/
├── client-first-baseline-contract.json
├── figma-design-system.json
├── raw-figma.html
├── expected-webflow-design-system.json
├── expected-final-webflow.html
└── expected-reports/
```

### Agent/dev tự làm được

Có thể tạo fixture mock.

### Bạn cần tham gia mức độ: TRUNG BÌNH

### Bạn tham gia để làm gì?

Bạn cần chọn component mẫu đại diện:

```text
- Button
- Card
- Hero section
- Form
- Navbar
```

### Khuyến nghị

Bắt đầu với:

```text
Card component
```

Vì đủ typography, spacing, image, button nhưng chưa quá phức tạp.

### Bạn tham gia như nào?

Bạn chọn 1 Figma component mẫu và export raw/context cho agent.

### Output cần có

```text
E2E fixture pass từ baseline → figma-contract → webflow-contract → final-html
```

---

## Task 16. Chạy quality gate/path audit/dependency audit

### Việc cần làm

Sau khi sửa xong:

```bash
python .claude/skills/_shared/scripts/run_quality_gate.py --profile html-first
```

Chạy lại:

```text
path audit
dependency audit
test suite
orchestrator smoke test
```

### Agent/dev tự làm được

Có thể tự chạy.

### Bạn cần tham gia mức độ: THẤP

### Bạn tham gia để làm gì?

Bạn review final summary:

```text
- còn path sai không?
- còn dead active file không?
- flow smoke test pass chưa?
```

### Output cần có

```text
quality gate pass
path audit pass
dependency audit pass
e2e fixture pass
```

---

# Ma trận bạn cần tham gia ở đâu nhiều nhất

| Khu vực                      | Mức bạn cần tham gia | Vì sao                                                  |
| ---------------------------- | -------------------: | ------------------------------------------------------- |
| Security/token cleanup       |              Rất cao | Chỉ bạn revoke/rotate token được.                       |
| Client-First baseline review |                  Cao | Đây là kiến trúc design system clone sang Figma.        |
| Figma extraction strategy    |              Rất cao | Cần file key/token/MCP/API access và quyết định source. |
| Figma library fix            |                  Cao | Cần sửa variable/style/layer naming trong Figma.        |
| Semantic naming convention   |                  Cao | Cần chốt rule team sẽ dùng trong Figma.                 |
| Webflow write approval       |              Rất cao | Ghi Webflow có rủi ro phá site.                         |
| Runtime Python bugfix        |                 Thấp | Agent/dev tự sửa được.                                  |
| Docs/path cleanup            |                 Thấp | Agent/dev tự sửa được, bạn chỉ review.                  |
| E2E fixture chọn component   |           Trung bình | Cần bạn chọn component đại diện.                        |

---

# Những quyết định bạn nên chốt trước khi giao agent

## Decision 1 — Repo root marker

Khuyến nghị:

```text
Use `.claude/` + `knowledge-base/` + `source-css/` to detect repo root.
```

## Decision 2 — Source CSS canonical path

Khuyến nghị:

```text
source-css/client-first-v2-2.webflow.css is canonical.
workspace/ only stores generated runtime artifacts.
```

## Decision 3 — Missing baseline behavior

Khuyến nghị:

```text
If workspace/<ws>/design-system/client-first-baseline-contract.json is missing,
fail with CLIENT_FIRST_BASELINE_NOT_FOUND.
Do not silently fallback to template.
```

## Decision 4 — Mapping file source

Khuyến nghị:

```text
Canonical mapping file:
.claude/skills/design-system-sync/references/figma-webflow-mapping.md
```

## Decision 5 — Figma extraction source

Bạn cần chọn:

```text
A. Figma REST API
B. Figma MCP full variable export
C. Manual JSON export for test only
```

Khuyến nghị:

```text
Use manual JSON fixture first for E2E test.
Then implement Figma REST/MCP full extraction.
```

## Decision 6 — Semantic matching

Khuyến nghị:

```text
Use exact_keyword/tokenized matching.
Avoid contains matching for semantic tags.
```

## Decision 7 — Webflow write policy

Khuyến nghị:

```text
Preview required.
Human approval required.
Write only to staging/branch first.
Always generate write-audit-log.jsonl.
```

---

# Practical execution order

## Sprint 1 — Make repo runnable

```text
1. Remove settings.local + rotate token.
2. Fix repo root resolver.
3. Fix map_variables CLI/defaults.
4. Fix orchestrator CSS path.
5. Fix validate_figma_extraction mapping path.
6. Smoke test scripts.
```

Bạn tham gia chủ yếu ở:

```text
- token/security
- confirm source-css canonical
- confirm baseline fail policy
```

---

## Sprint 2 — Make design-system sync pass

```text
1. Run Client-First baseline extraction.
2. Review baseline contract.
3. Create/manual fixture figma-design-system.json.
4. Validate figma contract.
5. Map to webflow contract.
6. Review mapping report.
```

Bạn tham gia chủ yếu ở:

```text
- review baseline
- fix Figma variables/styles
- approve mapping decisions
```

---

## Sprint 3 — Make HTML architect pass

```text
1. Fix semantic matching.
2. Chốt naming guide.
3. Prepare raw-figma.html fixture.
4. Run validate_figma_html.
5. Run process_html.
6. Review final-webflow.html.
```

Bạn tham gia chủ yếu ở:

```text
- chốt naming convention
- sửa layer names trong Figma
- review semantic/class output
```

---

## Sprint 4 — Add Webflow write safely

```text
1. Generate Webflow patch preview.
2. Review/approve patch.
3. Apply via Webflow MCP to staging.
4. Generate write audit log.
5. Post-apply verification.
```

Bạn tham gia chủ yếu ở:

```text
- connect Webflow MCP
- choose site/branch
- approve patch
- visual QA
```

---

## Sprint 5 — Production hardening

```text
1. Add E2E fixture.
2. Add quality gate.
3. Rerun path audit.
4. Rerun dependency audit.
5. Update docs.
```

Bạn tham gia chủ yếu ở:

```text
- chọn component fixture đại diện
- review final docs/report
```

---

# Prompt giao agent/dev

```text
Bạn hãy triển khai flow Figma → HTML → Webflow theo plan dưới đây.

Thực hiện theo sprint, không nhảy sang Webflow write trước khi P0 blocker và deterministic local pipeline pass.

Sprint 1:
1. Remove `.claude/settings.local.json` khỏi tracking, add `.gitignore`, tạo settings example.
2. Fix repo root resolver trong:
   - validate_artifacts.py
   - utils.py
   - resolve_client_first.py
3. Fix `map_variables.py` để support `--workspace <ws> --strict` với default path hợp lý.
4. Fix orchestrator CSS input path về `source-css/client-first-v2-2.webflow.css`.
5. Fix `validate_figma_extraction.py` default mapping path về `.claude/skills/design-system-sync/references/figma-webflow-mapping.md`.
6. Smoke test các scripts.

Sprint 2:
1. Run `extract_client_first_baseline.py` từ source-css.
2. Output baseline contract và extraction report.
3. Tạo/manual fixture `figma-design-system.json` nếu chưa có Figma API extraction.
4. Run validate figma contract.
5. Run map variables.
6. Output `webflow-design-system.json` và `mapping-report.json`.

Sprint 3:
1. Fix semantic mapping từ contains sang exact/token-based matching.
2. Update `html-semantic-mapping.json`.
3. Run validate HTML naming.
4. Run process HTML.
5. Output `final-webflow.html` và `html_processing_report.json`.

Sprint 4:
1. Implement Webflow patch preview.
2. Không apply Webflow nếu chưa có human approval.
3. Sau approval, dùng Webflow MCP:
   - variable_tool
   - style_tool
   - element write tool nếu cần
4. Output `write-audit-log.jsonl`.

Sprint 5:
1. Add E2E fixture.
2. Run quality gate.
3. Rerun path/dependency audit.
4. Update docs.

Important policies:
- Client-First CSS layer is architecture SOT.
- Figma is runtime value/component intent SOT.
- Webflow native `.w-*` classes must not be cloned into Figma.
- No write to Webflow without preview + approval.
- Fail clearly if baseline/mapping/schema is missing.
```
