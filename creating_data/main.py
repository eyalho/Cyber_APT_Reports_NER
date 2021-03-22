import srsly

from creating_data.A0_download_sources import download_repo
from creating_data.A1_convert_pdf_to_txt import pdftotext_converter
from creating_data.A2_convert_txt_dir_to_jsonl import StreamAPTCyberCriminalCampaginCollections
from creating_data.A3_create_patterns_file import create_patterns_file
from creating_data.A4_annotate_jsonl_based_on_patterns import create_a_labeled_jsonl_dataset
from creating_data.config import GIT_URL_1, SOURCE_PDF_DIR, GIT_1_SOURCE_DIR, GIT_1_TXT_DIR, GIT_1_JSONL_PATH, \
    MITRE_LABELS_JSON_PATH, PATTERNS_FILE_PATH, GIT_1_ANNO_JSONL_PATH

if __name__ == "__main__":
    # A0
    download_repo(GIT_URL_1, SOURCE_PDF_DIR)  # Start Only with APT_CyberCriminal_Campagin_Collections
    # A1
    pdftotext_converter(GIT_1_SOURCE_DIR, GIT_1_TXT_DIR)
    # A2
    GIT_1_JSONL_PATH.parent.mkdir(exist_ok=True, parents=True)
    stream = StreamAPTCyberCriminalCampaginCollections(GIT_1_TXT_DIR)
    srsly.write_jsonl(GIT_1_JSONL_PATH, stream)
    print(f"created {GIT_1_JSONL_PATH} (out of {GIT_1_TXT_DIR} dir)")
    # A3
    create_patterns_file(MITRE_LABELS_JSON_PATH, PATTERNS_FILE_PATH)
    # A4
    GIT_1_ANNO_JSONL_PATH.parent.mkdir(exist_ok=True, parents=True)
    create_a_labeled_jsonl_dataset(PATTERNS_FILE_PATH.name, GIT_1_JSONL_PATH, GIT_1_ANNO_JSONL_PATH)

    # download_repo(GIT_URL_2, SOURCE_PDF_DIR)
    # download_repo(GIT_URL_3, SOURCE_PDF_DIR)
    # download_repo(GIT_URL_4, SOURCE_PDF_DIR)
