## To do list
 *figure out what the deal w/ grappelli is, since 2.6.5 is compatible with django 1.7, but not necessarily 1.8
 * problem set urls should use problem-set.title slug instead of id
 * problem urls should use problem.title slug instead of id
 * javascript to handle the form submission for a student problem set
 * tango make directories and zip files upon problem set upload (7.13.15)
 * tango urls for polling and adding jobs  (7.13.15)
 * general documentation re: how we're using tango and the database schema

 * passing the json object with attempt numbers and lateness to the file
 * run-python based on the grader file (maybe require that it's always grade.py)
 * max-of() function for student problem sets to set the attempt to the max of the student uploaded files
 * refuse to submit if required files are not added (attempt_problem_set.html)
 * results object for a student problem solution (json file gets dumped into a file in the folio(??))

* remove remnants of grade app
* make sure that all queries ONLY return results _for this user_ !!! (pretty sure this works, 7.14.15)
* put the new session.py and sanity in a lib ->  admins should not have to upload sanity, session, makefile, or run-python
* results if a problem has been submitted (7.14.15)


###Cool stuff
* problem coloring based on score?
* js confirmation alert before submission
* data dump as csv (https://docs.djangoproject.com/en/1.8/howto/outputting-csv/)
* alerts if problem sets have not been finished or attempted & due date is coming up
* ability for a student to flag a problem if they don't know what's wrong?

* index page 
  * upcoming problem sets, next 3 due?
  * recently submitted questions
