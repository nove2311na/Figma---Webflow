# Hướng dẫn cho Designer

Bạn làm việc trên **Figma**. Tài liệu này giải thích những gì bạn cần biết và làm để pipeline AI hoạt động đúng.

---

## Hệ thống này làm gì cho bạn?

Bạn thiết kế trên Figma → AI tự động build ra Webflow page đúng chuẩn Client-First V2,
không cần bạn viết một dòng code hay class nào.

Điều kiện: Figma file của bạn phải **cấu trúc đúng** như mô tả dưới đây.

---

## Quy tắc duy nhất bạn PHẢI tuân thủ: Variables cho mọi thứ

> **Không dùng raw value. Luôn dùng Figma Variable.**

| Thay vì | Hãy làm |
|---|---|
| Apply `font-weight: 700` trực tiếp | Dùng variable `Font Weight/bold` |
| Chọn màu `#2d62ff` từ picker | Dùng variable `Colors/Theme/Text Color/primary` |
| Set padding `32px` thủ công | Dùng variable `Spacing/medium` |
| Set font-size `24px` thủ công | Dùng variable `Font Size/medium` |

**Tại sao?** Variable = hợp đồng giữa bạn và AI. AI đọc variable name, không đọc raw pixel.
Nếu không có variable → AI phải đoán → build sai.

---

## Naming conventions

### Figma layers (frames, components)

Layer name ảnh hưởng trực tiếp đến tên class trong Webflow:

```
"Hero Section"       →  section_hero       (section class)
"Content Row"        →  hero_content-row   (component_element)
"Image Wrapper"      →  hero_image-wrapper
"Nav"                →  nav_component
```

- Đặt tên rõ nghĩa, tiếng Anh, không dùng "Frame 1", "Group 23"
- Dùng khoảng trắng hoặc kebab-case đều được — AI sẽ normalize
- Section-level frames (hero, features, pricing, footer, nav) cần tên đúng để AI nhận ra cấu trúc trang

### Figma Variable naming

Theo cấu trúc đã có trong shared library:

```
Colors/
  Theme/Text Color/primary
  Theme/Background/primary
  Theme/Border Color/primary

Spacing/tiny | xxsmall | xsmall | small | medium | large | xlarge | xxlarge | huge | xhuge | xxhuge
Section Padding/small | medium | large
Gaps/small | regular | medium | large

Font Size/tiny | small | regular | medium | large
Font Weight/light | normal | medium | semibold | bold | xbold
H1 … H6/ (heading tokens)
```

Nếu cần thêm token mới → đặt tên theo pattern trên, báo Developer trước khi build.

---

## Muốn thêm token mới?

1. Tạo Figma Variable với tên theo pattern đã có
2. Apply cho các element liên quan
3. Báo Developer: "Tôi thêm token `Spacing/custom-xl = 5rem`"
4. Developer sẽ sync token đó vào repo và Webflow trước khi AI build

---

## Muốn thêm màu mới?

Thêm vào **Theme collection** (không phải Base primitives), theo ngữ nghĩa:

```
✅ Colors/Theme/Text Color/brand        (đúng — semantic)
❌ Colors/Brand/blue                    (sai — primitive, AI không dùng trực tiếp)
```

Semantic name tồn tại qua dark mode, rebrand. Primitive name không tồn tại.

---

## Checklist trước khi bàn giao Figma cho Developer

- [ ] Tất cả màu đều dùng Theme variable (không có raw hex)
- [ ] Tất cả spacing/padding/gap đều dùng Spacing variable
- [ ] Tất cả font-size, font-weight đều dùng Typography variable
- [ ] Layer names rõ nghĩa, tiếng Anh (không có "Frame 1", "Group 23")
- [ ] Mỗi section-level frame có tên nhận dạng được (hero, features, pricing, nav, footer...)
- [ ] Component wrappers được đặt tên theo pattern `[name]` hoặc `[name] Component`
- [ ] Không có border, shadow, gradient cứng — hoặc nếu có thì đã thống nhất sẽ tạo custom class

---

## Khi nào KHÔNG cần dùng variable?

- Border, shadow, gradient **đặc biệt** cho 1 section (e.g. gradient background của hero) → tạo custom class, không cần variable
- Giá trị chỉ dùng 1 lần duy nhất, không tái sử dụng → có thể để Developer tạo custom class

---

## Liên hệ

Nếu không chắc về token nào → hỏi Developer trước khi thiết kế thêm.
Đừng "tự sáng tạo" naming vì sẽ làm pipeline fail.
