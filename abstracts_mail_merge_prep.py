"""
abstractsmail_merge_prep.py
"""
import os
import sys
import pandas as pd
from PyPDF2 import PdfFileReader, PdfFileWriter


def main(): 
	assignments_df = pd.read_excel("~/Downloads/MSRS 2021 Abstracts.xlsx", sheet_name="assignments")

	# for col in ["Abs1", "Abs2", "Abs3", "Abs4", "Abs5", "Abs6", "Abs7", "Abs8", "Abs9", "Abs10"]: 
	# 	assignments_df[col] = assignments_df[col].map(lambda x: str(int(x)) + ".pdf", na_action="ignore")

	# assignments_df.to_excel("output_merge_sheet.xlsx")

	cols = ["Email Address", "First Name", "Last Name", "Abs1", "Abs2", "Abs3", "Abs4", "Abs5", "Abs6", "Abs7", "Abs8", "Abs9", "Abs10"]
	for idx, (merge_info) in assignments_df[cols].iterrows(): 
		abs_ids = merge_info[3:]

		pdf_writer = PdfFileWriter()

		for abs_id in abs_ids: 
			if pd.isnull(abs_id):
				continue

			pdf_reader = PdfFileReader(os.path.join(os.getcwd(), str(int(abs_id)) + ".pdf"))
			for page in pdf_reader.pages: 
				pdf_writer.addPage(page)

		out = os.path.join(os.getcwd(), "MSRS_abstracts_Dr_%s_%s.pdf"%(merge_info[1], merge_info[2]))
		with open(out, "wb") as f: 
			pdf_writer.write(f)

	return


if __name__ == "__main__":
	main()