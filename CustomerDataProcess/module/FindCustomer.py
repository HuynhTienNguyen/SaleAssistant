import re
import unicodedata
from rapidfuzz import process, fuzz

def normalize_text(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def find_customer_matches(
    user_query: str,
    customer_names: list[str],
    threshold: int = 50,
    limit: int = 5
):
    normalized_customers = {
        name: normalize_text(name)
        for name in customer_names
    }

    query_norm = normalize_text(user_query)

    matches = process.extract(
        query_norm,
        normalized_customers.values(),
        scorer=fuzz.token_set_ratio,
        limit=limit
    )

    results = []

    for match, score, _ in matches:
        if score < threshold:
            continue

        for original, norm in normalized_customers.items():
            if norm == match:
                results.append({
                    "customer_id": original,
                    "confidence": score
                })
                break

    return results if results else []
