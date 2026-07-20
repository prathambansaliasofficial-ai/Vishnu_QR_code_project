import os
import re
import time
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from supabase import Client, create_client

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_PUBLISHABLE_KEY = (
    os.getenv("SUPABASE_PUBLISHABLE_KEY")
    or os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
)

if not SUPABASE_URL:
    raise RuntimeError("Please set SUPABASE_URL in your environment or .env file.")

if not SUPABASE_SECRET_KEY and not SUPABASE_PUBLISHABLE_KEY:
    raise RuntimeError(
        "Please set SUPABASE_SECRET_KEY (preferred) or SUPABASE_PUBLISHABLE_KEY in your environment or .env file."
    )

supabase_key = SUPABASE_SECRET_KEY or SUPABASE_PUBLISHABLE_KEY
if not SUPABASE_SECRET_KEY:
    app.logger.warning(
        "SUPABASE_SECRET_KEY is not set. Falling back to the publishable key, which may not have table write access."
    )

supabase: Client = create_client(SUPABASE_URL, supabase_key)


def json_error(message: str, status_code: int = 400):
    return jsonify({"status": "ERROR", "message": message}), status_code


def get_json_body() -> Dict[str, Any]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    return payload


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", "", name.strip())


def validate_phone_number(phone_number: str) -> bool:
    return bool(re.fullmatch(r"\d{10}", phone_number or ""))

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.post("/api/signup")
def signup():
    try:
        payload = get_json_body()
        name = str(payload.get("name", "")).strip()
        roll_number = str(payload.get("roll_number", "")).strip()
        phone_number = str(payload.get("phone_number", "")).strip()
    except ValueError as exc:
        return json_error(str(exc), 400)

    if not name or not phone_number:
        return json_error("name and phone_number are required.", 400)

    if not validate_phone_number(phone_number):
        return json_error("phone_number must be exactly 10 digits.", 400)

    if not roll_number:
        roll_number = ""

    student_id = f"{normalize_name(name)}_{int(time.time())}"

    try:
        response = (
            supabase.table("students")
            .insert(
                {
                    "student_id": student_id,
                    "student_name": name,
                    "student_roll_number": roll_number,
                    "phone_number": phone_number,
                    "current_scans": 0,
                    "scanned_vishnu_names": [],
                }
            )
            .execute()
        )
    except Exception as exc:
        message = str(exc)
        if "permission denied for table students" in message.lower():
            return json_error(
                "Supabase permission denied for students table. Set SUPABASE_SECRET_KEY in your Vercel environment and ensure the table role has INSERT access.",
                500,
            )
        return json_error(f"Failed to create student record: {message}", 500)

    return jsonify({"student_id": student_id})


@app.post("/api/login")
def login():
    try:
        payload = get_json_body()
        name = str(payload.get("name", "")).strip()
        phone_number = str(payload.get("phone_number", "")).strip()
    except ValueError as exc:
        return json_error(str(exc), 400)

    if not name or not phone_number:
        return json_error("name and phone_number are required.", 400)

    try:
        response = (
            supabase.table("students")
            .select("student_id")
            .eq("student_name", name)
            .eq("phone_number", phone_number)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        message = str(exc)
        if "permission denied for table students" in message.lower():
            return json_error(
                "Supabase permission denied for students table. Set SUPABASE_SECRET_KEY in your Vercel environment and ensure the table role has SELECT access.",
                500,
            )
        return json_error(f"Failed to query student record: {message}", 500)

    data = response.data or []
    if not data:
        return json_error("Student not found.", 404)

    return jsonify({"status": "SUCCESS", "student_id": data[0]["student_id"]})


@app.post("/api/validate_qr")
def validate_qr():
    try:
        payload = get_json_body()
        student_id = str(payload.get("student_id", "")).strip()
        qr_string = str(payload.get("qr_string", "")).strip()
    except ValueError as exc:
        return json_error(str(exc), 400)

    if not student_id or not qr_string:
        return json_error("student_id and qr_string are required.", 400)

    try:
        qr_response = (
            supabase.table("qr_codes")
            .select("vishnu_name, max_scans, times_scanned")
            .eq("qr_string", qr_string)
            .limit(1)
            .execute()
        )
        qr_data = qr_response.data or []

        if not qr_data:
            return json_error("Sorry, invalid QR code", 404)

        qr_item = qr_data[0]
        if int(qr_item.get("times_scanned", 0)) >= int(qr_item.get("max_scans", 0)):
            return json_error("Sorry, QR code limit exceeded", 400)

        vishnu_name = qr_item.get("vishnu_name")
        student_response = (
            supabase.table("students")
            .select("student_id")
            .eq("student_id", student_id)
            .contains("scanned_vishnu_names", [vishnu_name])
            .limit(1)
            .execute()
        )
        student_data = student_response.data or []

        if student_data:
            return json_error("Sorry, this QR code has already been scanned by the student.", 400)

        return jsonify({"status": "SUCCESS", "vishnu_name": vishnu_name})
    except Exception as exc:
        return json_error(f"Failed to validate QR code: {exc}", 500)


@app.post("/api/claim_qr")
def claim_qr():
    try:
        payload = get_json_body()
        student_id = str(payload.get("student_id", "")).strip()
        qr_string = str(payload.get("qr_string", "")).strip()
    except ValueError as exc:
        return json_error(str(exc), 400)

    if not student_id or not qr_string:
        return json_error("student_id and qr_string are required.", 400)

    try:
        rpc_response = (
            supabase.rpc(
                "process_qr_scan",
                {"p_student_id": student_id, "p_qr_string": qr_string},
            )
            .execute()
        )
    except Exception as exc:
        return json_error(f"Failed to claim QR code: {exc}", 500)

    return jsonify(rpc_response.data if hasattr(rpc_response, "data") else rpc_response)


@app.get("/api/leaderboard")
def leaderboard():
    try:
        response = (
            supabase.table("students")
            .select("student_name, current_scans")
            .order("current_scans", desc=True)
            .limit(50)
            .execute()
        )
    except Exception as exc:
        return json_error(f"Failed to fetch leaderboard: {exc}", 500)

    leaderboard_data = []
    for item in response.data or []:
        leaderboard_data.append(
            {
                "name": item.get("student_name"),
                "current_scans": item.get("current_scans", 0),
            }
        )

    return jsonify(leaderboard_data)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
