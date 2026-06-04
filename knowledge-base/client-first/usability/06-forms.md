---
_raw_url: https://finsweet.com/client-first/docs/usability/forms
_distilled_at: 2026-06-04
_token_estimate: 700
---

# Finsweet Client-First — Forms

Input + label + helper + error. The form field is a component; the form is a layout.

## Anatomy of a field

```html
<div class="form_field">
  <label for="email" class="form_label">Email</label>
  <input id="email" type="email" class="form_input" required>
  <p class="form_helper">We won't share your email.</p>
  <p class="form_error" role="alert">Please enter a valid email.</p>
</div>
```

The 4 children:
- `form_label` — visible label, `for` matching input id.
- `form_input` — the input itself.
- `form_helper` — optional, gray text below input.
- `form_error` — optional, red text, shown on validation fail. `role="alert"` for screen readers.

## Base styles

```css
.form_input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-family: var(--font-family--body);
  font-size: 1rem;
  line-height: 1.5;
  color: var(--_theme---text-color--primary);
  background: var(--_theme---background--primary);
  border: 1px solid var(--_theme---border-color--primary);
  border-radius: var(--_sizes---border-radius--small);
}
.form_input:focus-visible {
  outline: var(--focus--width) solid var(--_theme---system--focus-state);
  outline-offset: var(--focus--offset);
  border-color: var(--_theme---system--focus-state);
}
```

## Combos for state

```css
.form_input.is-error    { border-color: var(--_theme---system--error-text); }
.form_input.is-success  { border-color: var(--_theme---system--success-text); }
.form_input.is-disabled { opacity: 0.5; cursor: not-allowed; }
```

Apply via JS on validation result.

## Form layout

```html
<form class="form_component">
  <div class="form_field">...</div>
  <div class="form_field">...</div>
  <button type="submit" class="button is-primary is-large">Submit</button>
</form>
```

```css
.form_component { display: grid; gap: var(--size--medium); }
```

For side-by-side fields (first + last name on one row):

```css
.form_row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--size--small); }
@media (max-width: 479px) { .form_row { grid-template-columns: 1fr; } }
```

## Checkboxes + radios

```html
<label class="form_checkbox">
  <input type="checkbox" name="agree" required>
  <span class="form_checkbox-label">I agree to the terms</span>
</label>
```

The label wraps the input so clicking the text toggles the checkbox. Don't split the label and input into sibling elements.

## Select

```html
<label for="country" class="form_label">Country</label>
<select id="country" class="form_input">
  <option>Vietnam</option>
  <option>United States</option>
</select>
```

Style `<select>` with the same `form_input` class. Native arrow is fine for accessibility — replacing it with a custom arrow requires keyboard event handling.

## Error display pattern

```html
<div class="form_field is-error">
  <label for="email" class="form_label">Email</label>
  <input id="email" type="email" class="form_input" aria-invalid="true" aria-describedby="email-error">
  <p id="email-error" class="form_error" role="alert">Please enter a valid email.</p>
</div>
```

- `aria-invalid="true"` on the input.
- `aria-describedby` linking to the error message id.
- The error message is always in the DOM (CSS hides it via `.form_field:not(.is-error) .form_error { display: none; }`).

## Anti-patterns

- Placeholder as label: `<input placeholder="Email">`. Breaks when user starts typing.
- Splitting label + input into siblings without `for`/`id`.
- Custom checkboxes without keyboard support.
- Showing errors only on submit (should be inline as user types for some validations).
