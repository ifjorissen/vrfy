##You Must Be A TA . . .
@ifjorissen
7.27.15

### If you're reading this, you're probably a TA for a CS course at Reed and wondering where you fit into all of this. 
As a TA, you have the following responsibilities / capabilities:
  * The ability to add, update, and delete problems and problem sets from the Admin interface of the webapp.
  * Part of your job requires writing the scripts that test submitted code.

### Writing a grading script
Don't think about it too hard. When a student submits a problem, the problem gets evaluated by running: `<your_grading_script>.py`. Which means that your script needs to be able to write output and access the submission and the solution. 

A picture of what's in the virtual machine that evaluates a submission:

```
tmp_eval_directory/
|
|__data.json (a data object that contains info about attempts and lateness)
|
|__session.py (a logging object, imported with `from session import Session`)
|
|__sanity.py (a tiny function/class library)
|
|__submission.py (the student submission, imported with `import <submission_name>` )
|
|__TA_solution.py (the "right" answer to the HW, imported with `import <TA_solution_name>`)
|
|__test_submission.py (the grading script that gets run)

```

* Note: it's really important that, when you make a problem on the admin interface, the "Required Filenames" and "Solution Files" fields correspond to the `<submission_name>` and `<TA_solution_name>` parameters that gets used in your grading script.

But you don't need to worry about all that.
Here's what HAS to be in every grading script: 

``` {python}

import <submission_name>  #student solution to the hw
import <TA_solution_name>  #ta's solution to the hw
from session import Session  #import the session object

#This is where you create an instance of the Session class, to log and score everything
sess = Session(<TA_solution_name> , <submission_name>)


... your testing code here ...

# Generate the final report
sess.finalize() 

```

While you don't **need** to make use of anything else in order to grade the hw, we've supplied five (5) methods on an instance of Session (e.g sess) we think might be helpful:
  * Write to internal log with: `sess.i_log(<message>)` Use case: You want to log a message (e.g test name / result) but don't want it to be visible to the student.
  * Write to the external log with: `sess.x_log(<message>)` Use case: You want to tell the student something about their code.
  * Perform a basic compartison with: `sess.compare()` Returns 'True' if all functions/classes/class funcs defined in <TA_solution_name> exist in <submission_name> and 'False' otherwise (and keeps the results in the log). Use case: You want check that every function, class (and functions within classes), which are defined in the <TA_solution_name> file exist (and are named correctly) in the student submission (<submission_name> file). *We strongly recommend performing this check before continuing with any other testing* 
  * Bulk compare inputs on a function with: `sess.test_hw_function('<function_name>', <array_of_public_inputs>, <array_of_private_inputs>)`. Use case: There are some tests or inputs a student know their hw will be tested on (these are the public inputs) and other (perhaps edge case scenarios), where we don't want to notify the student which test or input failed specifically, but that they should revisit their code.
  * Generate & Return the report as a JSON object with: `sess.finalize()` 

Check out some sample Test Scripts here (link...)




