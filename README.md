# 100 Day Challenge — Today's Read

Daily reading pages for the [100 Day Challenge](https://github.com/MahmouedMohamed/hundred_days_challenge) app.

## Structure

```
1/1.png
1/2.png
2/1.png
3/1.png
3/2.png
3/3.png
```

- Each **folder** is one day's reading. Folders are numbered `1`, `2`, `3`, … with no gaps.
- Inside a folder the pages can be per language (`N/<lang>/1.png`, with `q.txt` for a reflection question). The app looks in its own language first, then the flat folder, then any other language.
- Each folder holds one or more **pages**, numbered `1.png`, `2.png`, … with no gaps. Pages in a folder belong together and are shown in order.
- PNG only. Portrait pages around 1080×1520 read best on phones.

## One list per audience

Each audience has its own complete list, starting at day 1: **Muslims** read `muslim/N/…` and **everyone else** reads `general/N/…`, with the same layout inside (`muslim/11/ar/1.png`, …). `N` is the user's own count of days. The two lists can differ and can end at different days.

The root folders `1/` … `10/` are the days from before audiences existed. They stay exactly as they are: apps that predate audiences only read them, and people who already downloaded them keep them (a folder is never renumbered). Days 1 to 10 in `muslim/` and `general/` are copies of those. **Every day after 10 is added to `muslim/` and `general/` only**, never to the root, so the root stops at 10 for good.

### index.json

`index.json` says where each list ends, so the app finds out in **one request** whether there is anything new, and never probes for folders that are not there:

```json
{"shared": 10, "muslim": 12, "general": 11}
```

`shared` is the last root day. `muslim` and `general` are the last day of each audience's own list. A phone reads its audience's folder while it has that day, and falls back to the root while the root has it. It is written by the tool below; do not edit it by hand. An app without `index.json` behaves as before (root folders only). App versions before audiences only know the root folders, so they stop at `shared`.

A phone that looked and found nothing does not look again the same day, and after that only asks for the one folder it is due, so the repo gets a handful of requests per person per day.

## Making a day

`tools/make_pages.py` renders a day from one source file with every language (ar, en, de, tr, fr):

```
python tools/make_pages.py tools/src/muslim/11.json          # day 11 for Muslims
python tools/make_pages.py tools/src/general/11.json         # day 11 for everyone else
python tools/make_pages.py --copy-shared                     # copy root days 1-10 into both audiences again
python tools/make_pages.py --index                           # only rewrite index.json
python tools/make_pages.py tools/src/5.json                  # re-render a root day (1-10) only
```

The source of an audience day goes in `tools/src/muslim/` or `tools/src/general/` (the file name is the day number; the same number may exist in both). If you fix a root day (1-10), run `--copy-shared` afterwards so the copies match. Every run rewrites `index.json`. Commit the folders and `index.json` together, then push.

### History

Pages stay on the person's phone, so reading history (the clock icon on Today's Read) works offline and costs no requests. A folder is only downloaded once.

- A user gets **one folder per day**, starting at folder `1`.
- The next folder only downloads after the current one is marked read, and never on the same day the last one was downloaded.
- Downloaded pages are kept on the device and show up in the user's reading history. A read folder is never shown as "today's read" again.
- The app downloads `N/1.png`, `N/2.png`, … until a page is missing, so a gap in page numbers ends the folder early.
- With `index.json`, a day that is not there yet is known from one request; without it the app looks for the folder and, if `1/1.png` is still there, says "nothing new today". If the repo is unreachable users see "reading unavailable". History keeps working in every case.

## Adding a day

1. Render it with `tools/make_pages.py` (above), or create the next numbered folder by hand and run `python tools/make_pages.py --index`.
2. Commit the folder and `index.json`, and push to `main`. Raw GitHub picks it up within minutes.

Never rename or reorder folders that are already published: users who read them are already past that number.

## Content and copyright

Only publish pages you have the rights to share: your own writing, public-domain works, or material you have permission to redistribute. The pages in folders `1`–`3` are original samples written for this repository; replace them with your own content.

## facts/ (the note on Today, for Muslim users)

`facts/<lang>.json` (`ar`, `en`, `de`, `tr`, `fr`) is a list in order. Each person goes through it from the first entry, one per day *they open the app* (the note changes at Fajr), so a day nobody opens the app skips nothing. After the last entry it starts again from the first. Keep the files in the same order in every language, and add new entries at the end. The card sits on Today above the daily reading and is closed until the user taps it.

```json
[
  {
    "text": "The note itself. Line breaks are kept.",
    "source": "Optional: a book, an author, a surah and verse",
    "category": "quote"
  }
]
```

- `text` is required. `source` and `category` are optional.
- `category` sets the colour and the title: `info` (fact), `quote`, `poetry`, `hadith`, `quran` (verse). Leave it out, or use any other word, for the default look and the title "Today's note".
- Quran verses are written in Arabic in every language file; they are not translated.
- A language without a file falls back to another language, so add the entry to every file you maintain.

## votes/ (the vote on new challenges, a 50-challenge reward)

`votes/current.json` is the open vote: its `id` and 2 to 5 `candidates`, each with its own `id` and its `text` in every app language. People who reached 50 challenges pick one in the app; each vote lands in the Firestore collection `challengeVotes` with the vote id (`voteId`) and the candidate id. A new vote id is a new vote: everyone can vote again. To close voting, delete the file.

When a vote ends:
1. Count it: in the Firebase console, `challengeVotes`, filter `voteId` = the vote's id and count each `candidate`.
2. Close it: delete `votes/current.json` (the app then says no vote is open).
3. Ship the winner: add it to `content/challenges.json` in the app (all five languages), run `dart run tool/encrypt_challenges.dart`, and release.
4. Tell people: a post, or a push to the `all` topic from the admin panel, naming the winner.
5. Next vote: a new `votes/current.json` with a new `id` (for example `2026-12`) and new candidates.
