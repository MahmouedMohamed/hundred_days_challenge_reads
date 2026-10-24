# general/

Days for **everyone who is not Muslim** (and anyone who did not say), after the shared days. Nothing is here yet.

A day lives in `general/<N>/<lang>/1.png` (with `q.txt` for a reflection question), where `N` is the user's own day number: the first day here is the shared days' last number plus one (day 11 while the shared days end at 10).

To add one, put its source in `tools/src/general/<N>.json` and run `python tools/make_pages.py tools/src/general/<N>.json`. That renders the pages here and updates `index.json`. See the main README.
