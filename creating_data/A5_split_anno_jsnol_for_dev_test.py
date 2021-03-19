import collections
import json
import zipfile
from pathlib import Path
import pandas as pd
import srsly

from config import GIT_1_ANNO_JSONL_PATH, MITRE_LABELS_JSON_PATH, DST_EXPERIMENT_ANNO_JSONL_DIR

DF_INDEX_CSV_FILE_PATH = Path("index.csv")
DF_INDEX_ZIP_FILE_PATH = Path("index.zip")


def _get_labels():
    with Path(MITRE_LABELS_JSON_PATH.name).open("r", encoding="utf8") as f:
        mitre_labels = json.load(f)
        list_of_labels = mitre_labels.keys()
        return list_of_labels


def index_jsonl_by_meta_and_spans(annotated_jsonl_datafile):
    # df = pd.DataFrame(columns=('col1', 'col2', 'col3'))
    labels = _get_labels()
    df_columns = ["git_repo", "year", "filename"] + list(labels)
    print(df_columns)

    df_list_of_lists = []
    with open(annotated_jsonl_datafile, "r") as fr:
        for idx, line in enumerate(fr):
            if idx % 100000 == 0:
                print(idx)
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

            df_row_list = [git_repo, year, filename] + [spans_dict[label] for label in df_columns[-len(labels):]]
            df_list_of_lists.append(df_row_list)

        df = pd.DataFrame(df_list_of_lists, columns=df_columns)
        df.to_csv(DF_INDEX_CSV_FILE_PATH)
        zipfile.ZipFile(DF_INDEX_ZIP_FILE_PATH, mode='w').write(DF_INDEX_CSV_FILE_PATH,
                                                                compress_type=zipfile.ZIP_DEFLATED)


def stat_index_df(df):
    pass


def split_jsonl_dataset_by_year(max_year_for_train, annotated_jsonl_datafile, train_jsonl_path, test_jsonl_path):
    index_df = pd.read_csv(DF_INDEX_CSV_FILE_PATH)
    train_df = index_df[index_df.year <= max_year_for_train]
    test_df = index_df[index_df.year > max_year_for_train]

    # save experiment index into csv-zip
    train_df.to_csv(Path(train_jsonl_path).parent / "train_df.csv.zip",
                    compression=dict(method="zip", archive_name=f"train_df.csv"))
    test_df.to_csv(Path(train_jsonl_path).parent / "test_df.csv.zip",
                   compression=dict(method="zip", archive_name=f"test_df.csv"))

    print(f"train years {sorted(list(train_df.year.unique()))}")
    print(f"test years {sorted(list(test_df.year.unique()))}")
    with open(train_jsonl_path, "w") as f_train:
        with open(test_jsonl_path, "w") as f_test:
            with open(annotated_jsonl_datafile, "r") as fr:
                for idx, line in enumerate(fr):
                    if idx in train_df.index:
                        f_train.write(line)
                    elif idx in test_df.index:
                        f_test.write(line)
                    else:
                        raise ValueError(f"idx({idx}) not in train and not in test")


def _save_zip_of_df(df, dir_path, file_name):
    dst_zip_path = Path(dir_path) / Path(file_name).with_suffix(".csv.zip")
    dst_archive_name = Path(file_name).with_suffix(".csv")
    print(f"save {dst_zip_path} ({dst_archive_name})")
    df.to_csv(dst_zip_path,
              compression=dict(method="zip", archive_name=str(dst_archive_name)))


def filter_to_sentences_contain_group_name(annotated_jsonl_datafile, contain_group_name_annotated_jsonl_datafile):
    index_df = pd.read_csv(DF_INDEX_CSV_FILE_PATH)
    only_contain_group_name_df = index_df[index_df["group_name"] != str([])]
    print(f"Found {only_contain_group_name_df.shape[0]} lines with group_names")
    _save_zip_of_df(only_contain_group_name_df, Path(contain_group_name_annotated_jsonl_datafile).parent,
                    "only_contain_group_name_df")
    with open(contain_group_name_annotated_jsonl_datafile, "w") as fw:
        with open(annotated_jsonl_datafile, "r") as fr:
            for idx, line in enumerate(fr):
                if idx in only_contain_group_name_df.index:
                    fw.write(line)


if __name__ == "__main__":
    # index_jsonl_by_meta_and_spans(GIT_1_ANNO_JSONL_PATH)

    # exp1 - all labels, all data split by years
    # train_jsonl_path = DST_EXPERIMENT_ANNO_JSONL_DIR / "exp1" / "train_until_2016.jsonl"
    # test_jsonl_path = DST_EXPERIMENT_ANNO_JSONL_DIR / "exp1" / "test_from_2017.jsonl"
    # train_jsonl_path.parent.mkdir(exist_ok=True, parents=True)
    # test_jsonl_path.parent.mkdir(exist_ok=True, parents=True)
    # split_jsonl_dataset_by_year(2016, GIT_1_ANNO_JSONL_PATH, train_jsonl_path, test_jsonl_path)

    # create smaller dev dataset with only lines contained some group_name
    contain_group_name_annotated_jsonl_datafile = DST_EXPERIMENT_ANNO_JSONL_DIR / "only_contain_group_name" / "only_contain_group_name.jsonl"
    contain_group_name_annotated_jsonl_datafile.parent.mkdir(exist_ok=True, parents=True)
    filter_to_sentences_contain_group_name(GIT_1_ANNO_JSONL_PATH, contain_group_name_annotated_jsonl_datafile)
