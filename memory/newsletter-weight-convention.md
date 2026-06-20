---
name: newsletter-weight-convention
description: All future newsletters should include `weight: 1` in their frontmatter to ensure they appear at the top of the "Recent Posts" section on the home page.
metadata:
  type: project
---

# Newsletter Weight Convention

## Why
The home page (`layouts/index.html`) sorts posts by `date` (descending) by default, but may prioritize other posts due to:
- Custom sorting logic in the template (e.g., filtering by section or tag).
- Hugo’s default behavior of showing only the most recent posts (e.g., `first 5`).

Adding `weight: 1` to the frontmatter of newsletters ensures they appear at the **top of the "Recent Posts" section**, regardless of other sorting logic.

## How to Apply
For all future newsletters (e.g., `content/posts/digests/pending/*.md`), include this in the frontmatter:
```yaml
weight: 1
```

## Example
```yaml
---
title: "Stoic Saturday #4: Title Here"
description: "Description here"
date: 2026-06-27T00:00:00Z
author: Phil Huffman
weight: 1  # <-- Add this line
sendfox_subject: "Subject here"
tags:
  - weekly-digest
  - stoicism
---
```

## Notes
- `weight` is a Hugo frontmatter field that overrides default sorting (lower numbers appear first).
- This convention applies **only to newsletters** (e.g., `digests/`), not to other post types (e.g., `essays/` or `civics/`).
- If other posts also use `weight`, newsletters will still appear first due to their lower value (`1`).

**Related:** [[update-session-state-before-push]]