from django.contrib import admin
from catalog.models import Reedie, Course, Section
from django.contrib.auth.models import User
# Register your models here.
from django.contrib.auth.admin import UserAdmin
admin.site.unregister(User)

class ReedieInline(admin.StackedInline):
  model = Reedie
  can_delete = False

@admin.register(Reedie)
class ReedieAdmin(admin.ModelAdmin):
  readonly_fields = ('first_name', 'last_name', 'email')
  fieldsets = [
    ('Reed Profile Info', {'fields': ['user', 'first_name', 'last_name', 'email', 'role']}),
  ]

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
      return ", ".join([str(section) for section in obj.section_set.all()]) 

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
  fieldsets = [
    ('Course Info', {'fields': ['course', 'section_id', 'prof', 'start_date', 'end_date']}),
    ('Enrolled Students', {'fields': ['enrolled']}),
  ]
  filter_vertical = ['enrolled']
