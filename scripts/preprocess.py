import typer
import srsly
from pathlib import Path
from spacy.util import get_words_and_spaces, filter_spans
from spacy.tokens import Doc, DocBin
import spacy


def main(
        input_path: Path = typer.Argument(..., exists=True, dir_okay=False),
        output_path: Path = typer.Argument(..., dir_okay=False), ):
    nlp = spacy.blank("en")
    doc_bin = DocBin(attrs=["ENT_IOB", "ENT_TYPE"])
    for idx, eg in enumerate(srsly.read_jsonl(input_path)):
        if idx % 10000 == 0:
            print(f"converted {idx} sentences")
        doc = nlp(eg["text"])
        spans_from_json = eg.get("spans", [])
        spans_objects = [doc.char_span(s["start"], s["end"], label=s["label"]) for s in spans_from_json]
        spans_objects = filter_spans(spans_objects)
        doc.ents = spans_objects
        doc_bin.add(doc)
    doc_bin.to_disk(output_path)
    print(f"Processed {len(doc_bin)} documents: {output_path.name}")


if __name__ == "__main__":
    typer.run(main)
