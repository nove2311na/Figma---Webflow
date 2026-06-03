# Finsweet Client-First: The Definitive Guide (Knowledge Base)

The Client-First system is a Webflow build methodology that prioritizes clarity, scalability, and end-user friendliness. This is the core knowledge base that every Agent in the MAS system must strictly follow.

---

## Chapter 1: Naming Strategy

The ultimate goal: Class names must be self-explanatory regarding their function (Human-readable).

### 1.1. Custom Classes (Using the underscore `_`)
Custom classes are created for specific elements of a component or a single section.
- **Structure:** `[Component Prefix]_[Element Name]`
- **Delimiter:** Use a single underscore (`_`) to separate the component name and the element name. Use a hyphen (`-`) for words within names.
- **Correct Examples:** `home-hero_image-wrapper`, `nav_link`, `footer_legal-text`.
- **Incorrect Examples:** `home-hero-image-wrapper` (missing `_`), `HomeHero_Image` (does not use PascalCase).
- **Why use `_`?** So that both AI and humans can immediately identify this as a child element belonging to a specific parent component.

### 1.2. Utility Classes (Using the hyphen `-`)
Utility classes are site-wide classes that can be reused on any element.
- **Structure:** Only use hyphens (`-`). Absolutely NO underscores (`_`).
- **No Abbreviation Rule:** Do not use `mb-10`, `pl-large`. Must write in full: `margin-bottom`, `padding-left`.
- **Examples:** `text-size-large`, `background-color-brand`, `margin-bottom-medium`.

### 1.3. Combo Classes (Using the `is-` prefix)
Combo classes are used to create variations of a base class.
- **Prefix:** Starts with `is-`.
- **Examples:** `button` + `is-secondary`, `nav_link` + `is-active`.
- **Note:** **Prohibit** "class stacking" of more than 3 layers if it can be replaced by a Custom class.

---

## Chapter 2: Core Structure

Client-First requires a strict hierarchical structure consisting of 6 main layers to ensure consistency.

1.  **`page-wrapper`**: The outermost Div (100% width). Contains all page content.
2.  **`main-wrapper`**: Wraps the main content (excluding Nav and Footer). **Required** to use the `<main>` HTML tag.
3.  **`section_[name]`**: Uses a Custom class (e.g., `section_hero`). Manages the section's position on the page.
4.  **`padding-global`**: Located directly inside `section`. Manages consistent left/right gutters for the entire site.
5.  **`container-[size]`**: Located inside `padding-global`. Manages the maximum width (`max-width`) of the content (e.g., `container-large`).
6.  **`padding-section-[size]`**: Located inside `container` or positioned according to the layout, used to create top/bottom padding for the section.

---

## Chapter 3: Typography & Accessibility System

- **Tag-First Strategy:** Always style default HTML tags (`All H1 Headers`, `All Paragraphs`, `All Links`) before creating classes.
- **Heading Styles:** Use the `heading-style-h#` class (e.g., `heading-style-h2`) when a heading is semantically (SEO) an H3 but visually needs to look like an H2.
- **Text Sizes:** Use the `text-size-tiny`, `small`, `medium`, `large`, `huge` system.

---

## Chapter 4: Spacing & Units System

### 4.1. Spacing Wrappers (The optimal solution)
Client-First encourages not placing margin/padding directly on content classes (such as text).
- **Method:** Use a Div Wrapper around the element. Apply utility classes for direction and size (e.g., `margin-bottom` + `margin-medium`).
- **Advantage:** Allows for flexible spacing changes without needing to modify the element's own class.

### 4.2. REM Units (The Golden Rule)
- **Base:** 1rem = 16px.
- **Benefits:** Ensures accessibility when users change their browser font size and supports fluid responsiveness.
- **Calculation:** `PX value in Figma / 16 = REM value`.

---

## Chapter 5: Figma Analysis according to Client-First

When reading designs from Figma, the Architect must perform the following steps:
1.  **Component Identification:** Categorize what is a Global Component (Navbar, Footer) and what is an independent Section.
2.  **Layout Extraction:** Look at Figma's Auto Layout to determine whether to use Flexbox (Align/Justify) or Grid.
3.  **Variable Mapping:** 
    - Colors -> Webflow Variables.
    - Spacing (Gap, Padding) -> Spacing System (Utility or Variables).
4.  **Visual Fidelity:** Ensure Border-radius, Shadow, and Gradients are captured accurately 1:1 but applied using standard Classes.
