from pathlib import Path

import pdftotext

from config import GIT_1_SOURCE_DIR, GIT_1_TXT_DIR


def pdftotext_converter(source_pdf_dir, dst_txt_dir):
    source_pdf_dir = Path(source_pdf_dir)
    dst_txt_dir = Path(dst_txt_dir)
    print(f"pdf_dir : {source_pdf_dir}")
    print(f"dst_txt_dir : {dst_txt_dir}")
    bad_counter = 0
    for i, pdf_path in enumerate(source_pdf_dir.rglob("*pdf")):
        rel_pdf_path = pdf_path.relative_to(source_pdf_dir)
        dst_path = dst_txt_dir / f"{rel_pdf_path}.txt"
        dst_path.parent.mkdir(exist_ok=True, parents=True)
        # Load your PDF
        try:
            with open(pdf_path, "rb") as f:
                pdf = pdftotext.PDF(f)

            with open(dst_path, 'w') as f:
                f.write("\n\n".join(pdf))

            print("converted", i - bad_counter, dst_path)
        except Exception as e:
            print(e, i, dst_path)
            bad_counter += 1


if __name__ == "__main__":
    pdftotext_converter(GIT_1_SOURCE_DIR, GIT_1_TXT_DIR)
