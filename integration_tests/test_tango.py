# Core
import random

# 3rd Party
import requests

# Django
from django.test import LiveServerTestCase
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.files import File as Dfile

# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# vrfy
from course import models
import vrfy.settings

# Mocks
from httmock import with_httmock
from integration_tests import tango_mock

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"


class TangoFormTests(LiveServerTestCase):

    def _testMethodName():
        return "poot?"

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
            cs_course=models.Course.objects.create(title="BorkBork", num=420),
            description="Super fun problem",
            statement="yay"
        )
        # prob.save()
        return prob

    # Adds a new solution file
    # TODO: replace with mock?
    def _new_solfile(self, prob, filepath):
        with open(filepath, 'r') as f:
            df = Dfile(f)
            sol = models.ProblemSolutionFile.objects.create(
                problem=prob,
                file_upload=df,
                comment="fake"
            )
            sol.file_upload.save(filepath, df)
        return sol

    # helper function that fills out a form for a new problem set
    def _new_ps(self, name):
        self.driver.find_element_by_id("id_title").send_keys(name)
        self.driver.find_element_by_id(
            "id_description").send_keys("This is a description")
        problems = Select(self.driver.find_element_by_id('id_problems'))
        problems.select_by_index(0)

        # Oh dang. On the one hand, it's really good to check this; on the other
        # hand, this approach to testing is *super* brittle -- that is, the
        # moment you change anything about your templates, this'll explode. It
        # may already be exploding. Whee.
        #
        # I'ma see if I can't help find a way to make this test more... durable.
        # RMD - 2015-10-05
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[1]/div/p/span[1]/a[1]").click()
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[1]/div/p/span[2]/a[1]").click()
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[2]/div/p/span[1]/a[1]").click()
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[2]/div/p/span[2]/a[1]").click()

        self.driver.find_element_by_name("_save").click()

        return name

    def _del_ps(self, name):
        """
        Remove a problem set from the DB, by name, using the delete web form"""
        self.driver.get(self.live_server_url + "/admin/course/problemset/")
        self.driver.find_element_by_link_text(name).click()
        self.driver.find_element_by_class_name("deletelink").click()
        self.driver.find_element_by_name("post").submit()

    # get the name of the courselab on the Tango server
    # That isn't what this does? This is just a dispatch around Django's `slugify`.
    def _get_courselab_name(self, name):
        return slugify(name)

    # I can't figure out how to reason about this one; disabling it until I can
    # get an understanding of what it, uh, does.
    # def test_new_problem_set_opens_courselab(self):
    #     """
    #     Sees if using the admin form makes a new courselab in Tango
    #     """
    #     prob = self._new_problem("fun problem")
    #     self.driver.get(self.live_server_url + "/admin/course/problemset/add")
    #     self._login()

    #     name = "test_ps_" + str(random.randint(1, 10000))
    #     self._new_ps(name)

    #     url = vrfy.settings.TANGO_ADDRESS + "open/" + \
    #         vrfy.settings.TANGO_KEY + "/" + self._get_courselab_name(name) + "/"
    #     response = requests.get(url)

    #     # clean up the db and the tango courselab folder
    #     self._del_ps(name)
    #     prob.delete()

    #     # if that request creates the courselab, then it wasn't created by the
    #     # admin app
    #     self.assertNotEqual(response.json()["statusMsg"], "Created directory")

    # @with_httmock(tango_mock.open)
    # def test_new_problem_set_uploads_file(self):
    #     """
    #     Sees if using the admin form adds the file to Tango's courselabs
    #     """
    #     prob = self._new_problem("fun problem")
    #     sol = self._new_solfile(prob, "my_solution_file.txt")
    #     self.driver.get(self.live_server_url + "/admin/course/problemset/add")
    #     self._login()

    #     name = "test_ps_" + str(random.randint(1, 10000))
    #     self._new_ps(name)

    #     url = vrfy.settings.TANGO_ADDRESS + "open/" + \
    #         vrfy.settings.TANGO_KEY + "/" + self._get_courselab_name(name) + "/"
    #     response = requests.get(url)

    #     self._del_ps(name)
    #     sol.delete()
    #     prob.delete()

    #     # Check that the uploaded file is in the courselabs
    #     self.assertIn("my_solution_file", str(response.json()["files"]))

    # def test_student_file_uploads(self):
    #     """
    #     tests if a student submitted file shows up in Tango
    #     """
    #     # first we make the problem set
    #     filename = "mymain.py"
    #     prob = self._new_problem("fun problem")
    #     probfile = models.RequiredProblemFilename.objects.create(
    #         file_title=filename,
    #         problem=prob
    #     )
    #     self.driver.get(self.live_server_url + "/admin/course/problemset/add")
    #     self._login()
    #     name = "test_ps_" + str(random.randint(1, 10000))
    #     self._new_ps(name)

    #     url = vrfy.settings.TANGO_ADDRESS + "open/" + \
    #         vrfy.settings.TANGO_KEY + "/" + self._get_courselab_name(name) + "/"
    #     response1 = requests.get(url)
    #     beforesize = len(response1.json()["files"])

    #     # navigate to the form
    #     self.driver.get(self.live_server_url + "/problem_sets/")
    #     self.driver.find_element_by_link_text(name).click()
    #     self.driver.find_element_by_partial_link_text("Attempt").click()

    #     # upload the file
    #     fileupload = self.driver.find_element_by_id(filename)
    #     fileupload.send_keys("/home/alex/Desktop/bull.py")
    #     fileupload.submit()

    #     response2 = requests.get(url)
    #     aftersize = len(response2.json()["files"])

    #     self._del_ps(name)
    #     probfile.delete()
    #     prob.delete()

    #     # Check there are more files in the courselab than before the upload
    #     self.assertGreater(aftersize, beforesize)

    # def tearDown(self):
    #     self.driver.close()
