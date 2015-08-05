from django.contrib import admin
from catalog.models import Course, Section
# Register your models here.
class CourseAdmin(admin.ModelAdmin):
  list_display = ('title', 'sections')

  def sections(self, obj):
    sections = obj.section_set.all()
    if len(sections) is 0:
      return None
    else:
      return ", ".join([str(section) for section in obj.section_set.all()]) 

class SectionAdmin(admin.ModelAdmin):
    fieldsets = [
    ('Course Info', {'fields': ['course', 'prof', 'start_date', 'end_date']}),
    ('Enrolled Students', {'fields': ['enrolled', 'due_date']}),
  ]

admin.site.register(Course, CourseAdmin)
admin.site.register(Section)