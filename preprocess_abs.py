"""preprocess_abs.py

Given a file specified at pdf_path, which contains the abstracts merged from csv -> word doc -> pdf,
where each abstract has been formatted and is 1 per page, we partition them into individual pdfs
where each pdf is named [abstract_id].pdf, and contains only the single page of the big pdf
corresponding to that abstract.

This was the easiest way that I found to write all of the abstracts to individual pdfs.

Once the abstracts are as individual pdfs, we read the excel file containing the assignment of
abstracts to judges and combine all of each judge's abstracts into a single file,
with filename based on the judge name for easy attachment :).

"""
import os
from pprint import pprint
from PyPDF2 import PdfFileReader, PdfFileWriter
import pandas as pd
import argparse


def parse_command_line() -> dict:

    parser = argparse.ArgumentParser(
        description='prepare abstracts for mail merging to judges')

    parser.add_argument('--abstract_pdf', type=str, action='store', required=True,
                        help='pdf of all of the anonymized abstracts, formatted as one per page, in same order as abs id list')
    parser.add_argument('--submissions', type=str, action='store', required=True,
                        help='excel file the abstracts and all student information. Used to get the list of abstract ids')
    parser.add_argument('--judging', type=str, action='store', required=True,
                        help='excel file containing the ids of abstracts assigned to each judge')
    parser.add_argument('--bundle_abstracts', action='store_true',
                        help='if provided, bundle the abstracts for each judge into a single file for easier mailmerge')
    parser.add_argument('--outdir', type=str, action='store',
                        help='directory where each of the abstract bundles should be generated to')

    args = vars(parser.parse_args())
    print('--- received the following commandline arguments')
    pprint(args)
    return args


def main():

    args = parse_command_line()
    # pdf_path = "/Users/alex/Desktop/HOPKINS/MSRS/mailmerge_abstract_judging_merged.pdf"
    pdf_reader = PdfFileReader(args['abstract_pdf'])

    abstract_df = pd.read_excel(
        args['submissions'], sheet_name='remove repeats')
    ids = list(abstract_df['ids'])

    # create the file for the outputs if it does not exist
    if not os.path.exists(args['outdir']):
        print('creating output directory at %s' % args['outdir'])
        os.makedirs(args['outdir'])

    # create the file for the intermediates
    if not os.path.exists(os.path.join(args['outdir'], 'intermediates')):
        os.makedirs(os.path.join(args['outdir'], 'intermediates'))

    # separate the big pdf into individual pages
    for page_idx, page in enumerate(pdf_reader.pages):
        # this was to account for Natalie Marrero's long ass 2-page abstract from 2021.
        # comment it out under assumption that each abstract is 1 page
        # abs_id = ids[page_idx] if page_idx == 0 else ids[page_idx-1]

        abs_id = ids[page_idx]
        outfile = os.path.join(
            args['outdir'], 'intermediates', "%d.pdf" % abs_id)

        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(page)

        with open(outfile, "wb") as f:
            pdf_writer.write(f)

    # if we do not want to bundle the abstracts, exit here
    if not args['bundle_abstracts']:
        print('completing without bundling abstracts')
        exit()

    if '.xls' in args['judging']:
        assignments_df = pd.read_excel(args['judging'])
    else:
        assignments_df = pd.read_csv(args['judging'], )

    # cols = ["Email Address", "First Name", "Last Name", "Abs1", "Abs2",
    #         "Abs3", "Abs4", "Abs5", "Abs6", "Abs7", "Abs8", "Abs9", "Abs10", "Abs"]
    # print(assignments_df.head())
    # for idx, (cat, *merge_info) in assignments_df.iterrows():
    with open(args['judging'], 'r') as f:
        # skip the first line bc its a header lol
        _ = f.readline()
        line = f.readline()

        while line:
            cat, *merge_info = line.strip().split(',')

            judge_path = os.path.join(args['outdir'], "MSRS_abstracts_Dr_%s_%s.pdf" % (
                merge_info[1], merge_info[2]))

            # os.makedirs(judge_directory, exist_ok=True)

            abs_ids = merge_info[3:]

            print(merge_info)
            pdf_writer = PdfFileWriter()

            # conmbine the individual pdfs together
            for abs_id in abs_ids:
                if pd.isnull(abs_id):
                    continue

                pdf_reader = PdfFileReader(os.path.join(
                    args['outdir'], 'intermediates', str(int(abs_id)) + ".pdf"))
                for page in pdf_reader.pages:
                    pdf_writer.addPage(page)

                # individual_pdf_path = os.path.join(
                #     args['outdir'], 'intermediates', str(int(abs_id)) + ".pdf")

                # shutil.copy(individual_pdf_path, os.path.join(
                #     judge_directory, str(int(abs_id)) + ".pdf"))

            with open(judge_path, "wb") as out_fp:
                pdf_writer.write(out_fp)

            line = f.readline()

    return


if __name__ == "__main__":
    main()
