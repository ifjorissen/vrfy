##Vrfy Project Structure
@ifjorissen
7.27.15

### Main Components
There are three main components in this project:
  * A webapp for students to attempt problems on a problem set and view the results. Administrators and TAs will have access to the admin interface wich had CRUD access to Problems, Problem Sets, and Results. This webapp is powered by Django (for more on this, see Django.md). 
  * An instance of a Tango server, which receives problems and student attempts and grades them in an isolated environment (for more on this, see Tango.md)
  * A packaged logging and utility library, included in each Tango job, to facilitate and standardize testing and logging within the grading instance.

### Directory Structure:

```

vrfy_project /
|
|__vrfy
   |
   |__course (manages problems, solutions, results, student & admin interface)
   |
   |__catalog (an app to mangage course metadata, including section, enrollment, TAs)
   |
   |__auth (manages cosign authentication and ldap queries)
   |
   |__vrfy (project urls)
      |
      |__ settings.py
|
|
|__Tango
   |
   |__config.py (general configuration file for Tango env)
|
|__GraderLibs
   |
   |__sanity.py (tiny utility library for inspection functions & classes)
   |
   |__session.py (logging object for the TA)


```

### Project (Major) Feature List:
  * Student Privileges
    * Course App
      * View Problem Set (for a specific section & course)
      * Submit Problems on a Problem Set
        * Upload Required Files
        * Upload additional optional files (not yet implemented)
        * Upload additional optional files with a specific name (not yet implemented)
      * View results for a single problem upon submission
      * View results for a problem set 
      * Reattempt a Problem on a Problem Set
    * Catalog App (None)
    * Auth App (None)

  * Admin Privileges
    * Course App
      * CRUD: Problems, Problem Sets
      * Ability to upload/paste a markdown / html file in lieu of full detailed info (not yet implemented)
      * Read, Delete: Student Solutions & Results (currently full CRUD)
      * Manually Resubmit a Student's Solution
      * Download a .csv of aggreggate results & submissions (not yet implemented)
    * Catalog App
      * CRUD: Courses, Sections, Enrollment List
    * Auth App (None)

