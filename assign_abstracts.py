"""assign_abstracts.py

Script for reading submitted assignments and the category of each judge to assign
each judge a set of abstracts to judge.

There will be two modes for abstract assignment:

- specify number of judges per category
- assign each judge as many abstracts as possible, up to some limit

"""
import argparse
import logging
import os
import random
from pprint import pprint
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)


def parse_command_line():
    log.debug('parsing command line')
    log.debug('='*30)

    parser = argparse.ArgumentParser(
        description='Sort student abstracts to faculty judges',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--students', action="store", type=str, default="data/students.xlsx",
                        help="file containing abstract submissions"
                        )
    parser.add_argument('--students_tab', action="store", type=str,
                        help="file containing abstract submissions"
                        )
    parser.add_argument('--judges', action="store", type=str, default="judges2.xlsx",
                        help="excel file containing judges and category assignments"
                        )
    parser.add_argument('--judges_tab', action="store", type=str, default="AssignedToCategories",
                        help="the tab within the sheet to be read"
                        )
    parser.add_argument('--judges_header', action="store", type=int, default=3,
                        help="the row to use as header row"
                        )
    parser.add_argument('--judges_per_abstract_basic', action="store", type=int, default=7,
                        help='number of judges per abstract for basic science'
                        )
    parser.add_argument('--judges_per_abstract_clinical', action="store", type=int, default=5,
                        help='number of judges per abstract for clinical science'
                        )
    parser.add_argument('--judges_per_abstract_public', action="store", type=int, default=4,
                        help='number of judges per abstract for public health'
                        )
    parser.add_argument('--judges_per_abstract_heart', action="store", type=int, default=4,
                        help='number of judges per abstract for HEART'
                        )
    parser.add_argument('--judges_per_abstract_hom', action="store", type=int, default=4,
                        help='number of judges per abstract for history of medicine'
                        )
    parser.add_argument('--ignore_poster_only', action="store_true",
                        help='do not assign abstracts if they are submitted as poster only'
                        )
    parser.add_argument('--outdir', action="store", type=str, default='sorted', required=True,
                        help='directory in which output files should be written'
                        )

    args = vars(parser.parse_args())
    log.debug(args)
    return args


def read_judge_cat_assign(judges_file: str, judges_tab: str, judges_header: int, categories: list) -> dict:

    log.info('reading judge assignments from file %s' % judges_file)
    log.info('='*30)

    judges = pd.read_excel(judges_file,
                           sheet_name=judges_tab, header=judges_header, engine='openpyxl')

    log.debug('here are the columns read from the judging spreadsheet')
    log.debug(list(judges.columns))

    # for cleanliness
    judges.drop(columns=[
        'Basic Science',
        'Clinical Science',
        'Public Health',
        'Humanism, Ethics, Education, and the Art of Medicine (HEART)',
        'History of Medicine',
        'Justification / Notes',
        'signed up for only 1 category',
        'What activities would you like to judge at MSRS 2022? ',
        "What topic would you like to judge? If you are interested in multiple options, you'll be placed in whatever topic needs more judges. ",
        'Timestamp',
        "Would you like to recommend any colleagues who may be interested in judging? If so, please let us know their name(s) and affiliation(s). "
    ], inplace=True, errors='ignore')

    output_cols = ['Email Address', 'First Name', 'Last Name', ]

    judges_per_cat = {}
    for cat in categories:
        judges_per_cat[cat] = judges.loc[(judges["Would you like to judge student abstracts?"] == "Yes") & (
            judges["Assignment"] == cat)][output_cols].copy()

        log.debug('judges for category %s' % cat)
        log.debug('='*30)
        log.debug(judges_per_cat[cat].to_string())

    return judges_per_cat


def write_abstract_assignments(abstract_assignments: dict, judges_per_cat: Dict[str, pd.DataFrame], outdir: str) -> None:
    """write_abstract_assignments

    Function for writing out all of the judging assignments. 

    abstract_assignments is a dictionary that maps [category] -> [a dictionary ]
    where each sub-dictionary is a mapping of [judge name] -> [list of abstract ids]

    judges_per_cat is a dictionary that maps [category] -> pandas dataframe of the 
    judging information, e.g. name, email, etc. 

    Args:
        abstract_assignments (dict): dictionary of abstract assignments 
        judges_per_cat (dict): dictionary of judge information dataframes  
        outdir (str): directory where judge abstract assignments should be written
    """
    log.info('writing the abstract assignments for each judge to file')
    log.info('='*30)

    # first, we will write all of the abstract assignments in one file for each of the categories
    for cat, judge_dict in abstract_assignments.items():
        category_judges = judges_per_cat[cat]

        # we expect category_judges to be a df with the following columns:
        # judge email
        # judge first name
        # judge last name

        with open(os.path.join(outdir, "abstract_assignments_%s.csv" % cat.replace(" ", "_")), "w") as f:

            # write the header line. We need to add Abs 1 ... Abs n to the column headers also.
            f.writelines(','.join(
                list(category_judges.columns) + ['Abs%d' % i for i in range(1, 16)]) + "\n")

            # iterate over the judges to write out each judge's assigned abstracts
            for idx, (email, first, last) in category_judges.iterrows():
                name_key = "%s %s" % (first.strip(), last.strip())
                judge_abstract_id_list = judge_dict[name_key]
                f.writelines(
                    ','.join([email, first, last] + list(map(str, judge_abstract_id_list))) + "\n")

    # write out an additional file that contains all of the judge abstract assignments,
    # instead of as individual files.
    with open(os.path.join(outdir, 'unified.csv'), 'w') as f:

        # write the header line. This time, it will be [category] [email] [first] [last] [abs 1] ... [abs n]
        f.writelines(','.join(
            ['category'] + list(category_judges.columns) + ['Abs%d' % i for i in range(1, 16)])
            + "\n")

        # again, iterate over all judges in all categories
        for cat, judge_dict in abstract_assignments.items():
            category_judges = judges_per_cat[cat]

            for idx, (email, first, last) in category_judges.iterrows():
                name_key = "%s %s" % (first.strip(), last.strip())
                judge_abstract_id_list = judge_dict[name_key]
                f.writelines(
                    ','.join([cat.replace(',', ';'), email, first, last] + list(map(str, judge_abstract_id_list))) + "\n")

    return


def assign_abstracts_to_judges(id_df, category_judges, JUDGES_PER_ABSTRACT=4, JUDGE_LIM=15):

    log.info('sorting abstracts to judges')
    log.info('-- judges per abstract: %d, max abstracts per judge: %d' %
             (JUDGES_PER_ABSTRACT, JUDGE_LIM))
    log.info('='*30)

    id_df = id_df.sample(frac=1).reset_index(drop=True)
    judge_dict = {"%s %s" % (first.strip(), last.strip()): [] for first, last in zip(
        category_judges['First Name'], category_judges['Last Name'])}

    opted_out = []
    judge_conflict_identified = []
    for idx, (abs_id, cat, authors, to_judge) in id_df.iterrows():

        if to_judge != 'Yes':
            log.debug('abstract %d opt out' % (abs_id))
            opted_out.append(abs_id)
            continue

        # reorder judges so that the assignment is not order dependent
        # shuffled_names = list(judge_dict.keys())
        # random.shuffle(shuffled_names)

        names = [(name, len(judge_dict[name]), np.random.randn(1))
                 for name in judge_dict.keys()]

        # sort the judge names in ascending order by the number of abstracts that they have been assigned
        # break ties at each level using rng so that there is still random shuffling
        names.sort(key=lambda x: (x[1], x[2]))

        # pull out just the name field again
        shuffled_names = [name[0] for name in names]

        # keep track of whether assignments are successful
        status = [False]*JUDGES_PER_ABSTRACT

        # assign each abstract to the pre-defined number of judges
        for iteration in range(JUDGES_PER_ABSTRACT):

            # loop over judges to see if any are free to judge the abstract
            for name in shuffled_names:
                cur_abs = judge_dict[name]

                # check the following conditions are met:
                # 	- judge has not been fully assigned
                # 	- judge is not an author on the abstract
                # 	- judge has not already been assigned the abstract

                if search_judge_conflicts(name, authors):
                    judge_conflict_identified.append((name, abs_id))
                    shuffled_names.remove(name)
                    log.warning('judge conflict: %s %s %s' %
                                (abs_id, name, authors))

                if (len(cur_abs) < JUDGE_LIM) and (name not in authors) and (abs_id not in cur_abs):
                    judge_dict[name].append(abs_id)
                    status[iteration] = True
                    break

        if not all(status):
            log.warning('oh no! only able to assign abstract id %d to %d / %d judges' %
                        (abs_id, sum(status), JUDGES_PER_ABSTRACT))

    log.info('opted out: %s ' % opted_out)
    log.info('judge conflicts: %s' % judge_conflict_identified)
    log.info('final judging assignments:')
    for k, v in judge_dict.items():
        log.info('%s ; \t\t %s' % (k, v))

    return judge_dict


def preprocess_abstract_submissions(students_file, students_tab) -> Union[pd.DataFrame, pd.DataFrame]:

    log.info('processing abstract submissions')
    log.info('='*30)

    students = pd.read_excel(students_file, sheet_name=students_tab)
    rng = np.random.default_rng(seed=2022)
    ids = rng.choice(np.arange(100, 300), size=len(students), replace=False)
    students['ids'] = ids

    students['Scholarly Concentration'] = students['Scholarly Concentration'].apply(lambda x: x.replace(
        "Humanism, Ethics, Education, and the Art of Medicine", "Humanism, Ethics, Education, and the Art of Medicine (HEART)"))

    log.debug(ids)

    return students[['ids', 'Scholarly Concentration', 'Authors', 'Are you interested in being considered for an oral or podium presentation?']], students


def quality_check(id_df: pd.DataFrame, abstract_assignments: dict) -> bool:

    assigned_ids = []

    for cat, judge_dict in abstract_assignments.items():
        for name_key, judge_abstract_id_list in judge_dict.items():
            assigned_ids += judge_abstract_id_list

    assigned_ids = list(set(assigned_ids))

    any = 0
    for idx, (abstract, cat, authors, to_judge) in id_df.iterrows():
        if (to_judge == 'Yes') and (abstract not in assigned_ids):
            log.warning('abstract %d in category %s was not assigned for judging. authors: %s' % (
                abstract, cat, authors))
            any += 1

    return (any == 0)


def search_judge_conflicts(judge_name: str, authors_list: str) -> bool:
    """search_judge_conflicts

    More advanced method of searching for judge name within the authors list. 

    Separates the judge name by white space. We know that judge_name is going to be 
    just first name and last name. 

    Separates the authors list by commas, then each chunk is separated by spaces. 

    This means if we have judge name as [Billy Osler] and author list as 
    [William Halsted, Billy H Osler], this will return True. 

    A simple string matching alone would not have returned True. 

    i.e. this matches first name + last name while ignoring optional middle initial.

    Args:
        judge_name (str): name of judge
        authors_list (str): str of all authors

    Returns:
        bool: [description]
    """
    judge_name_chunks = judge_name.lower().split(' ')
    parsed_chunks = [author.strip().lower().split(' ')
                     for author in authors_list.split(',')]
    for author_chunks in parsed_chunks:
        if all([chunk in author_chunks for chunk in judge_name_chunks]):
            log.debug('judge name found in authors list: %s %s' %
                      (judge_name, authors_list))
            return True

    return False


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

    id_df, student_df = preprocess_abstract_submissions(
        args['students'], args['students_tab'])
    log.info('processing %d abstract submissions' % (len(id_df)))

    judges_per_cat = read_judge_cat_assign(
        args['judges'], args['judges_tab'], args['judges_header'], categories)

    abstract_assignments = {}
    for cat in categories:
        log.info('category: %s' % cat)
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
