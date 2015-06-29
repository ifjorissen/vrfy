from django.contrib import admin

# Register your models here.
from .models import Problem, ProblemSet, RequiredProblemFilename, ProblemSolutionFile

# admin.site.register(Problem)
# admin.site.register(ProblemSet)

# class ProblemSolutionInline(admin.TabularInline):
# 	model = ProblemSolution
# 	extra = 1

class RequiredProblemFilenameInline(admin.TabularInline):
	model = RequiredProblemFilename
	extra = 3


class ProblemSolutionFileInline(admin.TabularInline):
	model = ProblemSolutionFile
	extra = 3


# class ProblemSolutionAdmin(admin.ModelAdmin):
# 	class Meta:
# 		model = ProblemSolution
		
# 	inlines = [ProblemSolutionFileInline]


class ProblemAdmin(admin.ModelAdmin):
	class Meta:
		model = Problem

	fieldsets = [
		('Problem Info', {'fields': ['title', 'description', 'statement', 'many_attempts']}),
		# ('Required Files', {'fields': ['problem_files']}),
		('Course Info', {'fields': ['course']}),
	]
	inlines = [RequiredProblemFilenameInline, ProblemSolutionFileInline]
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


# admin.site.register(RequiredProblemFilename, RequiredProblemFilenameAdmin)
# admin.site.register(ProblemSolution, ProblemSolutionAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(ProblemSet, ProblemSetAdmin)