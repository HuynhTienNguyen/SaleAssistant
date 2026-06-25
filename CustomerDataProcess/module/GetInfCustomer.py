from flask import Flask, request, jsonify
from flask_cors import CORS
from DataProcessing import preprocess_data
from JsonGenerate import build_customer_context_and_history
from FindCustomer import find_customer_matches
import re
import unicodedata
from rapidfuzz import process, fuzz

app = Flask(__name__)
CORS(app)

PANEL = preprocess_data()

@app.route("/customers/resolve", methods=["POST"])
def resolve_customer():
    user_text = request.json.get("query", "")
    print(f"user_text: {user_text}")

    customer_names = PANEL["customer_id"].unique().tolist()

    matches = find_customer_matches(user_text, customer_names)
    print(f"matches: {matches}")

    if not matches:
        return jsonify({
            "found": False,
            "reason": "No confident match"
        })

    customers = []

    for m in matches:
        customer_json = build_customer_context_and_history(
            PANEL,
            m["customer_id"]
        )

        customers.append({
            "customer_id": m["customer_id"],
            "confidence": m["confidence"],
            "profile": customer_json
        })

    auto_selected = len(customers) == 1

    return jsonify({
        "found": True,
        "auto_selected": auto_selected,
        "customers": customers
    })



@app.route("/customers/profile", methods=["POST"])
def get_customer_profile():
    data = request.get_json()
    customer_id = data.get("customer_id")

    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    customer_info = build_customer_context_and_history(
        PANEL,
        customer_id
    )

    return jsonify(customer_info)

@app.route("/customers/all", methods=["GET"])
def get_all_customer_inf():
    ids = PANEL["customer_id"].unique().tolist()
    all_customer_info = []

    for customer_id in ids:
        customer_info = build_customer_context_and_history(
            PANEL,
            customer_id
        )
        all_customer_info.append(customer_info)

    return jsonify(all_customer_info)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
