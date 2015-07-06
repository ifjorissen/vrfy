import random
import datetime
import requests
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from django.core.urlresolvers import reverse

import sys
sys.path.append("../")
import vrfy.settings

from . import views
from .models import ProblemSet

class ProblemSetTests(TestCase):
  """
  A Model for TestCases that use Problem sets 
  It makes a new problem set for testing and then deletes it when the tests are over
  """
  @classmethod
  def setUpClass(cls):
    cls.ps = ProblemSet(title='test_ps_' + str(random.randint(1,10000)), pub_date=timezone.now(), due_date=timezone.now() + datetime.timedelta(days=30))
    cls.ps.save()
    cls.pk = cls.ps.pk
    super(ProblemSetTests, cls).setUpClass()
  
  @classmethod
  def tearDownClass(cls):
    #if the ps still exists, delete it
    if cls.ps.id != None :
      cls.ps.delete()
    super(ProblemSetTests, cls).tearDownClass()
  
class NonExistantProblemsetTests(ProblemSetTests):
  """
  Tests that the course pages give a 404 when you try to access a page that doesnt exist
  """
  @classmethod
  def setUpClass(cls):
    super(NonExistantProblemsetTests, cls).setUpClass()
    cls.ps.delete()

  def test_attempt_gives_404_for_nonexistant_problem_set(self):
    response = self.client.get(reverse('course:attempt_problem_set', args=(self.pk,)))
    self.assertEqual(response.status_code, 404)

  def test_detail_gives_404_for_nonexistant_problem_set(self):
    response = self.client.get(reverse('course:problem_set_detail', args=(self.pk,)))
    self.assertEqual(response.status_code, 404)

  def test_submit_gives_404_for_nonexistant_problem_set(self):
    response = self.client.post(reverse('course:problem_set_submit', args=(self.pk,)))
    self.assertEqual(response.status_code, 404)

  def test_results_gives_404_for_nonexistant_problem_set(self):
    response = self.client.get(reverse('course:results_detail', args=(self.pk,)))
    self.assertEqual(response.status_code, 404)
  
class GetExistingProblemsetTests(ProblemSetTests):
  """
  Test that pages return working for existing problem sets 
  """
  
  def test_attempt_gives_200_for_existing_problem_set(self):
    response = self.client.get(reverse('course:attempt_problem_set', args=(self.pk,)))
    self.assertEqual(response.status_code, 200)

  def test_detail_gives_200_for_existing_problem_set(self):
    response = self.client.get(reverse('course:problem_set_detail', args=(self.pk,)))
    self.assertEqual(response.status_code, 200)

  #302 because the page should redirect you after you submit
  def test_submit_gives_302_for_existing_problem_set(self):
    response = self.client.post(reverse('course:problem_set_submit', args=(self.pk,)))
    self.assertEqual(response.status_code, 302)

  def test_results_gives_200_for_existing_problem_set(self):
    response = self.client.get(reverse('course:results_detail', args=(self.pk,)))
    self.assertEqual(response.status_code, 200)

  #checks for the name of the problem set on the index page
  def test_ps_index_lists_existing_problem_sets(self):
    response = self.client.get(reverse('course:problem_set_index'))
    self.assertIn(self.ps.title, str(response.content))

class CantSeeFutureAssignmentsTests(ProblemSetTests):
  """
  Tests if you can see problem sets with their pubdate in the future
  """
  @classmethod
  def setUpClass(cls):
    super(CantSeeFutureAssignmentsTests, cls).setUpClass()
    #makes the ps's pub date in the future
    cls.ps.pub_date = timezone.now() + datetime.timedelta(days=5)
    cls.ps.save()
    
  def test_attempt_gives_404_for_future_problem_set(self):
    response = self.client.get(reverse('course:attempt_problem_set', args=(self.ps.pk,)))
    self.assertEqual(response.status_code, 404)

  def test_detail_gives_404_for_future_problem_set(self):
    response = self.client.get(reverse('course:problem_set_detail', args=(self.ps.pk,)))
    self.assertEqual(response.status_code, 404)

  def test_submit_gives_404_for_future_problem_set(self):
    response = self.client.post(reverse('course:problem_set_submit', args=(self.ps.pk,)))
    self.assertEqual(response.status_code, 404)

  def test_results_gives_404_for_future_problem_set(self):
    response = self.client.get(reverse('course:results_detail', args=(self.ps.pk,)))
    self.assertEqual(response.status_code, 404)

  #Checks that the future ps is not on the index page
  def test_ps_index_doesnt_list_future_problem_sets(self):
    response = self.client.get(reverse('course:problem_set_index'))
    self.assertNotIn(self.ps.title, str(response.content))

class AdminSubmissionTests(TestCase):

  def test_admin_makes_new_courselab_in_tango_when_making_new_problem_set(self):
    name = 'test_ps_' + str(random.randint(1,10000))
    r = self.client.post(reverse('admin:course_problemset_add'), {'title' : name, 'description' : 'something', '_save': ['Save'], 'pub_date_0': ['2015-07-02'], 'due_date_0': ['2015-07-02'], 'problems': ['2'], 'pub_date_1': ['18:03:53'], 'csrfmiddlewaretoken': ['CEOH3CWH8Er8hnWedEDwsC1PeBk3XoR0'], 'due_date_1': ['18:03:55']})
    self.assertEqual(r.status_code, False)
    url = vrfy.settings.TANGO_ADDRESS + "open/" + vrfy.settings.TANGO_KEY + "/" + slugify(name) + "/"
    response = requests.get(url)
    #if this command creats the courselab, then it wasn't created by the admin
    self.assertNotEqual(response.json()["statusMsg"], "Created directory")

