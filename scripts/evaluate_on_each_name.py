from pathlib import Path
import pandas as pd
import typer
from spacy.scorer import PRFScore

from collections import Counter


def _count_names(df: pd.DataFrame, col_name: str):
    names = df[col_name]
    try:
        names = names.apply(eval)
    except TypeError:
        pass
    counter = Counter([x for _list in names for x in _list])
    return counter


def _get_lower_names(counter: Counter):
    return {name.lower() for name in counter.keys()}


def evaluate_each_name(gold_df_path: str, by_model_df_path: str, output_path: str):
    entity_type = "group_name"

    gold_df = pd.read_csv(gold_df_path)
    cand_df = pd.read_csv(by_model_df_path)

    gold_counter = _count_names(gold_df, entity_type)
    gold_names = _get_lower_names(gold_counter)

    cand_counter = _count_names(cand_df, entity_type)
    cand_names = _get_lower_names(cand_counter)

    all_names = cand_names.union(gold_names)

    print(f"{entity_type}: {len(gold_names)=}")
    print(f"{entity_type}: {len(cand_names)=}")
    print(f"{entity_type}: {len(gold_names-cand_names)=}")
    print(f"{entity_type}: {len(cand_names-gold_names)=}")
    print(f"{entity_type} {len(all_names)=}")
    # slice into interesting lines only -> than create a column for each name the dataset was labeled by
    print(f"{gold_df.shape=}, {cand_df.shape=}")
    assert gold_df.shape[0] == cand_df.shape[0]
    gold_names_series = gold_df.copy()
    gold_names_series = gold_names_series[
        (gold_df[entity_type] != "[]") |
        (cand_df[entity_type] != "[]")
        ]
    gold_names_series = gold_names_series[entity_type]

    cand_names_series = cand_df.copy()
    cand_names_series = cand_names_series[
        (gold_df[entity_type] != "[]") |
        (cand_df[entity_type] != "[]")
        ]
    cand_names_series = cand_names_series[entity_type]

    comp_gold_cand_df = pd.concat([gold_names_series, cand_names_series], axis=1)
    comp_gold_cand_df.columns = ["gold_names", "cand_names"]
    print(f"{comp_gold_cand_df.shape=}")

    # convert to be list based
    for col in comp_gold_cand_df.columns:
        try:
            comp_gold_cand_df[col] = comp_gold_cand_df[col].apply(eval)
        except TypeError:
            pass

    prf_names = {name: PRFScore() for name in all_names}
    for idx in range(comp_gold_cand_df.shape[0]):
        line_gold_names = comp_gold_cand_df.iloc[idx][0]
        line_cand_names = comp_gold_cand_df.iloc[idx][1]

        # Calc TruePositive + FalsePositive
        for name in line_cand_names:
            if name in line_gold_names:
                prf_names[name].tp += 1
            else:
                prf_names[name].fp += 1
        # Calc FalseNegative
        for name in set(line_gold_names) - set(line_cand_names):
            prf_names[name].fn += 1

    prf_dict = {
        name: [prf.tp, prf.fp, prf.fn, prf.recall, prf.precision, prf.fscore, (prf.tp / (prf.tp + prf.fn + 1e-100))] for
        name, prf in prf_names.items()}
    prd_df = pd.DataFrame(prf_dict).transpose()
    prd_df.columns = ["tp", "fp", "fn", "recall", "precision", "f1", "acc"]
    print(f"{prd_df.shape=}")

    # with pd.option_context('display.max_rows', 500, 'display.max_columns', 10):
    #     display(prd_df)
    prd_df.to_csv(output_path)

    # calc aggregate
    prf = PRFScore()
    prf.tp = prd_df.tp.sum()
    prf.fp = prd_df.fp.sum()
    prf.fn = prd_df.fn.sum()

    prf_tot_df = pd.DataFrame([prf.tp, prf.fp, prf.fn, prf.recall, prf.precision, prf.fscore,
                               (prf.tp / (prf.tp + prf.fn + 1e-100))]).transpose()
    prf_tot_df.columns = ["tp", "fp", "fn", "recall", "precision", "f1", "acc"]
    prf_tot_df.to_csv(output_path.replace(".csv", "_agg.csv"))


def main(gold_df_path: str, by_model_df_path: str, output_path: str):
    evaluate_each_name(gold_df_path, by_model_df_path, output_path)


if __name__ == "__main__":
    try:
        typer.run(main)
    except SystemExit:
        pass
