# Name and keyboard

| Class | Flag when | Fix |
|-------|-----------|-----|
| Alt | `img` without `alt` | Meaningful alt, or `alt=""` if decorative |
| Button | `div`/`span` with `onClick` | `<button>` or `role` + key handler |
| Label | `input` without `label`/`aria-label` | `<label htmlFor>` |
| Blank | `target="_blank"` without `rel="noreferrer"` | Add rel |
| Contrast | Hardcoded tiny gray text they asked about | Darker token; do not guess hex from a dump |

Do not add `aria-label` on a native button that already has text.
