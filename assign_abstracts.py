"""abstract_sort.py

"""
import argparse
import os
import random
from typing import Union
from pprint import pprint

import numpy as np
import pandas as pd


def parse_command_line():
    print('parsing command line')
    print('='*30)

    parser = argparse.ArgumentParser(
        description='Sort student abstracts to faculty judges',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--students',
                        action="store",
                        type=str,
                        default="data/students.xlsx",
                        help="file containing abstract submissions"
                        )
    parser.add_argument('--students_tab',
                        action="store",
                        type=str,
                        default="assignmen",
                        help="file containing abstract submissions"
                        )
    parser.add_argument('--judges',
                        action="store",
                        type=str,
                        default="judges2.xlsx",
                        help="excel file containing judges and category assignments"
                        )
    parser.add_argument('--judges_tab',
                        action="store",
                        type=str,
                        default="AssignedToCategories",
                        help="the tab within the sheet to be read"
                        )
    parser.add_argument('--judges_header',
                        action="store",
                        type=int,
                        default=3,
                        help="the row to use as header row"
                        )
    parser.add_argument('--judges_per_abstract_basic',
                        action="store",
                        type=int,
                        default=7,
                        help='number of judges per abstract for basic science'
                        )
    parser.add_argument('--judges_per_abstract_clinical',
                        action="store",
                        type=int,
                        default=5,
                        help='number of judges per abstract for clinical science'
                        )
    parser.add_argument('--judges_per_abstract_public',
                        action="store",
                        type=int,
                        default=4,
                        help='number of judges per abstract for public health'
                        )
    parser.add_argument('--judges_per_abstract_heart',
                        action="store",
                        type=int,
                        default=4,
                        help='number of judges per abstract for HEART'
                        )
    parser.add_argument('--judges_per_abstract_hom',
                        action="store",
                        type=int,
                        default=4,
                        help='number of judges per abstract for history of medicine'
                        )
    parser.add_argument('--outdir',
                        action="store",
                        type=str,
                        default='sorted',
                        required=True,
                        help='directory in which output files should be written'
                        )

    args = vars(parser.parse_args())
    pprint(args)
    return args


def read_judge_cat_assign(judges_file: str, judges_tab: str, judges_header: int, categories: list) -> dict:

    print('reading judge assignments from file %s' % judges_file)
    print('='*30)

    judges = pd.read_excel(judges_file,
                           sheet_name=judges_tab, header=judges_header, engine='openpyxl')

    print('here are the columns read from the judging spreadsheet')
    print(judges.columns)

    judges.drop(columns=[
        'Basic Science',
        'Clinical Science',
        'Public Health',
        'Ethics and the Art of Medicine',
        'History of Medicine',
        'Justification / Notes',
        'signed up for only 1 category',
        'What activities would you like to judge at MSRS 2021? ',
        "What topic would you like to judge? If you are interested in multiple options, you'll be placed in whatever topic needs more judges. ",
        'Timestamp',
        "Would you like to recommend any colleagues who may be interested in judging? If so, please let us know their name(s) and affiliation(s). "
    ], inplace=True)

    print(judges.head())

    output_cols = ['Email Address', 'First Name', 'Last Name', ]

    judges_per_cat = {}
    for cat in categories:
        judges_per_cat[cat] = judges.loc[(judges["Would you like to judge student abstracts?"] == "Yes") & (
            judges["Assignment"] == cat)][output_cols].copy()
        print(judges_per_cat[cat].to_string())

    return judges_per_cat


def write_abstract_assignments(abstract_assignments: dict, judges_per_cat: dict, outdir: str) -> None:

    print('writing the abstract assignments for each judge to file')
    print('='*30)

    for cat, judge_dict in abstract_assignments.items():
        category_judges = judges_per_cat[cat]

        # judge email
        # judge first name
        # judge last name
        # abstract id 1
        # ...
        # abstract id 10

        with open(os.path.join(outdir, "abstract_assignments_%s.csv" % cat.replace(" ", "_")), "w") as f:

            # write the header line
            f.writelines(','.join(list(category_judges.columns)) + "\n")

            for idx, (email, first, last) in category_judges.iterrows():
                name_key = "%s %s" % (first.strip(), last.strip())
                judge_abstract_id_list = judge_dict[name_key]
                f.writelines(
                    ','.join([email, first, last] + list(map(str, judge_abstract_id_list))) + "\n")

    return


def assign_abstracts_to_judges(id_df, category_judges, JUDGES_PER_ABSTRACT=4, JUDGE_LIM=10):

    print('sorting abstracts to judges')
    print('-- judges per abstract: %d, max abstracts per judge: %d' %
          (JUDGES_PER_ABSTRACT, JUDGE_LIM))
    print('='*30)

    id_df = id_df.sample(frac=1).reset_index(drop=True)
    print(id_df.head())
    judge_dict = {"%s %s" % (first.strip(), last.strip()): [] for first, last in zip(
        category_judges['First Name'], category_judges['Last Name'])}

    for idx, (abs_id, cat, authors) in id_df.iterrows():

        # reorder judges so that the assignment is not order dependent
        shuffled_names = list(judge_dict.keys())
        random.shuffle(shuffled_names)

        # keep track of whether assignments are successful
        status = [False]*JUDGES_PER_ABSTRACT

        # assign each abstract to a pre-defined number of judges
        for iteration in range(JUDGES_PER_ABSTRACT):

            # iterate over judges to see if any are free to judge the abstract
            for name in shuffled_names:
                cur_abs = judge_dict[name]

                # check the following conditions are met:
                # 	- judge has not been fully assigned
                # 	- judge is not an author on the abstract
                # 	- judge has not already been assigned the abstract

                if (len(cur_abs) < JUDGE_LIM) and (name not in authors) and (abs_id not in cur_abs):
                    judge_dict[name].append(abs_id)
                    status[iteration] = True
                    break

        if not all(status):
            print('oh no! only able to assign abstract id %d to %d / %d judges' % (abs_id,
                                                                                   sum(status),
                                                                                   JUDGES_PER_ABSTRACT))

    print(judge_dict)

    return judge_dict


def preprocess_abstract_submissions(students_file) -> Union[pd.DataFrame, pd.DataFrame]:

    print('processing abstract submissions')
    print('='*30)

    students = pd.read_excel(students_file)
    rng = np.random.default_rng(seed=2022)
    ids = rng.choice(np.arange(100, 999), size=len(students), replace=False)
    students['ids'] = ids

    students['Scholarly Concentration'] = students['Scholarly Concentration'].apply(lambda x: x.replace(
        "Humanism, Ethics, Education, and the Art of Medicine", "Humanism, Ethics, Education, and the Art of Medicine (HEART)"))

    print(ids)
    print(students.head())

    return students[['ids', 'Scholarly Concentration', 'Authors']], students


def quality_check(id_df: pd.DataFrame, abstract_assignments: dict) -> bool:

    assigned_ids = []

    for cat, judge_dict in abstract_assignments.items():
        for name_key, judge_abstract_id_list in judge_dict.items():
            assigned_ids += judge_abstract_id_list

    assigned_ids = list(set(assigned_ids))

    for abstract in id_df['ids']:
        if abstract not in assigned_ids:
            print('abstract %d in category %s was not assigned for judging' % (
                abstract, id_df[id_df['ids'] == abstract]['Scholarly Concentration']))
            return False

    return True


def main():

    args = parse_command_line()

    categories = [
        "Basic Science",
        "Clinical Science",
        "Public Health",
        "Humanism, Ethics, Education, and the Art of Medicine (HEART)",
        "History of Medicine",
    ]

    category_hyperparam = {
        "Basic Science": args['judges_per_abstract_basic'],
        "Clinical Science": args['judges_per_abstract_clinical'],
        "Public Health": args['judges_per_abstract_public'],
        "Humanism, Ethics, Education, and the Art of Medicine (HEART)": args['judges_per_abstract_heart'],
        "History of Medicine": args['judges_per_abstract_hom'],
    }

    np.random.seed(2022)
    random.seed(2022)

    id_df, student_df = preprocess_abstract_submissions(args['students'])

    judges_per_cat = read_judge_cat_assign(
        args['judges'], args['judges_tab'], args['judges_header'], categories)

    abstract_assignments = {}
    for cat in categories:
        abstract_assignments[cat] = assign_abstracts_to_judges(
            id_df.loc[id_df['Scholarly Concentration'] == cat],
            judges_per_cat[cat],
            JUDGES_PER_ABSTRACT=category_hyperparam[cat]
        )

    if quality_check(id_df, abstract_assignments):

        write_abstract_assignments(
            abstract_assignments, judges_per_cat, args['outdir'])

        student_df.to_csv("assigned_ids_students.csv")

    return


if __name__ == "__main__":
    main()
