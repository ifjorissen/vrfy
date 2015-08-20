## Course App
@ifjorissen
8.20.15

### Overview: We're using Django 1.8 and Postgres for this project, which means that we get a free ORM (object relational mapper) thanks to Django. Each model is (roughly) a table in a database, with attributes (again, roughly) corresponding to a column in that table. If you're fuzzy on the meaning of Foreign Keys or Many-to-Many relationships, you should read up on those here (link...)


### A relatively in-depth explanation of the catalog app
  Purpose: A catalog is an (semi-)optional app / plugin to enhance the vrfy project and provide more organization to the data in a course
  * Models
    * Course
      * Title: Course Title (e.g Intro To Computer Science)
      * Num: Course number (e.g 121)
    * Section
      * Course: a (foreignkey) to the course this class is a section of
      * Section ID: section ID of the course (e.g FO2)
      * Start Date: day the course starts
      * End Date: day the course ends
      * Enrolled: a (many-to-many or m2m) list of student enrolled in the course
      * Professor: who's teaching the course
    * Reedie (Used to extend the Django User)
      * User: Django user this reedie is associated with
      * Other various attributes populated by the LDAP query
  * Views (None)

### A relatively in-depth explanation of the course app
  Purpose: catalog & organize problems into sets, problem results, solutions, attempts, etc.
  * Overview of how everything is connected:
    * A Problem (Problem) is an "abstract" object associated with a course, it has no due date or section assignment. 
    * A Problem Set (ProblemSet) is essentially a bag of problems, and *it* is the object associated with a section and a due date. 
    * Every student triggers the creation of a Student Problem Set (StudentProblemSet) and a solution (StudentProblemSolution) upon viewing the problem set. Each student problem set is associated with the published problem set, and each solution is associated with a problem (and the solution set it's a member of). 
    * When a student submits a problem, the solution is marked as submitted (and sent to Tango), and the attempt number increased by one. If the problem is autograded, Tango recieves the ProblemSolutionFiles associated with the Problem, each of the GraderLib files, and the StudentProblemFiles (after they have been mapped to the correct names per the RequiredFileName associated with the StudentProblemFile). Tango also recieves a Makefile that runs the Grader Script associated with the Problem and a data object (JSON) containing information about attempts and lateness. A results object (ProblemResult) is created for that submission and it is populated with the results from Tango. Multiple submissions overrwrite the solution object (the files from previous attempts are saved), but result objects are created for each submission of a solution. (i.e a Solution might have 6 attempts on a problem, and there would be 6 ProblemResult objects for each attempt, but only one solution object). The StudentSolution contains information about the lastest ProblemResult.  
  * Main Models
    * Problem
      * Title: Title for the problem
      * Description: a TL;DR of the problem _optional_
      * Statement: A detailed problem statement 
      * Many Attempts: a boolean value that determines whether or not multiple attempts on a problem are allowed. Defaults to True.
      * Autograde Problem: a boolean value that determines whether or not the problem should be sent to Tango for autograding. Defaults to True. 
      * Grade Script: the script that is used to grade a student submission. It will have access to the student's uploaded files, the grader libraries, and the problem solution files.  
      * CS Course: the course that the problem is associated with. (E.g Intro to Computer Science)
    * ProblemSet
      * Title: Title for the problem set
      * CS Section: the section(s) this problem set is assigned to (E.g Intro to Computer Science FO1)
      * Description: problem set description _optional_
      * Problems: a list (m2m) of the problems on this problem set. (Problems can be assigned to more than one problem set)
      * Pub Date: date the problem set is assigned (cannot be before the class begins)
      * Due Date: date the problem set is due (cannot be after the class ends)
    * StudentProblemSolution
      * Problem: the problem this submission is a solution for
      * Student Problem Set: the set of student solutions that this solution is associated with
      * Attempt Num: the number of attempts made on this problem
      * Submitted: the timestamp of the most recent attempt on this problem
      * Job ID: the job ID assigned to the most recent submission (a ProblemResult object) by Tango
    * StudentProblemSet
      * Problem Set: the corresponding problem set
      * User: the Reedie who is working on (/ has submitted) this set of solutions
      * Submitted: the most recent update to the solution set
    * Problem Result
      * Job ID: the job ID assigned to this submission by Tango 
      * Problem: the problem this result is for
      * SP Sol: the StudentProblemSolution associated with this problem.
      * Timestamp: when this result was received from Tango
      * Raw Log: the entire output.txt file generated by tango
      * JSON Log: the json object generated by the session.py library in the Test Runner repo. (link ...)
  * Support Models
    * GraderLib: a file that will get imported into every Tango courselab and will be available to the grading script for that assignment. Uploaded via the admin interface. Scope is currently site-wide (all problems in all courses & sections).
    * ProblemSolutionFile: one of the files that contains the solution to the problem it's associated to. Uploaded on a per-problem-basis via the admin interface.
    * RequiredProblemFilename: The name that a StudentProblemFile will get mapped to when it is sent to Tango for evaluation. Set on a per-problem-basis in the admin interface.
    * StudentProblemFile: one of the files a student uploads when attempting a problem. If it has a required problem filename, it will be mapped to that name when sent to Tango for evaluation. Uploaded via the student-view interface.