import collections
import json
from pathlib import Path
import pandas as pd
import srsly

from config import GIT_1_ANNO_JSONL_PATH, MITRE_LABELS_JSON_PATH, DST_EXPERIMENT_ANNO_JSONL_DIR


def create_df_index_of_jsonl_by_meta_and_spans(annotated_jsonl_datafile):
    labels_dict = _get_mitre_labels_dict()
    list_of_labels = labels_dict.keys()
    df_columns = ["git_repo", "year", "filename"] + list(list_of_labels)
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

            df_row_list = [git_repo, year, filename] + [spans_dict[label] for label in
                                                        df_columns[-len(list_of_labels):]]
            df_list_of_lists.append(df_row_list)

        df = pd.DataFrame(df_list_of_lists, columns=df_columns)
        _save_zip_of_df(df, annotated_jsonl_datafile)
        #                                                         compress_type=zipfile.ZIP_DEFLATED)


def filter_to_sentences_contain_group_name(annotated_jsonl_datafile, contain_group_name_annotated_jsonl_datafile):
    index_df = _load_df_index_of_anno_jsnol_file(annotated_jsonl_datafile)
    only_contain_group_name_df = index_df[index_df["group_name"] != str([])]
    print(f"Found {only_contain_group_name_df.shape[0]} lines with group_names")
    # _save_zip_of_df(only_contain_group_name_df, Path(contain_group_name_annotated_jsonl_datafile).parent,
    #                 "only_contain_group_name_df")
    _save_zip_of_df(only_contain_group_name_df, contain_group_name_annotated_jsonl_datafile)

    with open(contain_group_name_annotated_jsonl_datafile, "w") as fw:
        with open(annotated_jsonl_datafile, "r") as fr:
            for idx, line in enumerate(fr):
                if idx in only_contain_group_name_df.index:
                    fw.write(line)


def split_by_year(annotated_jsonl_datafile, exp_dir, max_year_for_train):
    index_df = _load_df_index_of_anno_jsnol_file(annotated_jsonl_datafile)
    train_df = index_df[index_df.year <= max_year_for_train]
    test_df = index_df[index_df.year > max_year_for_train]

    train_jsonl_path = Path(exp_dir) / f"train_until_{max_year_for_train}.jsonl"
    test_jsonl_path = Path(exp_dir) / f"test_from_{max_year_for_train + 1}.jsonl"

    # save experiment index into csv-zip
    _save_zip_of_df(train_df, train_jsonl_path)
    _save_zip_of_df(test_df, test_jsonl_path)

    print(f"train years {sorted(list(train_df.year.unique()))}")
    print(f"test years {sorted(list(test_df.year.unique()))}")

    _save_split_train_test_jsonl(annotated_jsonl_datafile, train_jsonl_path, test_jsonl_path, train_df, test_df)


def split_by_group_name(annotated_jsonl_datafile, exp_dir, train_group_names, test_group_names):
    train_jsonl_path = Path(exp_dir) / f"train_by_names.jsonl"
    test_jsonl_path = Path(exp_dir) / f"test_by_names.jsonl"
    info_train_str = f"train_group_names({len(train_group_names)}): {train_group_names}"
    info_test_str = f"train_group_names({len(test_group_names)}): {test_group_names}"
    f = open(exp_dir / "describe.txt", "w")
    f.write(info_train_str + "\n")
    f.write(info_test_str + "\n")
    print(info_train_str)
    print(info_test_str)

    only_contain_group_name_df = _load_df_index_of_anno_jsnol_file(annotated_jsonl_datafile)
    only_contain_group_name_df["group_name"] = only_contain_group_name_df["group_name"].apply(eval)

    def is_in_valid_names(names, valid_names):
        for name in names:
            if name in valid_names:
                return True
        return False

    only_contain_group_name_df["is_train"] = only_contain_group_name_df["group_name"].apply(
        lambda groups_list: is_in_valid_names(groups_list, train_group_names))
    # only_contain_group_name_df["is_test"] = only_contain_group_name_df["group_name"].apply(lambda groups_list: is_in_valid_names(groups_list, test_group_names))

    train_df = only_contain_group_name_df[only_contain_group_name_df["is_train"]]
    test_df = only_contain_group_name_df[~only_contain_group_name_df["is_train"]]
    all_size = only_contain_group_name_df.shape[0]
    train_size = train_df.shape[0]
    test_size = test_df.shape[0]
    assert train_size + test_size == all_size
    split_info = f"split_by_group_name:" \
                 f" train({train_size}):test({test_size}) ({train_size / all_size:.2f}:{test_size / all_size:.2f})"
    print(split_info)
    f.write(split_info + "\n")
    f.close()

    _save_split_train_test_jsonl(annotated_jsonl_datafile, train_jsonl_path, test_jsonl_path, train_df, test_df)
    _save_zip_of_df(train_df, train_jsonl_path)
    _save_zip_of_df(test_df, test_jsonl_path)


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


def _save_split_train_test_jsonl(annotated_jsonl_datafile, train_jsonl_path, test_jsonl_path, train_df, test_df):
    print(f"split {annotated_jsonl_datafile} into:\n - {train_jsonl_path}\n - {test_jsonl_path}")
    with open(annotated_jsonl_datafile, "r") as f_all:
        with open(train_jsonl_path, "w") as f_train:
            with open(test_jsonl_path, "w") as f_test:
                for idx, line in enumerate(f_all):
                    if idx in train_df.index:
                        f_train.write(line)
                    elif idx in test_df.index:
                        f_test.write(line)
                    else:
                        raise ValueError(f"idx({idx}) not in train and not in test")


if __name__ == "__main__":
    # create index_df
    create_df_index_of_jsonl_by_meta_and_spans(GIT_1_ANNO_JSONL_PATH)

    # exp1 - all labels, all data split by years
    exp_dir = DST_EXPERIMENT_ANNO_JSONL_DIR / "exp1"
    exp_dir.mkdir(exist_ok=True, parents=True)
    print(f"create dir {exp_dir}")
    split_by_year(GIT_1_ANNO_JSONL_PATH, exp_dir, 2016)

    # create smaller dev dataset with only lines contained some group_name
    contain_group_name_annotated_jsonl_datafile = DST_EXPERIMENT_ANNO_JSONL_DIR / "only_contain_group_name" / "only_contain_group_name.jsonl"
    contain_group_name_annotated_jsonl_datafile.parent.mkdir(exist_ok=True, parents=True)
    filter_to_sentences_contain_group_name(GIT_1_ANNO_JSONL_PATH, contain_group_name_annotated_jsonl_datafile)

    # exp2 - only_contain_group_name, split_by_group_name 80 20
    # exp3 - all labels, split_by_group_name 80 20
    contain_group_name_annotated_jsonl_datafile = DST_EXPERIMENT_ANNO_JSONL_DIR / "only_contain_group_name" / "only_contain_group_name.jsonl"
    exp_dir = DST_EXPERIMENT_ANNO_JSONL_DIR / "exp2"
    exp_dir.mkdir(exist_ok=True, parents=True)
    mitre_labels = _get_mitre_labels_dict()
    group_names = mitre_labels["group_name"]
    train_group_names = group_names[:int(len(group_names) * 0.8)]
    test_group_names = group_names[int(len(group_names) * 0.8):]
    split_by_group_name(contain_group_name_annotated_jsonl_datafile, exp_dir, train_group_names, test_group_names)

    exp_dir = DST_EXPERIMENT_ANNO_JSONL_DIR / "exp3"
    exp_dir.mkdir(exist_ok=True, parents=True)
    split_by_group_name(GIT_1_ANNO_JSONL_PATH, exp_dir, train_group_names, test_group_names)
