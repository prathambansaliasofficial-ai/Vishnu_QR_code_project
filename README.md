# Vishnu QR Scavenger Hunt

**A "find the sticker" treasure hunt with scratch-card QR codes, each hiding one of the names of Vishnu, and a live leaderboard.**

Built for the Diwali fest at DTU by a student society focused on spirituality and yoga. The in-app title is *Chetna Scavenger Hunt*.

## The idea

A traditional college hunt works like this: solve a quiz or riddle, walk to a location, collect a sticker, and win on the strength of your stickers. Riddles are where most people give up.

This hunt removes the riddles. **There is nothing to solve. You just have to find the stickers**, which are hidden in tricky spots around the venue, so it is really a game of hide and seek.

1. Find a sticker with a QR code.
2. Scan it with the web app.
3. Scratch the card on screen to reveal one of the names of Vishnu (the Vishnu Sahasranama, roughly 1,000 names).
4. Type the name in and submit it.
5. Your score updates on the leaderboard, in the same tab.

It is a low-effort, fun contest with no mental strain, so more people stay engaged, and in the process they learn the society's name and the Vishnu names. It works as a promotional giveaway for the society rather than a business.

## Status

- Built and tested. About 200 people signed up and used the QR codes in a trial run and it worked.
- **It was not run at the actual Diwali fest**, so it has not had a full live event yet.
- Still to do: refine it further for a real event.

## Features

- Sign up with name, phone number (10 digits) and optional roll number; log in later with name and phone.
- QR validation on the server: unknown codes, codes over their scan limit, and names you have already scanned are all rejected.
- Scratch-card reveal of the name on the phone screen.
- Live leaderboard ranked by number of scans.
- A generator that creates the whole set of QR codes and a printable PDF for the stickers.

## How it works

**Backend** (`app.py`): a Flask API that also serves `index.html`. Data lives in Supabase (tables `students` and `qr_codes`).

| Endpoint | Purpose |
|---|---|
| `POST /api/signup` | Create a participant |
| `POST /api/login` | Log in with name and phone number |
| `POST /api/validate_qr` | Check a scanned QR code is valid and not already used by that student |
| `POST /api/claim_qr` | Record the scan and update the student's score |
| `GET /api/leaderboard` | Students ranked by `current_scans` |

**Frontend** (`index.html`): a single-page web app with sign-up/login, scanner, scratch card and leaderboard views.

**QR tooling** (`Vishnu Project/`):
- `qr_code.py` generates a QR code for each name (with a peacock-feather logo in the centre) and writes the codes to `database_import.csv`.
- `create_pdf.py` lays the generated QR images out on A4 sheets (12 per page) for printing as stickers.

`database_import.csv` holds the random QR strings and their Vishnu names, ready to import into the `qr_codes` table.

## Run it locally

```bash
pip install -r requirements.txt
```

Create a `.env` file (it is git-ignored):

```
SUPABASE_URL=...
SUPABASE_SECRET_KEY=...    # preferred; SUPABASE_KEY (anon) is used as a fallback
```

Then:

```bash
python app.py
```

You will need a Supabase project with `students` and `qr_codes` tables, and the QR data imported from `database_import.csv`.

## Deployment

Configured for Vercel (`vercel.json` routes everything to `app.py`). Set the Supabase environment variables in the Vercel project settings.

## Tech

Python · Flask · Flask-CORS · Supabase · HTML/CSS/JavaScript (canvas scratch card) · `qrcode`, Pillow, ReportLab · Vercel
