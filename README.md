# Vishnu QR Scavenger Hunt (Chetna Scavenger Hunt)

**A web-based college treasure hunt built around hidden QR stickers, digital scratch cards and a live leaderboard.**

Live demo: https://vishnu-qr-code-project.vercel.app

The application is named *Chetna Scavenger Hunt* in the interface. It was created as a Diwali-fest concept at DTU for a student society focused on spirituality and yoga.

## Concept

Conventional college treasure hunts rely on riddles or quizzes. This project removes that barrier: participants only have to **find QR stickers hidden in hard-to-spot places**.

1. A participant finds a sticker and scans its QR code in the web app.
2. The app reveals a digital scratch card.
3. Scratching the card reveals one name from the *Vishnu Sahasranama* (the 1,008 names of Vishnu).
4. The participant enters the revealed name to claim points.
5. The leaderboard in the same app updates their score.

The intended effect is easy, enjoyable participation that also introduces people to the society and the names.

## Scope and Status

This was a **promotional contest concept** for a college society, not a commercial product.

- Built as a working prototype.
- **Tested with approximately 200 participants** who signed up and used the QR flow during a trial.
- **Not deployed as the actual Diwali-fest activity**, so event-scale operation has not been demonstrated.
- Future work: refine the experience, run it at a live event, and improve readiness for larger participation.

## Features

- Signup with name and 10-digit phone number (roll number optional); login with name and phone number.
- Server-side QR validation: unknown codes, scan limits, and duplicate-name checks per participant.
- On-screen scratch-card reveal and a name-entry step before points are awarded.
- Leaderboard ranked by number of successful scans.
- QR generation and printable A4 sticker sheets (12 stickers per page).

## Architecture

**Backend (`app.py`)**: Flask API that serves the app and handles participants, QR validation, claims and the leaderboard. Supabase stores the `students` and `qr_codes` tables; the claim endpoint calls the Supabase RPC function `process_qr_scan`.

| Endpoint | Purpose |
|---|---|
| `POST /api/signup` | Create a participant record |
| `POST /api/login` | Look up a participant by name and phone number |
| `POST /api/validate_qr` | Validate a QR code; check scan limits and duplicate claims |
| `POST /api/claim_qr` | Claim a valid code and update the score through a database function |
| `GET /api/leaderboard` | Return top participants by successful scans |

**Frontend (`index.html`)**: responsive single-page app with signup/login, QR scanning, scratch-card reveal (Canvas), name submission and leaderboard views.

**QR tools (`Vishnu Project/`)**: `qr_code.py` generates QR images and writes `database_import.csv`; `create_pdf.py` lays them out as printable A4 sheets.

## Running Locally

```bash
pip install -r requirements.txt
```

Create a `.env` file (do not commit it):

```env
SUPABASE_URL=...
SUPABASE_SECRET_KEY=...    # preferred
# SUPABASE_KEY=...         # anon-key fallback supported by the app
```

```bash
python app.py
```

A Supabase project is required, with the `students` and `qr_codes` tables, QR data imported from `database_import.csv`, and the `process_qr_scan` function.

**Deployment:** `vercel.json` routes the app and API requests to `app.py`. Set the Supabase variables in the Vercel project settings.

## Technology Stack

Python, Flask, Flask-CORS · Supabase · HTML, CSS, JavaScript (Canvas) · qrcode, Pillow, ReportLab · Vercel
