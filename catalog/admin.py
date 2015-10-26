import csv
from django.contrib import admin
from catalog.models import Reedie, Course, Section
from django.contrib.auth.models import User
from course.models import Problem
from itertools import chain
from django.utils.text import slugify
# Register your models here.
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
admin.site.unregister(User)


class ReedieInline(admin.StackedInline):
    model = Reedie
    can_delete = False

# class EnrollmentInline(admin.TabularInline):
#   model = Enrollment
#   extra = 1
#   verbose_name_plural = "Enrolled"


@admin.register(Reedie)
class ReedieAdmin(admin.ModelAdmin):
    readonly_fields = ('username', 'first_name', 'last_name', 'email', 'last_login')
    list_display = ('username', 'first_name', 'last_name', 'email', 'last_login')
    fieldsets = [
        ('Reed Profile Info', {
            'fields': [
                'user', 'first_name', 'last_name', 'last_updated', 'email', 'role']}), ]
    # inlines = (EnrollmentInline,)


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = (ReedieInline, )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'sections')

    def sections(self, obj):
        sections = obj.section_set.all()
        if len(sections) is 0:
            return None
        else:
            return ", ".join([str(section)
                              for section in obj.section_set.all()])


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    actions = ['section_gradebook_csv']
    fieldsets = [
        ('Course Info', {
            'fields': [
                'course', 'section_id', 'prof', 'start_date', 'end_date']}), ('Enrolled Students', {
                    'fields': ['enrolled']}), ]
    list_display = (
        'course_section',
        'section_id',
        'course',
        'prof',
        'start_date',
        'end_date')
    # inlines = (EnrollmentInline,)
    filter_vertical = ['enrolled']

    def section_gradebook_csv(self, request, queryset):
        '''
        creates a csv with users as rows & columns as problems
        '''
        date = timezone.now()
        title = '-'.join([s.section_id for s in queryset])
        course = queryset[0].course
        filename = "{!s}-{!s}gradebook-{}".format(
            slugify(course), title, date.strftime("%d_%m_%y"))
        response = HttpResponse(content_type="text/csv")
        response[
            'Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
        writer = csv.writer(response)
        # get all the problems assigned to this section
        for obj in queryset:
            writer = csv.writer(response)
            writer.writerow("")
            writer.writerow([obj.course_section()])
            fieldnames = ['User']
            section_problemsets = obj.problemset_set.all()
            section_problems = list(
                chain.from_iterable(
                    ps.problems.all() for ps in section_problemsets))
            fieldnames.extend([p.title for p in section_problems])
            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()
            # get all problems assigned to this section
            for user in obj.enrolled.all():
                row_dict = {'User': user.username()}
                result_dict = {(problem.title, problem.latest_score_with_usr(
                    obj, user)) for problem in section_problems}
                row_dict.update(result_dict)
                writer.writerow(row_dict)
        return response

    section_gradebook_csv.short_description = "Export the selected section as a gradebook"
