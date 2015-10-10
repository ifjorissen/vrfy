# TODO:
# Add tests for:
# adding a new file to existing problem set
# changing the name of a problem set

# Core
import random
import datetime

# Django
from django.test import TransactionTestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


# TODO: Rename both of these :/
# App Models
from course import models
import catalog.models


class ProblemSetTests(TransactionTestCase):
    """
    A Model for TestCases that use Problem sets. It makes a new problem set for
    testing and then deletes it when the tests are over.
    """

    @classmethod
    def setUpClass(cls):
        cls.course = catalog.models.Course.objects.get_or_create(
            title="course_" + str(random.randint(1, 10000)),
            num=random.randint(1, 10000)
        )

        duser, created = User.objects.get_or_create(username='isjoriss')
        cls.user, created = catalog.models.Reedie.objects.get_or_create(user=duser)

        cls.section = catalog.models.Section.objects.get_or_create(
            course=cls.course,
            section_id=str(random.randint(1, 10000)),
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=60)
        )

        cls.section.enrolled.add(cls.user)

        cls.ps = models.ProblemSet.objects.get_or_create(
            title='test_ps_' + str(random.randint(1, 10000)),
            pub_date=timezone.now(),
            due_date=timezone.now() + datetime.timedelta(days=30)
        )

        cls.ps.cs_section.add(cls.section)
        cls.pk = cls.ps.pk

        cls.prob = models.Problem.objects.get_or_create(
            title='test_prob_' +
            str(random.randint(1, 10000)), cs_course=cls.course
        )

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


class NonExistantProblemSetTests(ProblemSetTests):
    """
    Tests that the course pages give a 404 when you try to access a page that
    doesnt exist
    """
    @classmethod
    def setUpClass(cls):
        super(NonExistantProblemSetTests, cls).setUpClass()
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


class GetExistingProblemSetTests(ProblemSetTests):
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

        self.assertEqual(response.status_code, 200)

    # 302 because the page should redirect you after you submit
    def test_submit_gives_302_for_existing_problem_set(self):
        response = self.client.post(
            reverse(
                'course:problem_submit',
                args=(self.pk, self.prob.pk)
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_results_gives_200_for_existing_problem_set(self):
        response = self.client.get(
            reverse('course:results_detail', args=(self.pk,))
        )
        self.assertEqual(response.status_code, 200)

    # checks for the name of the problem set on the index page
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
