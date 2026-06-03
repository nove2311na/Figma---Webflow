# No-Overwrite Policy

Default write mode is `create_only`.

Allowed write modes:

| Mode | Meaning |
|---|---|
| `create_only` | Create only when path does not exist. |
| `append_with_evidence` | Append a dated note with source and validation. |
| `merge_with_report` | Edit existing file only after reading it and reporting changed sections. |
| `manual` | Human performs or approves the write. |

Forbidden:

- silent overwrite,
- deleting workspace state without archive validation,
- restoring archives into non-empty workspace,
- writing secrets to committed files.

