import json
import re
from pathlib import Path

structured_path = "../clients/poway/data/poway_knowledge_base.json"
output_path = "../clients/poway/data/poway_knowledge_base_structured.json"

with open(structured_path, "r", encoding="utf-8") as f:
    data = json.load(f)

flattened = []

# Regex pattern to extract Q&A pairs
qa_pattern = re.compile(r"Q:\s*(.*?)\s*A:\s*(.*?)(?=(\nQ:|\Z))", re.DOTALL)

for entry in data:
    matches = qa_pattern.findall(entry["content"])
    for q, a, _ in matches:
        flattened.append({
            "question": q.strip(),
            "answer": a.strip()
        })

# Write to flat file
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(flattened, f, indent=2)

print(f"Flattened {len(flattened)} Q&A pairs to {output_path}")
