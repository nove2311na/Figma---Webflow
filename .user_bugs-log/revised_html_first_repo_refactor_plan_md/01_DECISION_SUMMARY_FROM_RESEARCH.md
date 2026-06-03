# 01 — Decision Summary From Research

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## 1. Research xác nhận gì?

Hướng HTML-first vẫn đúng:

```text
Figma MCP + CSS
→ Semantic IR
→ HTML local
→ chunks
→ Webflow native ops
```

Những quyết định tiếp tục giữ:
- Python-first cho MVP.
- Strict mode cho mapping token/class/style.
- CSS thật là source of truth.
- Component reuse ưu tiên primitive recreation.
- Webflow write chỉ sau approval.
- Section analysis có thể parallel, Webflow writes nên serialize.

## 2. Research yêu cầu bổ sung gì?

### 2.1. Client-First Library Contract

Không đủ nếu chỉ có bảng class thủ công. Cần generated contract từ CSS thật:
- allowed classes;
- combo classes;
- variables;
- breakpoints;
- styleguide-only classes;
- Webflow native reserved classes;
- structural conventions.

### 2.2. Figma Extraction Contract

Figma MCP đọc xong phải lưu bundle ổn định, không để từng phase gọi MCP kiểu riêng.

### 2.3. Figma Normalizer

Cần xử lý Figma messy trước Semantic IR:
- generic layer names;
- missing styles;
- raw colors;
- arbitrary spacing;
- missing Auto Layout;
- ambiguous media;
- repeated uncomponentized blocks.

### 2.4. Component Signature Matching

Không chỉ match theo tên component; cần match theo structure/layout/slots/token cluster.

### 2.5. Golden Fixtures & Benchmarks

Phải có test clean/messy/broken để đo resolver có đúng không.

### 2.6. Asset/Alt Manifest

Ảnh phải có role và alt policy rõ: informative/decorative/functional/complex.

### 2.7. Tailwind-trace Evidence

Nếu Figma MCP output có Tailwind-like classes, chỉ dùng như evidence để suy ra intent, không copy vào HTML cuối.

### 2.8. Webflow Branch/Audit

Native ops cần branch-first, preflight, audit log, retry policy, concurrency policy.

## 3. Rủi ro nếu không update

| Thiếu | Rủi ro |
|---|---|
| Library Contract | LLM dùng class không tồn tại. |
| Extraction Contract | Figma output mỗi phase khác nhau, khó debug. |
| Normalizer | Figma messy làm sai semantic/tag/class. |
| Component Signature | Visual giống component nhưng mapping sai. |
| Fixtures | Không biết resolver đúng hay chỉ “nhìn ổn”. |
| Asset Manifest | Sai alt/decorative/functional image. |
| Audit Webflow | Khó rollback/debug native ops. |

## 4. Quyết định cập nhật plan

- Giữ architecture HTML-first.
- Thêm 4 phase/subphase mới: CSS Contract, Figma Extraction, Figma Normalization, Asset/Alt.
- Mở rộng Component Registry thành Registry + Signature.
- Mở rộng Gates/Evals bằng fixtures/benchmarks.
- Siết examples: mọi HTML snippet phải pass class existence gate.
