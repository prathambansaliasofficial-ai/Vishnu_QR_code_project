# Vishnu QR Scavenger Hunt

**A college treasure hunt built around hidden QR stickers, digital scratch cards, Vishnu's names, and a live leaderboard.**

The web app's in-product name is **Chetna Scavenger Hunt**. It was created for a DTU Diwali-fest concept by a student society focused on spirituality and yoga.

## The idea

A conventional college treasure hunt often asks participants to solve riddles or quizzes, travel to a location, and collect a sticker or reward. This project experiments with a simpler format: **no riddles and no quiz questions — participants just have to find the QR stickers hidden in difficult-to-spot places.** The physical hunt is a game of hide-and-seek.

The digital experience works like this:

1. A participant finds a hidden sticker and scans its QR code using the web app.
2. The app reveals a digital scratch card.
3. Scratching the card reveals one name from the **Vishnu Sahasranama** (traditionally 1,008 names of Vishnu).
4. The participant types the revealed name and submits it to claim points.
5. The leaderboard, available in the same app, updates the participant's score.

The intended effect is to make participation easy and fun while introducing people to the society and the names of Vishnu.

## Purpose and scope

This was a **promotional contest / giveaway concept for a college society**, not a standalone commercial product. The idea was that removing the riddle-solving barrier might keep more students engaged than a conventional quiz-based hunt.

The project was built as a working web-app prototype and tested. **Around 200 people signed up and used the QR-code experience during a trial.** However, it was **not deployed as the actual Diwali-fest activity**, so a full event-scale deployment has not yet happened. It remains a project that can be refined and tried at a future event.

## Features

- Participant signup using name and a 10-digit phone number; roll number is optional.
- Login using the participant's name and phone number.
- Server-side QR validation, including unknown codes, scan limits, and duplicate-name checks for a participant.
- On-screen scratch-card reveal.
- Name-entry step before points are claimed.
- Leaderboard ranked by the number of successful scans.
- QR-code generation and printable A4 sticker sheets.

## How it works

**Backend — `app.py`**

A Flask API serves the web app and handles participant records, QR validation, claims, and leaderboard data. Supabase stores the `students` and `qr_codes` tables. The claim endpoint calls the Supabase RPC function `process_qr_scan`.

| Endpoint | Purpose |
|---|---|
| `POST /api/signup` | Create a participant record |
| `POST /api/login` | Find a participant using name and phone number |
| `POST /api/validate_qr` | Validate a QR code and check scan limits / duplicate claims |
| `POST /api/claim_qr` | Claim a valid QR code and update the score through a database function |
| `GET /api/leaderboard` | Return the top participants by successful scans |

**Frontend — `index.html`**

A responsive, single-page web app containing signup/login, QR scanning, scratch-card reveal, name submission, and leaderboard views.

**QR-generation tools — `Vishnu Project/`**

- `qr_code.py` generates QR images for the Vishnu names and writes the QR data to `database_import.csv`.
- `create_pdf.py` arranges the generated QR images into printable A4 sheets (12 stickers per page).
- `database_import.csv` contains the QR strings and associated names for importing into the Supabase `qr_codes` table.

## Run locally

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file (do not commit it):

```env
SUPABASE_URL=...
SUPABASE_SECRET_KEY=...    # preferred
# SUPABASE_KEY=...         # anon-key fallback supported by the app
```

Then start the Flask app:

```bash
python app.py
```

You also need a Supabase project with the `students` and `qr_codes` tables, the QR data imported from `database_import.csv`, and the `process_qr_scan` database function used by the claim endpoint.

## Deployment

The repository includes a Vercel configuration (`vercel.json`) that routes the app and API requests to `app.py`. Configure the Supabase environment variables in the Vercel project settings.

## Tech stack

- **Backend:** Python, Flask, Flask-CORS
- **Database / backend service:** Supabase
- **Frontend:** HTML, CSS, JavaScript, Canvas-based scratch-card interaction
- **QR and print generation:** qrcode, Pillow, ReportLab
- **Deployment:** Vercel

## Project status

- Working prototype and QR-code flow tested with approximately 200 participants.
- Not run as the actual DTU Diwali-fest event.
- Future work: refine the experience, test it at a live event, and improve operational readiness for larger participation.
