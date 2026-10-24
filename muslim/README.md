# muslim/

The reading days for **Muslim users**: a complete list that starts at day 1, one folder per day, `muslim/<N>/<lang>/1.png` (and `q.txt` for a reflection question), where `N` is the user's own day number.

Days 1 to 10 here are copies of the root days (`python tools/make_pages.py --copy-shared` makes them again). Every day after 10 exists only in `muslim/` and in `general/`, each with its own text.

To add day `N`: put its source in `tools/src/muslim/<N>.json` and run `python tools/make_pages.py tools/src/muslim/<N>.json`. That renders the pages here and updates `index.json`. See the main README.
