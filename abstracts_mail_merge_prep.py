"""abstractsmail_merge_prep.py

Given the abstracts that were separated into individual pages from `abstract_partition.py`, this file 
runs the script to combine abstracts into single attachments for each judge, so that each document contains 
[abs1, abs2, ..., abs_n] for the n abstracts assigned to each judge. 

"""
import os
import pandas as pd
from PyPDF2 import PdfFileReader, PdfFileWriter


def main():
    assignments_df = pd.read_excel(
        "~/Downloads/MSRS 2021 Abstracts.xlsx", sheet_name="assignments")

    cols = ["Email Address", "First Name", "Last Name", "Abs1", "Abs2",
            "Abs3", "Abs4", "Abs5", "Abs6", "Abs7", "Abs8", "Abs9", "Abs10"]
    for idx, (merge_info) in assignments_df[cols].iterrows():
        abs_ids = merge_info[3:]

        pdf_writer = PdfFileWriter()

        for abs_id in abs_ids:
            if pd.isnull(abs_id):
                continue

            pdf_reader = PdfFileReader(os.path.join(
                os.getcwd(), str(int(abs_id)) + ".pdf"))
            for page in pdf_reader.pages:
                pdf_writer.addPage(page)

        out = os.path.join(os.getcwd(), "MSRS_abstracts_Dr_%s_%s.pdf" % (
            merge_info[1], merge_info[2]))
        with open(out, "wb") as f:
            pdf_writer.write(f)

    return


if __name__ == "__main__":
    main()
