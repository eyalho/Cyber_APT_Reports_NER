import json

import spacy
import srsly
from spacy.matcher import Matcher
from spacy.tokens import Span

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
with open("patterns.jsonl", "r") as fr:
    for idx, line in enumerate(fr):
        pattern_json = srsly.json_loads(line)
        pattern = pattern_json["pattern"]
        label = pattern_json["label"]
        # pattern_name = "_".join([x["lower"] for x in pattern])
        matcher.add(label, [pattern])

with open("APT_CyberCriminal_Campagin_Collections_annotated.jsonl", "w") as fw:
    with open("APT_CyberCriminal_Campagin_Collections.jsonl", "r") as fr:
        for idx, line in enumerate(fr):
            line_json = srsly.json_loads(line)
            line_nlp = nlp(line_json["text"])
            matches = matcher(line_nlp)
            spans = []
            for match_id, start, end in matches:
                span = Span(line_nlp, start, end, label=match_id)
                print(idx, span)
                # print(span.label_, span.text, span.sent)

                span_dict = dict()
                span_dict["text"] = span.text  # same as line_nlp[start:end]
                span_dict["start"] = span.start_char
                span_dict["end"] = span.end_char
                span_dict["label"] = span.label_
                # span_dict["pattern"] = nlp.vocab.strings[match_id]  # Get string representation
                span_dict["token_start"] = span.start
                span_dict["token_end"] = span.end
                spans.append(span_dict)
                # print(span_dict)
            line_json["spans"] = spans
            fw.write(json.dumps(line_json) + "\n")


