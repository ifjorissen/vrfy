## To do list
 * figure out what the deal w/ grappelli is, since 2.6.5 is compatible with django 1.7, but not necessarily 1.8 (7.15.15- seems fine?)
 * problem set urls should use problem-set.title slug instead of id
 * problem urls should use problem.title slug instead of id
 * javascript to handle the form submission for a student problem set (?, nah?)
 * tango make directories and zip files upon problem set upload (7.13.15)
 * tango urls for polling and adding jobs  (7.13.15)
 * general documentation re: how we're using tango and the database schema

 * passing the json object with attempt numbers and lateness to the file
 * run-python based on the grader file (maybe require that it's always grade.py) (7.15.15)
 * refuse to submit if required files are not added (attempt_problem_set.html)
 * results object for a student problem solution (json file gets dumped into a file in the folio(??)) (7.15.15)
 * student should be able to upload additional optional files

* remove remnants of grade app (7.19.15)
* make sure that all queries ONLY return results _for this user_ !!! (pretty sure this works, 7.14.15)
* put the new session.py and sanity in a lib ->  admins should not have to upload sanity, session, makefile, or run-python (7.15.15)
* results if a problem has been submitted (7.14.15) 

* search and filtering in django admin (list_filter)
* only add a courselab & grading file _if_ the problem is meant to be autograded
* django-json (or django-pgjson) to hold the raw json object for results
* make most fields on Student (& Result) admin fields read-only
* bug in the results where you've attempted the set but the results arent ready... what if the job isnt done


###Cool stuff
* problem coloring based on score?
* js confirmation alert before submission
* data dump as csv (https://docs.djangoproject.com/en/1.8/howto/outputting-csv/)
* alerts if problem sets have not been finished or attempted & due date is coming up

* index page 
  * upcoming problem sets, next 3 due?
  * recently submitted questions
