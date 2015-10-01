# TODO:
# Add tests for:
# adding a new file to existing problem set
# changing the name of a problem set

import random
import datetime
import requests
from django.test import TestCase, LiveServerTestCase, TransactionTestCase
from django.utils import timezone
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User
from django.core.files import File as Dfile
import datetime

import sys
sys.path.append("../")
import vrfy.settings

from . import views
from . import models
import catalog.models
from django.contrib.auth.models import User
#from .models import ProblemSet, Problem, ProblemSolutionFile

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"


class ProblemSetTests(TransactionTestCase):
    """
    A Model for TestCases that use Problem sets
    It makes a new problem set for testing and then deletes it when the tests are over
    """
    @classmethod
    def setUpClass(cls):
        cls.course = catalog.models.Course(
            title="course_" + str(random.randint(1, 10000)), num=random.randint(1, 10000))
        cls.course.save()
        duser, created = User.objects.get_or_create(username='isjoriss')
        cls.user, created = catalog.models.Reedie.objects.get_or_create(
            user=duser)
        # cls.user.save()
        #cls.user = generic.models.CSUser.get_ldap_user(username = 'isjoriss')

        cls.section = catalog.models.Section(
            course=cls.course,
            section_id=str(
                random.randint(
                    1,
                    10000)),
            start_date=timezone.now(),
            end_date=timezone.now() +
            datetime.timedelta(
                days=60))
        cls.section.save()
        cls.section.enrolled.add(cls.user)

        cls.ps = models.ProblemSet(
            title='test_ps_' +
            str(
                random.randint(
                    1,
                    10000)),
            pub_date=timezone.now(),
            due_date=timezone.now() +
            datetime.timedelta(
                days=30))
        cls.ps.save()
        cls.ps.cs_section.add(cls.section)
        cls.pk = cls.ps.pk

        cls.prob = models.Problem( title='test_prob_' +
     str(random.randint(1, 10000)), cs_course=cls.course)
        cls.prob.save()
        cls.ps.problems.add(cls.prob)
        super(ProblemSetTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        # if the ps still exists, delete it
        if cls.ps.id is not None:
            try:
                cls.ps.delete()
            # since the ps was not made in the admin, the courselab was never
            # created, and as such cannot be deleted
            except FileNotFoundError:
                pass
        # we always want to delete the problem, but it still doesnt have a
        # courselab
        try:
            cls.prob.delete()
        except FileNotFoundError:
            pass

        # cls.user.delete()
        cls.section.delete()
        cls.course.delete()
        cls.user.enrolled.clear()
        super(ProblemSetTests, cls).tearDownClass()


class NonExistantProblemsetTests(ProblemSetTests):
    """
    Tests that the course pages give a 404 when you try to access a page that doesnt exist
    """
    @classmethod
    def setUpClass(cls):
        super(NonExistantProblemsetTests, cls).setUpClass()
        # probably haven't made 10000 problem sets yet
        cls.pk = random.randint(1, 10000)

    def test_attempt_gives_404_for_nonexistant_problem_set(self):
        response = self.client.get(
            reverse(
                'course:attempt_problem_set',
                args=(
                    self.pk,
                )),
            secure=True)
        self.assertEqual(response.status_code, 404)

    def test_submit_gives_404_for_nonexistant_problem_set(self):
        response = self.client.post(
            reverse(
                'course:problem_submit',
                args=(
                    self.pk,
                    self.prob.pk)))
        self.assertEqual(response.status_code, 404)

    def test_results_gives_404_for_nonexistant_problem_set(self):
        response = self.client.get(
            reverse(
                'course:results_detail',
                args=(
                    self.pk,
                )))
        self.assertEqual(response.status_code, 404)


class GetExistingProblemsetTests(ProblemSetTests):
    """
    Test that pages return working for existing problem sets
    """

    def test_attempt_gives_200_for_existing_problem_set(self):
        response = self.client.get(
            reverse(
                'course:attempt_problem_set',
                args=(
                    self.pk,
                )))
        self.assertIn('poop', self.section.enrolled.all())
        self.assertEqual(response.status_code, 200)

    # 302 because the page should redirect you after you submit
    def test_submit_gives_302_for_existing_problem_set(self):
        response = self.client.post(
            reverse(
                'course:problem_submit',
                args=(
                    self.pk,
                    self.prob.pk)))
        self.assertIn('poop', self.section.enrolled.all())
        self.assertEqual(response.status_code, 302)

    def test_results_gives_200_for_existing_problem_set(self):
        response = self.client.get(
            reverse(
                'course:results_detail',
                args=(
                    self.pk,
                )))
        self.assertIn('poop', self.section.enrolled.all())
        self.assertEqual(response.status_code, 200)

    # checks for the name of the problem set on the index page
    def test_ps_index_lists_existing_problem_sets(self):
        response = self.client.get(reverse('course:problem_set_index'))
        self.assertIn('poop', self.section.enrolled.all())
        self.assertIn(self.ps.title, str(response.content))


class CantSeeFutureAssignmentsTests(ProblemSetTests):
    """
    Tests if you can see problem sets with their pubdate in the future
    """
    @classmethod
    def setUpClass(cls):
        super(CantSeeFutureAssignmentsTests, cls).setUpClass()
        # makes the ps's pub date in the future
        cls.ps.pub_date = timezone.now() + datetime.timedelta(days=5)
        cls.ps.save()

    def test_attempt_gives_404_for_future_problem_set(self):
        response = self.client.get(
            reverse(
                'course:attempt_problem_set',
                args=(
                    self.ps.pk,
                )))
        self.assertEqual(response.status_code, 404)

    def test_submit_gives_404_for_future_problem_set(self):
        response = self.client.post(
            reverse(
                'course:problem_submit',
                args=(
                    self.ps.pk,
                    self.prob.pk)))
        self.assertEqual(response.status_code, 404)

    def test_results_gives_404_for_future_problem_set(self):
        response = self.client.get(
            reverse(
                'course:results_detail',
                args=(
                    self.ps.pk,
                )))
        self.assertEqual(response.status_code, 404)

    # Checks that the future ps is not on the index page
    def test_ps_index_doesnt_list_future_problem_sets(self):
        response = self.client.get(reverse('course:problem_set_index'))
        self.assertNotIn(self.ps.title, str(response.content))


class TangoFormTests(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        User.objects.create_superuser(
            ADMIN_USERNAME, 'fake@example.com', ADMIN_PASSWORD)

    # helper function that logs in to the admin side
    def _login(self):
        self.driver.find_element_by_id("id_username").send_keys(ADMIN_USERNAME)
        pw = self.driver.find_element_by_id("id_password")
        pw.send_keys(ADMIN_PASSWORD)
        pw.send_keys(Keys.RETURN)

    # helper function to make a new problem
    def _new_problem(self, name):
        prob = models.Problem.objects.create(
            title=name,
            course="420",
            description="Super fun problem",
            statement="yay")
        return prob

    # adds a new solution file
    def _new_solfile(self, prob, filepath):
        with open(filepath, 'r') as f:
            sol = models.ProblemSolutionFile.objects.create(problem=prob)
            df = Dfile(f)
            sol.file_upload.save(filepath, df)
        return sol

    # helper function that fills out a form for a new problem set
    def _new_ps(self, name):
        self.driver.find_element_by_id("id_title").send_keys(name)
        self.driver.find_element_by_id(
            "id_description").send_keys("This is a description")
        problems = Select(self.driver.find_element_by_id('id_problems'))
        problems.select_by_index(0)

        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[1]/div/p/span[1]/a[1]").click()
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[1]/div/p/span[2]/a[1]").click()
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[2]/div/p/span[1]/a[1]").click()
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[2]/div/p/span[2]/a[1]").click()

        self.driver.find_element_by_name("_save").click()

        return name

    def _del_ps(self, name):
        # remove it from the db
        self.driver.get(self.live_server_url + "/admin/course/problemset/")
        self.driver.find_element_by_link_text(name).click()
        self.driver.find_element_by_class_name("deletelink").click()
        self.driver.find_element_by_name("post").submit()

    # get the name of the courselab on the Tango server
    def _get_courselab_name(self, name):
        return slugify(name)

    def test_new_problem_set_opens_courselab(self):
        """
        Sees if using the admin form makes a new courselab in Tango
        """
        prob = self._new_problem("fun problem")
        self.driver.get(self.live_server_url + "/admin/course/problemset/add")
        self._login()

        name = "test_ps_" + str(random.randint(1, 10000))
        self._new_ps(name)

        url = vrfy.settings.TANGO_ADDRESS + "open/" + \
            vrfy.settings.TANGO_KEY + "/" + self._get_courselab_name(name) + "/"
        response = requests.get(url)

        # clean up the db and the tango courselab folder
        self._del_ps(name)
        prob.delete()

        # if that request creates the courselab, then it wasn't created by the
        # admin app
        self.assertNotEqual(response.json()["statusMsg"], "Created directory")

    def test_new_problem_set_uploads_file(self):
        """
        Sees if using the admin form adds the file to Tango's courselabs
        """
        prob = self._new_problem("fun problem")
        sol = self._new_solfile(prob, "my_solution_file.txt")
        self.driver.get(self.live_server_url + "/admin/course/problemset/add")
        self._login()

        name = "test_ps_" + str(random.randint(1, 10000))
        self._new_ps(name)

        url = vrfy.settings.TANGO_ADDRESS + "open/" + \
            vrfy.settings.TANGO_KEY + "/" + self._get_courselab_name(name) + "/"
        response = requests.get(url)

        self._del_ps(name)
        sol.delete()
        prob.delete()

        # Check that the uploaded file is in the courselabs
        self.assertIn("my_solution_file", str(response.json()["files"]))

    def test_student_file_uploads(self):
        """
        tests if a student submitted file shows up in Tango
        """
        # first we make the problem set
        filename = "mymain.py"
        prob = self._new_problem("fun problem")
        probfile = models.RequiredProblemFilename.objects.create(
            file_title=filename, problem=prob)
        self.driver.get(self.live_server_url + "/admin/course/problemset/add")
        self._login()
        name = "test_ps_" + str(random.randint(1, 10000))
        self._new_ps(name)

        url = vrfy.settings.TANGO_ADDRESS + "open/" + \
            vrfy.settings.TANGO_KEY + "/" + self._get_courselab_name(name) + "/"
        response1 = requests.get(url)
        beforesize = len(response1.json()["files"])

        # navigate to the form
        self.driver.get(self.live_server_url + "/problem_sets/")
        self.driver.find_element_by_link_text(name).click()
        self.driver.find_element_by_partial_link_text("Attempt").click()

        # upload the file
        fileupload = self.driver.find_element_by_id(filename)
        fileupload.send_keys("/home/alex/Desktop/bull.py")
        fileupload.submit()

        response2 = requests.get(url)
        aftersize = len(response2.json()["files"])

        self._del_ps(name)
        probfile.delete()
        prob.delete()

        # Check there are more files in the courselab than before the upload
        self.assertGreater(aftersize, beforesize)

    def tearDown(self):
        self.driver.close()
