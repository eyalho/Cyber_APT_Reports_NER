import re
from pathlib import Path

import srsly

from config import GIT_1_TXT_DIR, GIT_1_JSONL_PATH


class StreamAPTCyberCriminalCampaginCollections(object):
    """Stream cleaned lines from StreamAPTCyberCriminalCampaginCollections."""

    def __init__(
            self, file_path):
        """
        file_path (unicode / Path): Path to archive or directory of archives.
        RETURNS (StreamAPTCyberCriminalCampaginCollections): The loader.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise IOError(f"Can't find file path: {self.file_path}")

    def __iter__(self):
        minux_idx = 0
        for idx, file_path in enumerate(self.iter_files()):
            print(idx - minux_idx, file_path)
            if not self.validate_file(file_path):
                minux_idx += 1
                continue
            with open(str(file_path), "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if self.is_valid(line):
                        text = self.clean_txt(line)
                        yield {"text": text, "meta": self.get_meta(file_path)}

    def validate_file(self, file_path):
        git_repo = file_path.parent.parent.parent.name
        try:
            assert git_repo == "APT_CyberCriminal_Campagin_Collections"
            year = file_path.parent.parent.name
            assert int(year) < 2100
            assert int(year) > 1900
        except Exception as e:
            print(f"No year found: skip {file_path}\n --> Error: {e}")
            return False
        return True

    def get_meta(self, file_path):
        file_name = file_path.name
        git_repo = file_path.parent.parent.parent.name
        year = file_path.parent.parent.name
        return {"filename": file_name, "git_repo": git_repo, "year": year}

    def iter_files(self):
        if not self.file_path.is_dir():
            return [self.file_path]
        yield from self.file_path.glob("**/*.txt")

    def clean_txt(self, text):
        text = re.sub(r"\s+", " ", text)  # replace multiple unicode white spaces with a single space
        return text.strip()

    def is_valid(self, line):
        return True


if __name__ == "__main__":
    GIT_1_JSONL_PATH.parent.mkdir(exist_ok=True, parents=True)
    stream = StreamAPTCyberCriminalCampaginCollections(GIT_1_TXT_DIR)
    srsly.write_jsonl(GIT_1_JSONL_PATH, stream)
    print(f"created {GIT_1_JSONL_PATH} (out of {GIT_1_TXT_DIR} dir)")
