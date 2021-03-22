import json
from pathlib import Path

from config import MITRE_LABELS_JSON_PATH, PATTERNS_FILE_PATH


def create_patterns_file(mitre_labels_json_path, pattern_file_dst_path):
    with Path(mitre_labels_json_path).open("r", encoding="utf8") as f:
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
            # e.g: {"label":"INGRED","pattern":[{"lower":"red"},{"lower":"wine"}]}
            patterns.append(entry)

    jsonl = [json.dumps(pattern) for pattern in patterns]
    Path(pattern_file_dst_path).open('w', encoding='utf-8').write('\n'.join(jsonl))


if __name__ == "__main__":
    create_patterns_file(MITRE_LABELS_JSON_PATH, PATTERNS_FILE_PATH)

########################## create jsonl with only the matched lines (37956/574000) #########################

# lines = []
# with open("APT_CyberCriminal_Campagin_Collections.jsonl", "r") as fr:
#     for idx, line in enumerate(fr):
#         if idx % 1000 == 0: print(f" {len(lines)}/{idx} lines match")
#         for label in labels:
#             for fixed_pattern in mitre_labels[label]:
#                 if f" {fixed_pattern.lower()} " in line.lower() and fixed_pattern.lower() != "collection":
#                     # print(fixed_pattern, line)
#                     lines.append(line)
#                     break
#
# with open("filtered.jsonl", "w") as fw:
#     for line in lines:
#         fw.write(line)
