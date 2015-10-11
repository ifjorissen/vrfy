import unittest
from unittest import mock

import vrfy
import course


# Utility Object
class FakeDingus(object):
    beep = ''


class DataMaker(object):

    @classmethod
    def make_a_problem(self):
        fake_problem = FakeDingus()
        fake_problem.title = 'Problem Title'
        fake_problem.cs_course = FakeDingus()
        fake_problem.cs_course.num = 5
        fake_problem.get_upload_folder = lambda: "fake_folder/"

        return fake_problem

    @classmethod
    def make_problem_set(self):
        fake_pset = FakeDingus()
        fake_pset.title = 'The Title of This Problem Set'
        return fake_pset

    @classmethod
    def make_student_problem_set(self):
        sps = FakeDingus()
        sps.problem_set = self.make_problem_set()
        sps.user = FakeDingus()
        sps.user.username = lambda: 'catbug'
        return sps

    @classmethod
    def make_student_problem_solution(self):
        sps = FakeDingus()
        sps.problem = self.make_a_problem()
        sps.student_problem_set = self.make_student_problem_set()
        return sps


class TestPathmakers(unittest.TestCase):

    def test_student_file_upload_path(self):
        dingus = DataMaker.make_student_problem_solution()
        dingus.student_problem_solution = DataMaker.make_student_problem_solution()
        dingus.attempt_num = 1

        expected = (
            '5/folio/catbug/the-title-of-this-problem-set/' +
            'problem-title_files/v1/poot'
        )

        res = course.models.student_file_upload_path(dingus, 'poot')

        self.assertEqual(expected, res)

    @mock.patch('course.models.os')
    def test_solution_file_upload_path(self, mock_os):
        dingus = FakeDingus()
        dingus.problem = DataMaker.make_a_problem()

        folder = dingus.problem.get_upload_folder()
        file_name = 'poot'
        expected = folder + file_name
        expected_called_path = vrfy.settings.MEDIA_ROOT + expected

        res = course.models.solution_file_upload_path(dingus, file_name)

        mock_os.path.isfile.assert_called_with(expected_called_path)
        self.assertEqual(expected, res)

    @mock.patch('course.models.os')
    def test_grader_lib_upload_path(self, mock_os):
        fake_path = 'otter_pops'

        expected_new_path = 'lib/' + fake_path
        expected_checked = vrfy.settings.MEDIA_ROOT + expected_new_path
        generated_path = course.models.grader_lib_upload_path({}, fake_path)

        mock_os.path.isfile.assert_called_with(expected_checked)
        self.assertEqual(expected_new_path, generated_path)


class TestProblem(unittest.TestCase):

    def test_is_late(self):
        True

    # TODO: finish mocking this out, I hope?
    def test_latest_score(self):
        sps = mock.create_autospec(course.models.StudentProblemSolution)
        sps.job_id = 1
        sps.attempt_num = 2

        score = sps.latest_score()

        sps.problemresult_set.assert_called_with(1, 2)
