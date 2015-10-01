"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'vrfy.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append an app list module for "Administration"
        self.children.append(
            modules.Group(
                title="Administration",
                column=2,
                collapsible=True,
                children=[
                    modules.ModelList(
                        _('Users'),
                        collapsible=False,
                        models=(
                            'catalog.models.Reedie',
                            'django.contrib.*',
                        ),
                    ),
                    modules.ModelList(
                        _('Enrollment'),
                        collapsible=False,
                        models=(
                            'catalog.models.Course',
                            'catalog.models.Section',
                        ),
                    )]))

        # self.children.append(modules.Group(
        #     title="Administration",
        #     column=1,
        #     collapsible=True,
        #     children=[
        #         modules.ModelList(
        #         _('Add Problems and Problem Sets'),
        #         collapsible=True,
        #         column=1,
        #         models=('course.models.GraderLib', 'course.models.Problem', 'course.models.ProblemSet'),
        #         # exclude=('django.contrib.*',),
        #     ),
        #         modules.ModelList(
        #         _('Results'),
        #         collapsible=True,
        #         column=1,
        #         models=('course.models.StudentProblemSet', 'course.models.StudentProblemSolution',),
        #     ),
        #         modules.ModelList(
        #         _('Advanced: View Previous Attempts on a Problem'),
        #         collapsible=True,
        #         column=1,
        #         models=('course.models.ProblemResult',),
        #     # exclude=('django.contrib.*',),
        #     ),

        #     ]
        # ))
        self.children.append(modules.ModelList(
            _('Add Problems and Problem Sets'),
            collapsible=True,
            column=1,
            models=(
                'course.models.GraderLib',
                'course.models.Problem',
                'course.models.ProblemSet'),
            # exclude=('django.contrib.*',),
        ))

        self.children.append(modules.ModelList(
            _('Results'),
            collapsible=True,
            column=1,
            models=('course.models.StudentProblemSet',
                    'course.models.StudentProblemSolution',),
            # exclude=('django.contrib.*',),
        ))

        self.children.append(modules.ModelList(
            _('Advanced: View Previous Attempts on a Problem'),
            collapsible=True,
            column=1,
            models=('course.models.ProblemResult',),
            # exclude=('django.contrib.*',),
        ))

        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            collapsible=False,
            column=3,
        ))
