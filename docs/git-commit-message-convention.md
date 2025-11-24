## Git commit message convention

We follow Conventional Commits to produce readable history, automated changelogs, and predictable versioning.

### Message format
```
<type>[optional scope][!]: <short summary>

[optional body]

[optional footer(s)]
```
Note: `< >` indicates mandatory; `[ ]` indicates optional 

### Types
- `feat`: add a user-facing feature
- `fix`: bug fix
- `docs`: documentation-only changes
- `style`: formatting, whitespace, missing semicolons, no code change
- `refactor`: code change that neither fixes a bug nor adds a feature
- `perf`: performance improvement
- `test`: add or update tests only
- `build`: build system or external dependencies changes (npm, pip, docker)
- `ci`: CI configuration or scripts
- `chore`: maintenance tasks (no src or test changes)
- `revert`: revert a previous commit

Use the smallest accurate type. Prefer `refactor` over `chore` for code reshaping.

### Scope
Optional, but recommended when it clarifies impact. Use a folder, module, or domain name:
- Examples: `api`, `db`, `models`, `auth`, `ui`, `deps`
- Format: lowercase kebab or simple token, e.g. `feat(models): add item serialization`

### Summary line (subject)
- Imperative, present tense: “add”, “fix”, “update”
- Lowercase, no trailing period
- Aim for ≤ 72 characters

### Body
Explain the what and the why, not the how. Include context and tradeoffs.
- Wrap at ~72 characters per line
- Use bullet points if helpful
- Reference designs, specs, or docs when relevant

### Breaking changes
Signal with either `!` after type/scope or a `BREAKING CHANGE:` footer.
```
feat(api)!: require auth token for all write endpoints

BREAKING CHANGE: All POST/PUT/PATCH/DELETE now require Authorization header.
```

### Footers
- Issue references: `Refs #123`, `Closes #456`
- Co-authors: `Co-authored-by: Name <email>`
- Reverts: `Reverts <commit-sha>`

### Examples
Simple commit (most-used):
```
feat(models): add OrderItem relationship and constraints
```

```
docs(git): document git checkout best practices in docs/
```

Commit with body (make sure the body line wrapped at ~72 chars for the sake of readability):
```
fix(order): correct total calculation for cart checkout

Fixes rounding errors when combining per-item discounts with a cart-wide
coupon. Tax is now calculated on the discounted subtotal, and shipping
is added only when the free-shipping threshold is not met. Persists the
final total on Order to prevent drift if prices change later.

- Adds unit tests for mixed percentage and fixed-amount discounts
- Aligns rounding to banker's rounding at 2 decimal places
- Updates `OrderItem` to store effective_unit_price at checkout
```

```
fix(db): ensure connection pool closes on app shutdown

Avoids leaked connections when running under uvicorn reload mode.
Refs #231
```

```
refactor(item): extract price normalization helper

Moves duplicate logic into shared function for reuse and testability.
```

```
perf(api): cache item lookups for 5 minutes

Cuts 95th percentile latency by ~30% under load.
```

### Commit hygiene
- Keep commits focused and logically separate.
- Prefer many small, coherent commits over one large mixed commit.
- Avoid “wip” on shared branches; use local work-in-progress commits or stashes.
- Run tests/linters before committing when possible.

### Subject and body length guidance
- Subject ≤ 72 chars; body lines wrapped at ~72 chars
- If the subject alone conveys the change, body is optional

### Optional tooling
If desired in the future, we can enforce this format via commit hooks or commitlint. Until then, follow this guideline manually.


