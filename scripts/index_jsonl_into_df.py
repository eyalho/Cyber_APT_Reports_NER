import collections
import json
from pathlib import Path
import pandas as pd
import srsly
import typer
from tqdm import tqdm


def create_df_index_of_jsonl_by_meta_and_spans(origin_labels_json, annotated_jsonl_datafile, dst_zip_path):
    labels_dict = get_origin_labels_dict(origin_labels_json)
    list_of_labels = labels_dict.keys()
    df_columns = ["git_repo", "year", "filename"] + list(list_of_labels)

    df_list_of_lists = []
    with open(annotated_jsonl_datafile, "r") as fr:
        for count_lines, _ in enumerate(fr):
            pass

    with open(annotated_jsonl_datafile, "r") as fr:
        for line in tqdm(fr, total=count_lines + 1):
            line_json = srsly.json_loads(line)
            try:
                line_text = line_json["text"]
                git_repo = line_json["meta"]["git_repo"]
                year = line_json["meta"]["year"]
                filename = line_json["meta"]["filename"]
                spans = line_json["spans"]
            except ValueError:
                raise

            spans_dict = collections.defaultdict(list)
            for span in spans:
                span_text = span["text"]
                span_label = span["label"]
                spans_dict[span_label].append(span_text)

            df_row_list = [git_repo, year, filename] + [spans_dict[label] for label in
                                                        df_columns[-len(list_of_labels):]]
            df_list_of_lists.append(df_row_list)

        df = pd.DataFrame(df_list_of_lists, columns=df_columns)
        save_zip_of_df(df, dst_zip_path)


def get_origin_labels_dict(origin_labels_json):
    with Path(origin_labels_json).open("r", encoding="utf8") as f:
        mitre_labels_dict = json.load(f)
    return mitre_labels_dict


def save_zip_of_df(df, dst_zip_path):
    """
    This file save a zip of the dataframe
    :param df: to save as file
    :param dst_file_path: path of csv/zip file
    :return: dst_zip_path: the path where the zip file was saved
    """
    dst_zip_path = Path(dst_zip_path)
    df.to_csv(dst_zip_path,
              compression=dict(method="zip", archive_name=dst_zip_path.with_suffix(".csv").name))
    return dst_zip_path


def main(origin_labels_json: str, jsonl_path: str, df_zipped_path: str):
    create_df_index_of_jsonl_by_meta_and_spans(origin_labels_json, jsonl_path, df_zipped_path)


if __name__ == "__main__":
    try:
        typer.run(main)
    except SystemExit:
        pass
