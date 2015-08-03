## Course App
@ifjorissen
7.27.15

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
      * Enrolled: a (many-to-many) list of student enrolled in the course
      * Professor: who's teaching the course
  * Views (None)

### A relatively in-depth explanation of the course app
  Purpose: catalog & organize problems into sets, problem results, solutions, attempts, etc.
  * Overview of how everything is connected:
    * A Problem (Problem) is an "abstract" object associated with a course, it has no due date or section assignment. 
    * A Problem Set (ProblemSet) is essentially a bag of problems, and *it* is the object associated with a section and a due date. 
    * Every student triggers the creation of a Student Problem Set (StudentProblemSet) and a solution (StudentProblemSolution) upon viewing the problem set. Each student problem set is associated with the published problem set, and each solution is associated with a problem (and the solution set it's a member of). 
    * When a student submits a problem, the solution is marked as submitted (and sent to Tango), and the attempt number increased. A results object (ProblemResult) is created for that submission and it is populated with the results from Tango. A result is a member of a result set (ProblemResultSet), which is modified whenever a student (re-)submits a problem. Multiple submissions overrwrite the solution object (the files from previous attempts are saved), but result objects are created for each submission of a solution. (i.e a Solution might have 6 attempts on a problem, and there would be 6 ProblemResult objects for each attempt, but only one solution object). 
  * Models