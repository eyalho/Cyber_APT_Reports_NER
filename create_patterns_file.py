import json
from pathlib import Path

with Path("MITRE_labels.json").open("r", encoding="utf8") as f:
    mitre_labels = json.load(f)

labels = mitre_labels.keys()

patterns = []
for label in labels:
    print(f"Create a pattern for label={label} with {len(mitre_labels[label])} fixed values")
    for fixed_pattern in mitre_labels[label]:
        pattern = []
        for word in fixed_pattern.split(" "):
            pattern.append({'lower': word})
        entry = {'label': label, 'pattern': pattern}
        # print(entry)
        # {"label":"INGRED","pattern":[{"lower":"red"},{"lower":"wine"},{"lower":"vinegar"}]}
        patterns.append(entry)

jsonl = [json.dumps(pattern) for pattern in patterns]
Path('patterns.jsonl').open('w', encoding='utf-8').write('\n'.join(jsonl))

# ######################### create pattern based on exsiting dataset #########################
# import json
#
# import spacy
# from pathlib import Path
#
# import srsly
#
# texts = []  # your corpus
#
# with Path("example_test.jsonl").open("r", encoding="utf8") as f:
#     for line in f:
#         texts.append(srsly.json_loads(line)["text"])
#
# # patterns = []  # collect patterns here
#
# nlp = spacy.load('en_core_web_sm')  # or any other model
# docs = nlp.pipe(texts)  # use nlp.pipe for efficiency
# for doc in docs:
#     for ent in doc.ents:
#         entry = {'label': ent.label_, 'pattern': [{'lower': ent.text}]}
#         print(entry)
#         patterns.append(entry)
#
# # dump JSON and write patterns to file
# jsonl = [json.dumps(pattern) for pattern in patterns]
# Path('patterns.jsonl').open('w', encoding='utf-8').write('\n'.join(jsonl))
