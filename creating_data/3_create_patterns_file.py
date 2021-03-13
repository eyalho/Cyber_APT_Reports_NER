import json
from pathlib import Path

with Path("creating_data/MITRE_labels.json").open("r", encoding="utf8") as f:
    mitre_labels = json.load(f)

labels = mitre_labels.keys()

patterns = []
for label in labels:
    print(f"Create a pattern for label={label} with {len(mitre_labels[label])} fixed values")
    for fixed_pattern in mitre_labels[label]:
        pattern = []
        for word in fixed_pattern.split(" "):
            pattern.append({'lower': word.lower()})
        entry = {'label': label, 'pattern': pattern}
        # print(entry)
        # {"label":"INGRED","pattern":[{"lower":"red"},{"lower":"wine"},{"lower":"vinegar"}]}
        patterns.append(entry)

jsonl = [json.dumps(pattern) for pattern in patterns]
Path('creating_data/patterns.jsonl').open('w', encoding='utf-8').write('\n'.join(jsonl))

########################## create jsonl with only the matched lines (37956/574000) #########################

lines = []
with open("APT_CyberCriminal_Campagin_Collections.jsonl", "r") as fr:
    for idx, line in enumerate(fr):
        if idx % 1000 == 0: print(f" {len(lines)}/{idx} lines match")
        for label in labels:
            for fixed_pattern in mitre_labels[label]:
                if f" {fixed_pattern.lower()} " in line.lower() and fixed_pattern.lower() != "collection":
                    # print(fixed_pattern, line)
                    lines.append(line)
                    break

with open("filtered.jsonl", "w") as fw:
    for line in lines:
        fw.write(line)
