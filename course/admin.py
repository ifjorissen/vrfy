from django.contrib import admin

# Register your models here.
from .models import Problem, ProblemSet

# admin.site.register(Problem)
# admin.site.register(ProblemSet)

class ProblemAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['title', 'description', 'statement']}),
		('Course Info', {'fields': ['course']}),
	]
	list_display = ('title', 'course')

# class ProblemInline(admin.StackedInline):
# 	model = Problem
# 	extra = 1


class ProblemSetAdmin(admin.ModelAdmin):
	fieldsets = [
		('Problem Set Info', {'fields': ['title', 'description']}),
		('Problems', {'fields':['problems']}),
		('Release & Due Dates', {'fields': ['pub_date', 'due_date']}),
	]
	# inlines = [ProblemInline]
	list_display = ('title', 'pub_date', 'due_date')

admin.site.register(Problem, ProblemAdmin)
admin.site.register(ProblemSet, ProblemSetAdmin)