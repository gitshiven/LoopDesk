import json
import os

CORRECTIONS_FILE = "memory/corrections_store.json"

def load_corrections() -> list:
    if not os.path.exists(CORRECTIONS_FILE):
        return []
    with open(CORRECTIONS_FILE, "r") as f:
        return json.load(f)

def save_correction(message: str, wrong_category: str, correct_category: str, note: str = ""):
    corrections = load_corrections()
    corrections.append({
        "message": message,
        "wrong_category": wrong_category,
        "correct_category": correct_category,
        "note": note
    })
    with open(CORRECTIONS_FILE, "w") as f:
        json.dump(corrections, f, indent=2)
    print(f"Correction saved: {wrong_category} → {correct_category}")

def get_relevant_corrections(message: str) -> list:
    corrections = load_corrections()
    # Return last 5 corrections as few-shot examples
    return corrections[-5:] if corrections else []