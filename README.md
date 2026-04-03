# YouTube Content Gap Research

## Overview
This repository captures a practical process for identifying underserved YouTube search demand and gap opportunities a creator can fill.

## Objective
- Find high-demand keywords / queries that return low-quality or low-quantity results on YouTube.
- Recommend content ideas that are practical, high-ROI, and low competition.

## Methodology
1. Use YouTube keyword tools (VidIQ, TubeBuddy, Keywords Everywhere, Ahrefs, Semrush) to generate a dataset:
   - keyword
   - search volume
   - trend
   - competition / density
   - video count
2. Use YouTube autocomplete and `People also ask` for question-based intent:
   - track “how to”, “why”, “best”, “for beginners”, “vs”, “2026”
3. Review top videos and their comment clusters for unmet needs:
   - “this didn’t cover…”
   - “where is content about…”
   - “please explain…”
4. Analyze Google Trends for `YouTube Search` and rising queries; map to low supply top 10 results.
5. Scan community forums (Reddit, Quora, StackExchange, Discord) for explicit asks: “no good video on…”, “Can anyone recommend a guide for…”

## Initial Gap Leads (hypotheses)
These are candidate gap neighborhoods based on recent macro trends and typical supply deficits:
- Practical AI prompt engineering with current (2026+) multimodal models.
- Deep-diving topics in personal finance for younger audiences:
  - shortcuts for `tax optimization in gig economy` by country.
  - `crypto tax reporting for Web3 earners` with regional rules.
- `Video production on budget` using free mobile-first workflows for shorts and TikTok repurposing.
- `Career pivot planning for mid-30s` (from corporate → no-code + AI freelancing) with step-by-step milestones.
- `SaaS MVP launches without code` with real world launch analytics and repeatable templates.

## Next Steps (Run this weekly)
1. Export keyword list (100+ terms) from VidIQ/TubeBuddy with metrics.
2. Filter by market score:
   - volume >= 5000/mo
   - competition <= 0.4 (or low video count)
3. For each candidate, validate by manual search:
   - top 10 results are short, out-of-date, or generic.
4. Build a content plan by ranking: high intent, low production barrier, high leverage.
5. Create tracking sheet and update with real performance in YouTube Studio.

## 2026 research-log
- See `notes/research-log-2026.md` for the focused gap analysis, draft opportunity list, and manual research actions.

## Automated research script
- `scripts/gap_research.py`: runs YouTube Data API search, saves top video metadata + transcripts + comments to `data/`.
- Usage:
  - `pip install google-api-python-client youtube-transcript-api pandas tqdm`
  - `export YOUTUBE_API_KEY="YOUR_API_KEY"`
  - `python scripts/gap_research.py --query "ai prompt engineering" --max-videos 20 --comments 150`

This script provides a concrete path to inspect real comments and transcript content for gap signals.

## Automation Aids
- `scripts/extract_autocomplete.py` (scrapes YouTube suggestions for seeds)
- `scripts/analyze_gap.py` (combines API data from Keywords Everywhere + YouTube Data API v3 for supply metrics)

## Repository links
- Workflow docs: `docs/process.md`
- Notes: `notes/gap-observations-2026.md`

## Licence
MIT
