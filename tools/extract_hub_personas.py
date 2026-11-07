import json
import urllib.request

url = "https://datasets-server.huggingface.co/rows?dataset=nvidia/Nemotron-Personas-El-Salvador&config=default&split=train&offset=0&limit=50"
req = urllib.request.Request(url, headers={"User-Agent": "GameForge-Client/1.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

target_uuids = {
    "108fefeb-c9f6-4429-8ce1-a67eaad444ef": "merchant",      # Rosa, 39, La Libertad - Comercio
    "2e2bca1d-f265-4214-beb3-858d676f2907": "blacksmith",    # José, 51, Santa Ana - Construcción / Forja
    "0b125a4d-c467-4cc5-8789-968ae1ba7f01": "elder",         # Don Antonio, 88, Santa Ana - Sabio / Medicina
}

extracted = {
    "dataset": "nvidia/Nemotron-Personas-El-Salvador",
    "source_url": "https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador",
    "license": "CC-BY-4.0",
    "attribution": "NVIDIA Sovereign AI Initiative & WideLabs / El Salvador National Demographics",
    "personas": {}
}

for r in data["rows"]:
    row = r["row"]
    uuid = row["uuid"]
    if uuid in target_uuids:
        role = target_uuids[uuid]
        extracted["personas"][role] = {
            "uuid": uuid,
            "role": role,
            "department": row["department"],
            "municipality": row["municipality"],
            "age": row["age"],
            "sex": row["sex"],
            "occupation": row["occupation"],
            "professional_persona": row["professional_persona"],
            "cultural_background": row["cultural_background"],
            "culinary_persona": row["culinary_persona"],
            "skills": row["skills_and_expertise_list"],
        }

with open("game/data/personas_el_salvador.json", "w", encoding="utf-8") as f:
    json.dump(extracted, f, indent=2, ensure_ascii=False)

print("Extracted personas count:", len(extracted["personas"]))
for k, v in extracted["personas"].items():
    print(f"Role: {k} | UUID: {v['uuid']} | Dept: {v['department']} | Age: {v['age']}")
