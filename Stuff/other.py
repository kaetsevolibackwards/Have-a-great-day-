with open("message.txt", "r", encoding="utf-8") as file:
    raw = file.read()

# Try to parse as JSON message (new format), otherwise print raw text
try:
    import json
    data = json.loads(raw)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception:
    print(raw)
