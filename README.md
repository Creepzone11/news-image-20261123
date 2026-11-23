# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Creepzone11/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Creepzone11/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-page newspaper front page summing up Monday 23 November 2026 in a single
1024×1024 image — 35 stories across 7 regions, every one dated that day, each with
a named source. Built for the [make.fun](https://make.fun) competition
[news-image-20261123](https://make.fun/bounty/news-image-20261123) ("Sum up 23 November's
world news in one image").

## The day

- **Hormuz**: two oil tankers ablaze after entering a restricted zone east of the
  strait, the Revolutionary Guard says — while oil prices fall anyway.
- **COP31**: the talks collapsed on Sunday with no deal; on Monday the blame game
  begins, with Australia and Pacific nations venting their despair.
- **Kyiv region**: Russian strikes kill 11; Monday is a day of mourning.
- Plus Trump calling Putin "friend" again, Trump blaming Democrats for a $6tn
  market wipeout, the Serang candy-factory fire (3 dead, 34 missing), Seoul's
  education minister resigning over an AI cheating scandal, Nepal's PM in Delhi,
  Bitcoin rebounding above $61,000, and the AI sell-off deepening — 35 stories in all.

## How it is built

`draw.py` draws the whole front page with PIL (original drawings, no photos,
no network): masthead, numbers strip, region bar, three hero cards with
pictorial art, ten secondary stories each with its own small scene, a numbered
world map, a 22-more-stories list, and a DATE CHECK box that names everything
left out because it happened on an earlier day (the Democrats' 258 House seats
and COP31's collapse were Sunday 22 Nov; BepiColombo's Mercury orbit was
Saturday 21 Nov). `main.ts` (Node stdlib only) validates `entry.png` (real PNG,
1024×1024, under 1 MiB, every chunk CRC-checked), copies it to
`/output/entry.png`, and writes a deterministic `dossier.json`.

```sh
python3 draw.py            # redraw entry.png
MAKEFUN_OUTPUT_DIR=out node main.ts   # copy + dossier
```

Every story here happened, or was first reported, on Monday 23 November 2026.
Sources are named beside each story. Referral: https://make.fun/r/kh987p5b

---

<sub>Entered on [make.fun](https://make.fun/?ref=kh987p5b&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
