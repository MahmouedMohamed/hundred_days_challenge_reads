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
- Each folder holds one or more **pages**, numbered `1.png`, `2.png`, … with no gaps. Pages in a folder belong together and are shown in order.
- PNG only. Portrait pages around 1080×1520 read best on phones.

## How the app uses it

- A user gets **one folder per day**, starting at folder `1`.
- The next folder only downloads after the current one is marked read, and never on the same day the last one was downloaded.
- Downloaded pages are kept on the device and show up in the user's reading history. A read folder is never shown as "today's read" again.
- The app downloads `N/1.png`, `N/2.png`, … until a page is missing, so a gap in page numbers ends the folder early.
- If the next folder doesn't exist yet, users see "nothing new today". If `1/1.png` is missing (repo removed or emptied), they see "reading unavailable". History keeps working in both cases.

## Adding a day

1. Create the next numbered folder, e.g. `4/`.
2. Add `1.png`, `2.png`, … in reading order.
3. Commit and push to `main`. Raw GitHub picks it up within minutes.

Never rename or reorder folders that are already published: users who read them are already past that number.

## Content and copyright

Only publish pages you have the rights to share: your own writing, public-domain works, or material you have permission to redistribute. The pages in folders `1`–`3` are original samples written for this repository; replace them with your own content.

## facts/ (the note on Today, for Muslim users)

`facts/<lang>.json` (`ar`, `en`, `de`, `tr`) is a list in order. Each person goes through it from the first entry, one per day *they open the app* (the note changes at Fajr), so a day nobody opens the app skips nothing. After the last entry it starts again from the first. Keep the files in the same order in every language, and add new entries at the end. The card sits on Today above the daily reading and is closed until the user taps it.

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
