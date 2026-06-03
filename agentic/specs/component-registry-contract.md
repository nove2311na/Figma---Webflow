# Component Registry Contract Specification

## Component Registry Rules

- All components used must be registered in the Component Registry.
- A component entry in the registry defines:
  - Component Name and ID
  - Structure Signature (hierarchy of child slots and HTML tag layout)
  - Style Mappings (required variables and classes)
  - Target Webflow Component ID (if mapping to an existing Webflow component)
- This contract guarantees that components are matched strictly based on signature and metadata, rather than simple name string matching.
