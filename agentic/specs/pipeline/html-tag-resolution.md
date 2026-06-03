# HTML Tag Resolution Specification

## Tag Resolver Priority

- Priority of HTML tag resolution:
  1. Component Registry (matches explicitly configured HTML tags for matched components)
  2. Explicit Prefix (e.g. layers prefixed with `button:`, `section:`, `nav:` in Figma)
  3. Normalized Role (e.g. `heading-1` maps to `h1`, `paragraph` maps to `p`, `button` maps to `a` or `button`)
  4. Text Purpose (text node length, tag mappings)
  5. Control/Media/List Context (e.g. children of list map to `li`, wrapper maps to `ul`)
  6. Parent Context (e.g. a button wrapper maps to semantic elements)
  7. Fallback (defaults to `div` or `span` for text)
