"""
abstract_partition.py

"""
import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
import pandas as pd


def main(): 

	pdf_path = "/Users/alex/Desktop/HOPKINS/MSRS/mailmerge_abstract_judging_merged.pdf"
	pdf_reader = PdfFileReader(pdf_path)

	abstract_df = pd.read_excel('~/Downloads/MSRS 2021 Abstracts.xlsx')
	ids = list(abstract_df['ids'])

	for page_idx, page in enumerate(pdf_reader.pages): 

		abs_id = ids[page_idx] if page_idx == 0 else ids[page_idx-1]
		outfile = os.path.join("/Users/alex/Desktop/HOPKINS/MSRS", "%d.pdf"%abs_id)

		pdf_writer = PdfFileWriter()
		pdf_writer.addPage(page)


		with open(outfile, "wb") as f:
			pdf_writer.write(f)

	return


if __name__ == "__main__": 
	main()
