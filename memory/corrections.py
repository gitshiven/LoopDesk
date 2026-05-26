import os
import json
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

# Fall back to local file if Supabase not configured
LOCAL_FILE = "memory/corrections_store.json"

def get_client():
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None

def load_corrections() -> list:
    client = get_client()
    if client:
        try:
            res = client.table("corrections").select("*").order("created_at").execute()
            return res.data or []
        except Exception as e:
            print(f"Supabase error: {e}")
    # fallback to local
    if not os.path.exists(LOCAL_FILE):
        return []
    with open(LOCAL_FILE, "r") as f:
        return json.load(f)

def save_correction(message: str, wrong_category: str, correct_category: str, note: str = ""):
    client = get_client()
    if client:
        try:
            client.table("corrections").insert({
                "message": message,
                "wrong_category": wrong_category,
                "correct_category": correct_category,
                "note": note
            }).execute()
            print(f"Correction saved to Supabase: {wrong_category} → {correct_category}")
            return
        except Exception as e:
            print(f"Supabase error: {e}")
    # fallback to local
    corrections = load_corrections()
    corrections.append({
        "message": message,
        "wrong_category": wrong_category,
        "correct_category": correct_category,
        "note": note
    })
    with open(LOCAL_FILE, "w") as f:
        json.dump(corrections, f, indent=2)

def get_relevant_corrections(message: str) -> list:
    corrections = load_corrections()
    return corrections[-5:] if corrections else []