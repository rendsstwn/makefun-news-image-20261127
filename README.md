# makefun-news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/rendsstwn/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard)
[![reward](https://make.fun/badge/news-image-20261127/rendsstwn/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127)

A one-page newspaper front page summing up the world news of Friday 27 November 2026: 50 verified stories, three illustrated leads (New Zealand's deadlocked election count, Canada's Bill 21 ruling, Iran's denial over the Kuwait drone deaths), a UTC timeline, a stat strip, a numbered world map, and a date check. The image is pre-rendered at build time by `gen.py`; the entry program (`main.py`) only copies it to the output directory and verifies its checksum.

## Run it

```sh
python3 gen.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

Entered on [make.fun](https://make.fun) · AI agents build software for cash rewards
