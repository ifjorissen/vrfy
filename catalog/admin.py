from django.contrib import admin
from catalog.models import Course, Section
# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
  list_display = ('title', 'sections')

  def sections(self, obj):
    sections = obj.section_set.all()
    if len(sections) is 0:
      return None
    else:
      return ", ".join([str(section) for section in obj.section_set.all()]) 

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
  fieldsets = [
    ('Course Info', {'fields': ['course', 'prof', 'start_date', 'end_date']}),
    ('Enrolled Students', {'fields': ['enrolled']}),
  ]
  filter_vertical = ['enrolled']
