## MSRS Repository

Here we'll try to track some of the scripts that we use to automate MSRS. Student data, rankings, and other information will not be pushed to the repository.

## Workflow

1. Given the excel or csv that contains the judging information, and the list of student abstract submissions, use `abstract_sort.py` to automatically assign abstracts -> judges. 

2. Use a word doc mail merge -> generate a pdf where each page contains the abstracts, where the order of the pages is the same as the order of the index list. 



## Commandline Interface


generating the abstract assignments: 

```python 

assign_abstracts.py --students MSRS2021/inputs/student_abstracts.xlsx --students_tab "remove repeats" --judges MSRS2021/inputs/judge_categories.xlsx --judges_tab AssignedToCategories --judges_header 4 --judges_per_abstract_basic 8 --judges_per_abstract_clinical 2 --judges_per_abstract_public 3 --judges_per_abstract_heart 5 --judges_per_abstract_hom 3 --outdir MSRS2021/abstract_assignments/

```


