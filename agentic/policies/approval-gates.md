# Approval Gates

| Action | Gate |
|---|---|
| Create new scaffold file | Confirm path is inside this folder and write mode is create-only. |
| Edit existing file | Read current file and preserve unrelated changes. |
| Archive workspace | Confirm archive file exists and has non-zero size before deleting workspace. |
| Restore workspace | Confirm target workspace is empty. |
| Blueprint completion | PM presents blueprint and waits for user approval. |
| Webflow external write | Confirm site ID, page ID, approved blueprint, payload summary, and rollback/QA plan. |
| Figma external read | Confirm Figma URL/node scope and record extraction path. |
| Secret access | Require explicit need and never commit secret values. |
| Final completion | Run structure, quality, secret, and QA gates. |

