# Component Registry Contract Specification

The Component Registry guarantees that all UI components generated or manipulated in the Figma-to-Webflow pipeline adhere to a strictly registered definition. In **strict mode**, any component instance discovered in Figma that is not registered, or fails signature matching, blocks the pipeline immediately.

## Registry Database Structure

The registry database is located at `knowledge-base/component-registry.json` and must conform to the JSON schema defined in `agentic/schemas/component-registry.schema.json`.

Each component in the registry defines:
- **`id`**: Unique alphanumeric identifier (e.g. `button`).
- **`name`**: Descriptive human-readable name.
- **`category`**: Category of the component (e.g., `primitives`, `layout`, `structure`, `forms`, `typography`, `media`).
- **`description`**: Explanation of purpose and usage.
- **`required_classes`**: Mandatory CSS classes from the Client-First contract that this component must utilize.
- **`required_variables`**: Mandatory CSS variables from the CSS variable index that this component must utilize.
- **`signatures`**: References to valid signature IDs in the component signatures database.

## Registry Constraints

1. **Mandatory Registry Enrollment**: Every component built in the final HTML code must correspond to an active component in the registry.
2. **Client-First Integration**: All classes specified in `required_classes` must exist inside the generated Client-First CSS contract (`knowledge-base/generated/client-first-library-contract.json`).
3. **No Dynamic Class Insertion**: The compiler is prohibited from injecting classes into components if they violate or bypass registry definitions.
4. **Validation Enforcements**: The validation gate `scripts/gates/validate_component_matching.py` verifies compliance. If a component uses an unauthorized class, the validation gate throws a blocker and exits with code 1.
