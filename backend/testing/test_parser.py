import json
from app.services.slither_parser import parse_slither_output

with open("output.json") as f:
    raw = json.load(f)

findings = parse_slither_output(raw)

for f in findings:
    print(f)