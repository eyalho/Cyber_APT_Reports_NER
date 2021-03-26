<!-- SPACY PROJECT: AUTO-GENERATED DOCS START (do not remove) -->

# 🪐 spaCy Project: Detecting cyber related names based on APT reports (Named Entity Recognition)

This project uses [`sense2vec`](https://github.com/explosion/sense2vec) and [Prodigy](https://prodi.gy) to bootstrap an NER model to detect fashion brands in [APTCyberCollection comments](https://files.pushshift.io/reddit/comments/). For more details, see [our blog post](https://explosion.ai/blog/sense2vec-reloaded#annotation).

## 📋 project.yml

The [`project.yml`](project.yml) defines the data assets required by the
project, as well as the available commands and workflows. For details, see the
[spaCy projects documentation](https://spacy.io/usage/projects).

### ⏯ Commands

The following commands are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run).
Commands are only re-run if their inputs have changed.

| Command | Description |
| --- | --- |
| `preprocess` | Convert the data to spaCy's binary format |
| `train` | Train a named entity recognition model |
| `evaluate` | Evaluate the model and export metrics |
| `package` | Package the trained model so it can be installed |
| `visualize-model` | Visualize the model's output interactively using Streamlit |
| `visualize-data` | Explore the annotated data in an interactive Streamlit app |
| `create-jsnol-anno-by-model` | Use the trained model and re-label the jsnol based on it prediction |
| `index-jsnol-into-df` | Index the jsnol files by simple dataframes and deserialized into zipped csv |
| `evaluate-in-depth` | evaluate-in-depth on each name |

### ⏭ Workflows

The following workflows are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `all` | `preprocess` &rarr; `train` &rarr; `evaluate` &rarr; `create-jsnol-anno-by-model` &rarr; `index-jsnol-into-df` &rarr; `evaluate-in-depth` |

### 🗂 Assets

The following assets are defined by the project. They can
be fetched by running [`spacy project assets`](https://spacy.io/api/cli#project-assets)
in the project directory.

| File | Source | Description |
| --- | --- | --- |
| [`assets/cyber_attrs_training.jsonl`](assets/cyber_attrs_training.jsonl) | Local |  |
| [`assets/cyber_attrs_eval.jsonl`](assets/cyber_attrs_eval.jsonl) | Local |  |

<!-- SPACY PROJECT: AUTO-GENERATED DOCS END (do not remove) -->