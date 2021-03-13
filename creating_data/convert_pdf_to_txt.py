from pathlib import Path

import pdftotext


def main(pdf_dir, dst_dir):
    pdf_dir = Path(pdf_dir)
    dst_dir = Path(dst_dir)
    bad_counter = 0
    for i, pdf_path in enumerate(pdf_dir.rglob("*pdf")):
        dst_path = dst_dir / f"{pdf_path}.txt"
        dst_path.parent.mkdir(exist_ok=True, parents=True)
        # Load your PDF
        try:
            with open(pdf_path, "rb") as f:
                pdf = pdftotext.PDF(f)

            with open(dst_path, 'w') as f:
                f.write("\n\n".join(pdf))

            print("converted", i - bad_counter, dst_path)
        except Exception as e:
            # print(e, i, dst_path)
            bad_counter += 1


if __name__ == "__main__":
    main("pdf_dir", "dst_dir")
