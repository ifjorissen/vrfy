import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from . import views
from .models import ProblemSet

class NonExistantProblemsetTests(TestCase):
  """
  Tests that the course pages give a 404 when you try to access a page that doesnt exist
  """
  #makes a new problem set, gets the primary key then deletes the problem set so
  #we know that this pk is attached to no item in the db
  _ps = ProblemSet(title='test_ps', pub_date=timezone.now(), due_date=timezone.now() + datetime.timedelta(days=30))
  _ps.save()
  pk = _ps.pk
  _ps.delete()


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
