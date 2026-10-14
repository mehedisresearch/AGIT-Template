---
description: All code comments must be written in English
alwaysApply: true
---

# English-only comments

- Write **all** new and updated comments in **English**: `//`, `/* */`, `///`, JSDoc, inline `<!-- -->` in templates, and similar.
- **Do not** add or keep Chinese (or other non-English) text in comments when editing files.
- User-facing copy (UI strings, i18n keys, docs meant for end users) is **not** covered by this rule—only **source comments**.

```typescript
// BAD — non-English comment
// Initialiser le cache (example: any non-English language)

// GOOD
// Initialize the cache from the last session snapshot.
```

```tsx
// BAD
{/* Chargement… */}

// GOOD
{/* Loading spinner */}
```
