# Skill: Ninety-Days Report

Monthly companion reports on the bond market and the S&P 500, projecting the next ninety days under the assumption that the Iran situation does not improve. Produced on the first of every month at 0700 CT. The September 2026 installments are the canonical models: `content/posts/investing/bond-market-ninety-days.md` (bonds) and `content/posts/investing/sp500-next-ninety-days.md` (equities).

## When this runs

- Scheduled by launchd: `com.huffmanwrites.ninety-days-report` (plist source: `scripts/com.huffmanwrites.ninety-days-report.plist`; runner: `scripts/ninety-days-report-runner.sh`).
- The runner invokes Claude Code headless in this repo with this skill. Runs: the 1st of every month at 07:00 CT, indefinitely (no self-disable date).
- If drafts for today's date already exist, update them in place (same-day re-run).

## Mission

Produce TWO fact-checked, house-style ARTICLES, each projecting the markets ninety days out under a no-improvement Iran assumption:

1. **The bond market piece** — the yield curve, the Fed, term premium, buybacks, mortgages.
2. **The S&P 500 piece** — the index, valuation, the Fed's discount rate, the corruption premium, the consumer.

Both are DRAFTS for Philip to review, edit, and publish. Do NOT commit, push, or copy to SimpleBrain. (That happens at publish, per the one-commit rule.)

## House style

- Tone: personal stakes + historical context + contemporary urgency. Not yelling, not lecturing. Think *with* the reader.
- Model the voice and structure on the two canonical September installments, including their section architecture (Ninety Days From Today; Where the Market Stands Today; the thematic core; the map; the playbook; the close; Sources).
- Em-dash limit: no more than 3 per file. Prefer commas, colons, semicolons, or splitting sentences.
- Every load-bearing claim (yields, spreads, oil, levels, probabilities, historical figures) MUST be verified against a source this month; cite inline with links and a `## Sources` list. Flag anything unverifiable.
- Closing attribution: `*PRH | huffmanwrites.org | © Philip Huffman*`.

## Research phase (both articles)

1. Read the newest previous installments (`content/posts/investing/bond-market-ninety-days*.md`, `content/posts/investing/sp500-next-ninety-days*.md`) to carry the baseline and the running arguments forward.
2. Compute the new window: the run date plus ninety days. Name every dated anchor inside it (FOMC meetings, refunding dates, elections, holidays) and verify those dates.
3. Web-search fresh data and corroborate with at least two sources: 2s/10s/30s Treasury yields and the 10s30s spread (FRED DGS10/DGS30), Fed pricing (CME FedWatch via recent coverage) and the next two FOMC dates, Brent/WTI and the Strait of Hormuz status (ISW, AP, Reuters), mortgage rates (Freddie Mac), the S&P 500 level/distance from record/VIX/forward P/E, strategist targets, and any developments in the governance-corruption story (tariff litigation, exemption favoritism, Fed pressure).
4. Update or retire last month's claims: what came true, what did not, what the new window changes. The series improves if each installment holds the prior one accountable.

## Article structure

Both pieces keep the canonical architecture, refreshed:

1. **Ninety Days From Today** — the window, the war state as of the run date, the premise restated.
2. **Where the Market Stands Today** — the numbers, bulleted and bolded, all sourced.
3. **The thematic core** — bonds: safe-haven anatomy, the 10s30s spread trend, the buyback scorecard. Equities: the complacency problem, the rate-hike math, the corruption premium. Update each from live data; a section that no longer carries its weight may be replaced, but the corruption coverage is a standing requirement, not a one-off.
4. **The Ninety-Day Map** — dated checkpoints across the window, a base case, an escalation branch (1973-74/-48.2% and 1979 precedents; 1990/-19.9% as the milder analog), and a paradox branch (for bonds, the flight-to-quality rally; for equities, the melt-up that ignores the odds).
5. **What a Careful Investor Does** — the resilience playbook, matched to the new window.
6. **The close** — personal stakes, the credo voice, the dated storm.

- Hero images: generate a fresh pair per article via the OpenAI images API (`gpt-image-2`, key from `.zshrc`'s `OPENAI_API_KEY`, against `https://api.openai.com/v1`; do NOT rely on `OPENAI_BASE_URL`, which points at the local Ollama proxy and serves no images). Standing instruction from Philip: keep using this key until it is declined; if a call fails with an auth/billing error (quota or balance exhausted), do not debug or retry the account — note it in the output and stop. The agreed fallback is fal.ai (FAL) for image generation, to be wired up at that point (Philip will provide the FAL key).

- Files: `content/posts/investing/bond-market-ninety-days-YYYY-MM-DD.md` and `content/posts/investing/sp500-next-ninety-days-YYYY-MM-DD.md` (date = run date). The undated September slugs stay as the first installments.
- Frontmatter (both): `title`, `description` (one sentence naming the new window), `date` (run time, CT), `author: Philip Huffman`, `lastmod`, `hero_desktop`/`hero_mobile`/`hero_alt`/`hero_caption` (generated this run), `tags: [investing, markets, politics, risk]`, `draft: true`.
- Date guard: the `date` must never be in the future when published (Hugo's default `buildFuture: false` silently skips future-dated content). Dating to the run day is safe for same-day publication. Never pre-date.
- Hero images: generate a fresh pair per article via the OpenAI images API (`gpt-image-2`, key from `.zshrc`'s `OPENAI_API_KEY`, against `https://api.openai.com/v1`; do NOT rely on `OPENAI_BASE_URL`, which points at the local Ollama proxy and serves no images). Follow `skills/hero-image-workflow.md`: locked aesthetic (Parian marble, midnight navy, gold, conceptual, no text), next available NN in `static/img/articles/` (check the highest existing number first), 16:9 cropped to 1365×768 and 4:5 to 896×1120, WebP q92 via `cwebp`. Wire frontmatter and add `data/gallery.yml` entries. Concepts should stay distinct from prior installments while remaining in the same visual family (September used a marble wall with a gold yield-curve crack, and a marble bull with a climbing gold fissure).
- Verify: `hugo --gc --minify --buildDrafts` builds with 0 errors.
- Leave both files uncommitted. Do NOT copy to SimpleBrain (that happens at publish). Do NOT commit or push.

## SimpleBrain note (for Philip at publish)

At publish time, the post-commit copy goes to `~/SimpleBrain/raw/content/posts/investing/`, and the SimpleBrain translate loop converts it to `wiki/articles/<slug>.md` and archives the raw file (see `translate.md` there).