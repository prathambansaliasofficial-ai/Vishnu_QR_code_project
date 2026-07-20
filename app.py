import os
from flask import Flask, abort, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Please set SUPABASE_URL and SUPABASE_KEY in your environment or .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/verify/<qr_string>")
def verify_qr(qr_string: str):
    response = (
        supabase.table("vishnu_codes")
        .select("vishnu_name")
        .eq("qr_string", qr_string)
        .limit(1)
        .execute()
    )

    data = response.data
    if not data:
        abort(404)

    vishnu_name = data[0].get("vishnu_name")
    return render_template("index.html", vishnu_name=vishnu_name)


@app.route("/")
def index():
    return "QR verification app is running. Use /verify/<qr_string> to verify a code."


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
