"""
sort.py

"""
import numpy as np
import pandas as pd
import os 
import sys 
import argparse
import random



def parse_command_line(args):
	'''

	'''
	
	print('parsing command line')
	print('='*30)

	parser = argparse.ArgumentParser(description='Sort student abstracts to faculty judges')
	parser.add_argument('--students', 
						action="store", 
						type=str, 
						default="data/students.xlsx"
						)
	parser.add_argument('--judges', 
						action="store", 
						type=str, 
						default="judges2.xlsx"
						)
	parser.add_argument('--judges_tab',
						action="store",
						type=str,
						default="Sheet3"
						)
	parser.add_argument('--judges_header', 
						action="store",
						type=int,
						default=3
						)
	parser.add_argument('--outdir', 
						action="store", 
						type=str, 
						default='sorted'
						)

	args = vars(parser.parse_args())

	return args



def read_judge_assignments(judges_file, judges_tab, judges_header, categories): 

	print('reading judge assignments from file %s'%judges_file)
	print('='*30)

	judges = pd.read_excel('data/judges2.xlsx', sheet_name="Sheet3", header=3)

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

	output_cols = ['Email Address', 'First Name', 'Last Name',]

	judges_per_cat = {}
	for cat in categories: 
		judges_per_cat[cat] = judges.loc[(judges["Would you like to judge student abstracts?"] == "Yes") & (judges["Assignment"] == cat)][output_cols].copy()
		print(judges_per_cat[cat].to_string())

	return judges_per_cat


def write_abstract_assignments(abstract_assignments, judges_per_cat, outdir): 

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

		with open(os.path.join(outdir, "abstract_assignments_%s"%cat.replace(" ", "_")), "w") as f: 

			# write the header line
			f.writelines(','.join(list(category_judges.columns)) + "\n")

			for idx, (email, first, last) in category_judges.iterrows(): 
				name_key = "%s %s"%(first.strip(), last.strip())
				judge_abstract_id_list = judge_dict[name_key]
				f.writelines(','.join([email, first, last] + list(map(str, judge_abstract_id_list))) + "\n")

	return


def sort_abstracts(id_df, category_judges, JUDGES_PER_ABSTRACT=4, JUDGE_LIM=9): 

	print('sorting abstracts to judges')
	print('-- judges per abstract: %d, max abstracts per judge: %d'%(JUDGES_PER_ABSTRACT, JUDGE_LIM))
	print('='*30)

	id_df = id_df.sample(frac=1).reset_index(drop=True)
	print(id_df.head())
	judge_dict = {"%s %s"%(first.strip(), last.strip()):[] for first, last in zip(category_judges['First Name'], category_judges['Last Name'])}

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
			print('oh no! only able to assign abstract id %d to %d / %d judges'%(abs_id, 
																				sum(status), 
																				JUDGES_PER_ABSTRACT))

	print(judge_dict)

	return judge_dict


def process_abstract_submissions(students_file): 

	print('processing abstract submissions')
	print('='*30)

	students = pd.read_excel('data/students.xlsx')
	rng = np.random.default_rng()
	ids = rng.choice(np.arange(100, 999), size=len(students), replace=False)
	students['ids'] = ids

	students['Scholarly Concentration'] = students['Scholarly Concentration'].apply(lambda x: x.replace("Humanism, Ethics, Education, and the Art of Medicine", "Ethics and the Art of Medicine"))

	print(ids)
	print(students.head())

	return students[['ids', 'Scholarly Concentration', 'Authors']], students[['ids', 'Scholarly Concentration']], students


def main():

	args = parse_command_line(sys.argv)

	categories = [
		"Basic Science", 
		"Clinical Science", 
		"Public Health", 
		"Ethics and the Art of Medicine",
		"History of Medicine",
	]

	np.random.seed(2021)
	random.seed(2021)

	id_df, id_df_anon, student_df = process_abstract_submissions(args['students'])

	judges_per_cat = read_judge_assignments(args['judges'], args['judges_tab'], args['judges_header'], categories)

	abstract_assignments = {}
	for cat in categories: 
		abstract_assignments[cat] = sort_abstracts(
										id_df.loc[id_df['Scholarly Concentration'] == cat], 
										judges_per_cat[cat]
									)

	write_abstract_assignments(abstract_assignments, judges_per_cat, args['outdir'])

	return


if __name__ == "__main__": 
	main()