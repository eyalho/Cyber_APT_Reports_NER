import collections
import json
from pathlib import Path
import pandas as pd
import srsly
from tqdm import tqdm

from config import GIT_1_ANNO_JSONL_PATH, MITRE_LABELS_JSON_PATH, DST_EXPERIMENT_ANNO_JSONL_DIR, \
    GIT_1_DEV_ANNO_JSONL_PATH


def create_df_index_of_jsonl_by_meta_and_spans(annotated_jsonl_datafile):
    labels_dict = _get_mitre_labels_dict()
    list_of_labels = labels_dict.keys()
    df_columns = ["git_repo", "year", "filename"] + list(list_of_labels)
    print(df_columns)

    df_list_of_lists = []
    with open(annotated_jsonl_datafile, "r") as fr:
        for idx, line in enumerate(fr):
            if idx % 100000 == 0:
                print("create_df_index: line =", idx)
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
                span_text = str(span["text"]).lower()  # save just lower-case values
                span_label = span["label"]
                spans_dict[span_label].append(span_text)

            df_row_list = [git_repo, year, filename] + [spans_dict[label] for label in
                                                        df_columns[-len(list_of_labels):]]
            df_list_of_lists.append(df_row_list)

        df = pd.DataFrame(df_list_of_lists, columns=df_columns)
        _save_zip_of_df(df, annotated_jsonl_datafile)
        _save_zip_of_df(df, "index_df.zip")


def filter_to_sentences_contain_group_name(annotated_jsonl_datafile, contain_group_name_annotated_jsonl_datafile):
    index_df = _load_df_index_of_anno_jsnol_file(annotated_jsonl_datafile)
    only_contain_group_name_df = index_df[index_df["group_name"] != str([])]
    print(f"Found {only_contain_group_name_df.shape[0]} lines with group_names")
    _save_zip_of_df(only_contain_group_name_df, contain_group_name_annotated_jsonl_datafile)

    with open(contain_group_name_annotated_jsonl_datafile, "w") as fw:
        with open(annotated_jsonl_datafile, "r") as fr:
            for idx, line in enumerate(fr):
                if idx in only_contain_group_name_df.index:
                    fw.write(line)


def split_by_year(annotated_jsonl_datafile, exp_dir, max_year_for_train):
    train_jsonl_path = Path(exp_dir) / f"train_until_{max_year_for_train}.jsonl"
    test_jsonl_path = Path(exp_dir) / f"test_from_{max_year_for_train + 1}.jsonl"
    index_df = _load_df_index_of_anno_jsnol_file(annotated_jsonl_datafile)

    # train-test split
    index_df["is_train"] = index_df.year <= max_year_for_train
    index_df["is_test"] = index_df.year > max_year_for_train

    print(f"train years {sorted(list(index_df[index_df['is_train']].year.unique()))}")
    print(f"test years {sorted(list(index_df[index_df['is_test']].year.unique()))}")

    _save_split_train_test_jsonl(annotated_jsonl_datafile, train_jsonl_path, test_jsonl_path, index_df)


def dev_split_by_group_name(annotated_jsonl_datafile, exp_dir, train_group_names, test_group_names):
    """
        The dataset would become really small -> Useful for development
        Test include only sentences with test_group_names
        Train include only sentences with train_group_names
    """
    train_jsonl_path = Path(exp_dir) / f"train_by_names.jsonl"
    test_jsonl_path = Path(exp_dir) / f"test_by_names.jsonl"
    # make sure labels are lower-case only
    train_group_names = list(pd.unique([str(name).lower() for name in train_group_names]))
    test_group_names = list(pd.unique([str(name).lower() for name in test_group_names]))
    info_train_str = f"train_group_names({len(train_group_names)}): {train_group_names}"
    info_test_str = f"test_group_names({len(test_group_names)}): {test_group_names}"
    with open(exp_dir / "describe.txt", "w") as f:
        f.write(info_train_str + "\n")
        f.write(info_test_str + "\n")
    print(info_train_str)
    print(info_test_str)

    index_df = _load_df_index_of_anno_jsnol_file(annotated_jsonl_datafile)
    index_df["group_name"] = index_df["group_name"].apply(eval)

    def is_in_valid_names_only(names, valid_names, invalid_names):
        names = [name.lower() for name in names]
        valid_names = [name.lower() for name in valid_names]
        invalid_names = [name.lower() for name in invalid_names]
        for name in names:
            if name in valid_names:
                # Contain valid name :)
                # just check it doesn't contain an invalid name too
                for name in names:
                    if name in invalid_names:
                        return False
                return True
        return False

    index_df["is_train"] = index_df["group_name"].apply(
        lambda groups_list: is_in_valid_names_only(groups_list, train_group_names, test_group_names))
    index_df["is_test"] = index_df["group_name"].apply(
        lambda groups_list: is_in_valid_names_only(groups_list, test_group_names, train_group_names))

    _save_split_train_test_jsonl(annotated_jsonl_datafile, train_jsonl_path, test_jsonl_path, index_df)


def _get_mitre_labels_dict():
    with Path(MITRE_LABELS_JSON_PATH).open("r", encoding="utf8") as f:
        mitre_labels_dict = json.load(f)
    return mitre_labels_dict


def _series_of_lists_to_1d_series(series_of_lists):
    """
    When we have a series of lists [["a","b"], ["b","c","a"],..]
    Normal value_counts() won't count occurances of each label but of combination.
    So, one simple way to count is to use:
    to_1D(series_of_lists).value_counts()
    """
    return pd.Series([x for _list in series_of_lists for x in _list])


def _save_zip_of_df(df, dst_file_path):
    """
    This file save a zip of the dataframe
    :param df: to save as file
    :param dst_file_path: path of csv/zip file
    :return: dst_zip_path: the path where the zip file was saved
    """
    dst_file_path = Path(dst_file_path)
    file_stem = f"{dst_file_path.stem}_df"
    dst_zip_path = dst_file_path.parent / Path(file_stem).with_suffix(".zip")
    dst_archive_name = Path(file_stem).with_suffix(".csv")
    print(f"save {dst_zip_path} ({dst_archive_name})")
    df.to_csv(dst_zip_path,
              compression=dict(method="zip", archive_name=str(dst_archive_name)))
    return dst_zip_path


def _load_df_index_of_anno_jsnol_file(anno_jsnol_file_path):
    anno_jsnol_file_path = Path(anno_jsnol_file_path)
    file_stem = f"{anno_jsnol_file_path.stem}_df"
    dst_zip_path = anno_jsnol_file_path.parent / Path(file_stem).with_suffix(".zip")
    if not dst_zip_path.is_file():
        create_df_index_of_jsonl_by_meta_and_spans(anno_jsnol_file_path)
    return pd.read_csv(dst_zip_path)


def _save_split_train_test_jsonl(annotated_jsonl_datafile, train_jsonl_path, test_jsonl_path, train_test_df):
    count_excluded_lines = 0
    train_df = train_test_df[train_test_df["is_train"]]
    test_df = train_test_df[train_test_df["is_test"]]
    all_size = train_test_df.shape[0]
    train_size = train_df.shape[0]
    test_size = test_df.shape[0]
    print(f"{train_size=}, {test_size=}, {all_size=} (Exclude {all_size - test_size - train_size} lines)")
    print(f"split: ({train_size}):test({test_size}) ({train_size / all_size:.2f}:{test_size / all_size:.2f})")

    # save experiment index into csv-zip
    _save_zip_of_df(train_df, train_jsonl_path)
    _save_zip_of_df(test_df, test_jsonl_path)

    print(f"split {annotated_jsonl_datafile} into:\n - {train_jsonl_path}\n - {test_jsonl_path}")
    with open(annotated_jsonl_datafile, "r") as f_all:
        with open(train_jsonl_path, "w") as f_train:
            with open(test_jsonl_path, "w") as f_test:
                for idx, line in enumerate(tqdm(f_all, total=train_test_df.shape[0])):
                    if idx in train_df.index:
                        f_train.write(line)
                    elif idx in test_df.index:
                        f_test.write(line)
                    else:
                        count_excluded_lines += 1
    if count_excluded_lines > 0:
        print(f" ---- Exclude {count_excluded_lines} lines (by split decisions) ----")


if __name__ == "__main__":
    # create index_df
    create_df_index_of_jsonl_by_meta_and_spans(GIT_1_ANNO_JSONL_PATH)

    # create a smaller dev dataset with only lines contained some group_name
    filter_to_sentences_contain_group_name(GIT_1_ANNO_JSONL_PATH, GIT_1_DEV_ANNO_JSONL_PATH)

    # exp1 - Full dataset split by years
    exp_dir = DST_EXPERIMENT_ANNO_JSONL_DIR / "full_dataset_split_by_years"
    exp_dir.mkdir(exist_ok=True, parents=True)
    print(f"create dir {exp_dir}")
    split_by_year(GIT_1_ANNO_JSONL_PATH, exp_dir, 2016)

    # exp2 - Only the dev, split_by_group_name 80 20
    exp_dir = DST_EXPERIMENT_ANNO_JSONL_DIR / "dev_dataset_split_by_names"
    exp_dir.mkdir(exist_ok=True, parents=True)
    mitre_labels = _get_mitre_labels_dict()
    group_names = mitre_labels["group_name"]
    train_group_names = group_names[:int(len(group_names) * 0.8)]
    test_group_names = group_names[int(len(group_names) * 0.8):]
    dev_split_by_group_name(GIT_1_DEV_ANNO_JSONL_PATH, exp_dir, train_group_names, test_group_names)
