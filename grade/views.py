from django.shortcuts import render
from django.views.generic.edit import CreateView

from .models import Assignment

def index(request):
    return render(request, 'grade/index.html')

class AssignmentCreate(CreateView):
    model = Assignment
    fields = '__all__'

