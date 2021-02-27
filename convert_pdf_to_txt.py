import pdftotext
from pathlib import Path


cur_dir = Path(".")
bad_counter = 0
for i, pdf_path in enumerate(cur_dir.rglob("*pdf")):
    dst_dir = Path("txt_files")
    dst_path = dst_dir / f"{pdf_path}.txt"
    dst_path.parent.mkdir(exist_ok=True,parents=True)
    # Load your PDF
    try:
        with open(pdf_path,"rb") as f:
            pdf = pdftotext.PDF(f)

        with open(dst_path, 'w') as f:
            f.write("\n\n".join(pdf))

        print("converted", i-bad_counter, dst_path)
    except Exception as e:
        #print(e, i, dst_path)
        bad_counter +=1
