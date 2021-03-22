import json

import spacy
import srsly
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.util import filter_spans

from config import PATTERNS_FILE_PATH, GIT_1_JSONL_PATH, GIT_1_ANNO_JSONL_PATH


def _spans_to_spans_dicts_list(spans):
    # print(span.label_, span.text, span.sent)
    spans_dicts_list = []
    for span in spans:
        span_dict = dict()
        span_dict["text"] = span.text  # same as line_nlp[start:end]
        span_dict["start"] = span.start_char
        span_dict["end"] = span.end_char
        span_dict["label"] = span.label_
        # span_dict["pattern"] = nlp.vocab.strings[match_id]  # Get string representation
        span_dict["token_start"] = span.start
        span_dict["token_end"] = span.end
        spans_dicts_list.append(span_dict)
    return spans_dicts_list


def create_a_labeled_jsonl_dataset(pattern_file_path, jsonl_datafile, annotated_jsonl_datafile):
    nlp = spacy.load("en_core_web_sm")
    matcher = Matcher(nlp.vocab)
    with open(pattern_file_path, "r") as fr:
        for idx, line in enumerate(fr):
            pattern_json = srsly.json_loads(line)
            pattern = pattern_json["pattern"]
            label = pattern_json["label"]
            # pattern_name = "_".join([x["lower"] for x in pattern])
            matcher.add(label, [pattern])

    with open(annotated_jsonl_datafile, "w") as fw:
        with open(jsonl_datafile, "r") as fr:
            for idx, line in enumerate(fr):
                line_json = srsly.json_loads(line)
                line_nlp = nlp(line_json["text"])
                matches = matcher(line_nlp)
                spans = []
                for match_id, start, end in matches:
                    span = Span(line_nlp, start, end, label=match_id)
                    spans.append(span)
                spans = filter_spans(spans)
                if spans:
                    print(f"{idx}, spans({len(spans)}):{spans}")
                spans_dicts_list = _spans_to_spans_dicts_list(spans)

                line_json["spans"] = spans_dicts_list
                fw.write(json.dumps(line_json) + "\n")


if __name__ == "__main__":
    # PATTERNS_FILE_PATH = "creating_data/patterns.jsonl"
    # DATASET_DIR = Path("/home/eyal/dev/nlp_datasets")
    # JSONL_DATAFILE = DATASET_DIR / "APT_CyberCriminal_Campagin_Collections.jsonl"
    # ANNOTATED_JSONL_DATAFILE = DATASET_DIR / "ANNO_APT_CyberCriminal_Campagin_Collections.jsonl"
    GIT_1_ANNO_JSONL_PATH.parent.mkdir(exist_ok=True, parents=True)
    create_a_labeled_jsonl_dataset(PATTERNS_FILE_PATH.name, GIT_1_JSONL_PATH, GIT_1_ANNO_JSONL_PATH)
