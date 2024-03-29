## MSRS Repository

Here we'll try to track some of the scripts that we use to automate MSRS. Student data, rankings, and other information will not be pushed to the repository.

## Workflow

0. Make sure that the environment is set up properly. There are some dependencies for the scripts to work: 

```
rich
pandas
PyPDF2
```

https://anaconda.org/conda-forge/rich/

https://pandas.pydata.org/docs/getting_started/install.html

https://pypi.org/project/PyPDF2/

1. Given the excel or csv that contains the judging information, and the list of student abstract submissions, use `abstract_sort.py` to automatically assign abstracts -> judges. 

2. Use a word doc mail merge -> generate a pdf where each page contains the abstracts, where the order of the pages is the same as the order of the index list. Note that this mail merge should be ANONYMIZED in an attempt to mitigate judge bias -- it should only include the abstract ID, and not the student name or the list of authors. 

3. Once a PDF has been generated, we can use the `preprocess_abs.py` script in order to generate an individualized PDF to be attached via email to each judge. The overall goal here is to make it easier for judges to grade things. If you really want to skip the step of selecting a specific PDF for judge while emailing them, you can attach the same big document of anonymized abstracts to all judges, but I personally feel that this is not professional. 

4. Use mail merge to email judges, and attach the PDFs generated by `preprocess_abs.py` to each judge. 

5. Once judging scores have been entered, we're going to need to process those. This is typically done using a Gaussian Mixed Effects Model (implemented by Harshi Gupta, Matthew Tan. Original code can be found [here](https://github.com/muon2998/MSRS) but modifications and updates can be added to this repository. 


## Commandline Interface

Overall input structure / directory organization in this example:  
* folder `MSRS2021` 
  * subfolder `inputs`
    * file `student_abstracts.xlsx` which contains the student information (submitting student name, title, authors, abstract text, etc)
      * the tab within the .xlsx file that we want to parse is titled "PROCESSING_READY"
    * file `judge_categories.xlsx` which contains the judge information (i.e. each row has the judge and what category they got assigned to) 
      * the tab within the .xlsx file that we want to parse is titled "ASSIGNED_TO_CATEGORIES"
  * subfolder `abstract_assignments` -- where the outputs from `assign_abstracts.py` will be generated to. 
  * subfolder `attachments` -- where the attachments from `preprocess_abs.py` will be generated to.

### Example script call to generate the abstract assignments: 

```console 

python assign_abstracts.py --students MSRS2021/inputs/student_abstracts.xlsx --students_tab "PROCESSING_READY" --judges MSRS2021/inputs/judge_categories.xlsx --judges_tab ASSIGNED_TO_CATEGORIES --judges_header 4 --judges_per_abstract_basic 8 --judges_per_abstract_clinical 2 --judges_per_abstract_public 3 --judges_per_abstract_heart 5 --judges_per_abstract_hom 3 --outdir MSRS2021/abstract_assignments/

```

### Explanation of interface: 


For `assign_abstracts.py`: 

`--students`: use this to speicfy the path to the Excel sheet which contains the student abstract submissions. 

`--students_tab`: use this to specify the name of the tab within the Excel sheet that needs to be processed. i.e. if you remove duplicates, preprocess, etc the student submissions but not in the tab that the survey responses are populated into, then specify that here. In the above example, the students tab is named "PROCESSING_READY"

`--judges`: use this to speicfy the path to the Excel sheet which contains the judge information, and which judge has been assigned to which judging category. 

`--judges_tab`: similar to the `--students_tab` flag, use this to specify which tab of the Excel sheet contains the judges assigned ot their categories. 

`--judges_header`: use this to specify which row the list of judges starts from. (e.g. if there are category metrics for tracking judge responses, these should go above the header row and this argument enables them to be seamlessly ignored by `pandas` dataframe loading. 

```console
--judges_per_abstract_basic 8 --judges_per_abstract_clinical 2 --judges_per_abstract_public 3 --judges_per_abstract_heart 5 --judges_per_abstract_hom 3
``` 
use this to specify how many judges should see each abstract. 

There is also a hard-coded limit for the maximum number of abstracts that each judge should see -- default 15! If possible... this should be reduced for their sanity :) 

`--outdir` -- where the abstract assignments should be written. There will be 6 `.csv` files in the folder that you specify -- one for each MSRS category, and one that combines them all (`unified.csv`). 


For `preprocess_abs.py`: 

Usage for this script is much easier to understand 

```console
preprocess_abs.py -h   

usage: preprocess_abs.py [-h] --abstract_pdf ABSTRACT_PDF --submissions SUBMISSIONS --judging JUDGING [--bundle_abstracts] [--outdir OUTDIR]

prepare abstracts for mail merging to judges

optional arguments:
  -h, --help            show this help message and exit
  --abstract_pdf ABSTRACT_PDF
                        pdf of all of the anonymized abstracts, formatted as one per page, in same order as abs id list
  --submissions SUBMISSIONS
                        excel file the abstracts and all student information. Used to get the list of abstract ids
  --judging JUDGING     excel file containing the ids of abstracts assigned to each judge
  --bundle_abstracts    if provided, bundle the abstracts for each judge into a single file for easier mailmerge
  --outdir OUTDIR       directory where each of the abstract bundles should be generated to
```
