from pathlib import Path

PATTERNS_FILE_PATH = Path("patterns.jsonl")
MITRE_LABELS_JSON_PATH = Path("MITRE_labels.json")

GIT_URL_1 = "https://github.com/CyberMonitor/APT_CyberCriminal_Campagin_Collections"
GIT_URL_2 = "https://github.com/blackorbird/APT_REPORT"
GIT_URL_3 = "https://github.com/kbandla/APTnotes"
GIT_URL_4 = "https://github.com/fdiskyou/threat-INTel"

DATASET_DIR = Path("/home/eyal/dev/nlp_datasets")
SOURCE_PDF_DIR = DATASET_DIR / "sources_pdf"
DST_TXT_DIR = DATASET_DIR / "converted_to_txt"
DST_JSONL_DIR = DATASET_DIR / "converted_to_jsnol"
DST_ANNO_JSONL_DIR = DATASET_DIR / "converted_to_anno_jsnol"
DST_EXPERIMENT_ANNO_JSONL_DIR = DATASET_DIR / "experiment_anno_jsnol"

GIT_1_SOURCE_DIR = SOURCE_PDF_DIR / "APT_CyberCriminal_Campagin_Collections"
GIT_1_TXT_DIR = DST_TXT_DIR / "APT_CyberCriminal_Campagin_Collections"
GIT_1_JSONL_PATH = DST_JSONL_DIR / "APT_CyberCriminal_Campagin_Collections.jsonl"
GIT_1_ANNO_JSONL_PATH = DST_ANNO_JSONL_DIR / "APT_CyberCriminal_Campagin_Collections.jsonl"
GIT_1_DEV_ANNO_JSONL_PATH = DST_ANNO_JSONL_DIR / "DEV_APT_CyberCriminal_Campagin_Collections.jsonl"
