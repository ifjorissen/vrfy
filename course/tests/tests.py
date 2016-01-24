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
        fake_problem.id = 2
        fake_problem.cs_course = FakeDingus()
        fake_problem.cs_course.num = 5
        fake_problem.get_upload_folder = lambda: "fake_folder/"

        return fake_problem

    @classmethod
    def make_problem_set(self):
        fake_pset = FakeDingus()
        fake_pset.title = 'The Title of This Problem Set'
        fake_pset.id = 3
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
        sps.id = 4
        sps.problem = self.make_a_problem()
        sps.student_problem_set = self.make_student_problem_set()
        return sps

    @classmethod
    def make_grader_lib(self):
        grader_lib = FakeDingus()
        grader_lib.id = 6
        grader_lib.cs_course = FakeDingus()
        grader_lib.cs_course.num = 5
        return grader_lib

class TestPathmakers(unittest.TestCase):

    def test_student_file_upload_path(self):
        dingus = DataMaker.make_student_problem_solution()
        dingus.student_problem_solution = DataMaker.make_student_problem_solution()
        dingus.attempt_num = 1

        expected = (
            'cs5/folio/catbug/the-title-of-this-problem-set_3/' +
            'problem-title_2_files/v1/poot'
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
        dingus = DataMaker.make_grader_lib()
        fake_path = 'otter_pops'

        expected_new_path = 'cs5/lib/' + fake_path
        expected_checked = vrfy.settings.MEDIA_ROOT + expected_new_path

        # Path doesn't exist, rm should not be called
        mock_os.path.isfile.return_value = False

        generated_path = course.models.grader_lib_upload_path(dingus, fake_path)

        mock_os.path.isfile.assert_called_with(expected_checked)
        mock_os.remove.assert_not_called()
        self.assertEqual(expected_new_path, generated_path)

        # Path exists
        mock_os.path.isfile.return_value = True

        generated_path = course.models.grader_lib_upload_path(dingus, fake_path)

        mock_os.path.isfile.assert_called_with(expected_checked)
        mock_os.remove.assert_called_with(vrfy.settings.MEDIA_ROOT +
                                          generated_path)
        self.assertEqual(expected_new_path, generated_path)
