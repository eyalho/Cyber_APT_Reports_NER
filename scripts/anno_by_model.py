import json
from pathlib import Path

import spacy
import srsly
import typer
from spacy.tokens import Span
from spacy.util import filter_spans
from tqdm import tqdm


def _spans_to_spans_dicts_list(spans):
    # print(span.label_, span.text, span.sent)
    spans_dicts_list = []
    for span in spans:
        span_dict = dict()
        span_dict["text"] = span.text  # same as line_nlp[start:end]
        span_dict["start"] = span.start_char
        span_dict["end"] = span.end_char
        span_dict["label"] = span.label_
        span_dict["token_start"] = span.start
        span_dict["token_end"] = span.end
        spans_dicts_list.append(span_dict)
    return spans_dicts_list


def main(model: str, origin_jsonl_path: str, label_by_model_jsonl_path: str):
    nlp = spacy.load(model)
    origin_jsonl_path = Path(origin_jsonl_path)
    label_by_model_jsonl_path = Path(label_by_model_jsonl_path)
    print(f"annotate with {model}:\n{origin_jsonl_path}->{label_by_model_jsonl_path}")
    with open(label_by_model_jsonl_path, "w") as fw:
        with open(origin_jsonl_path, "r") as fr:
            for count_lines, _ in enumerate(tqdm(fr)):
                pass
        with open(origin_jsonl_path, "r") as fr:
            for idx, line in enumerate(tqdm(fr, total=count_lines + 1)):
                line_json = srsly.json_loads(line)
                line_json["spans"] = list()  # delete any existing spans (labels)
                line_nlp = nlp(line_json["text"])
                spans = []
                for ent in line_nlp.ents:
                    span = Span(line_nlp, ent.start, ent.end, label=ent.label_)
                    spans.append(span)
                spans = filter_spans(spans)  # useless line, NER model should not output problematic spans
                # if spans:
                #     print(f"{idx}, spans({len(spans)}):{spans}")
                spans_dicts_list = _spans_to_spans_dicts_list(spans)
                line_json["spans"] = spans_dicts_list
                fw.write(json.dumps(line_json) + "\n")


if __name__ == "__main__":
    try:
        typer.run(main)
    except SystemExit:
        pass
