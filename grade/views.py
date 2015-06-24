from django.shortcuts import render
import sys

sys.path.append("../")
import vrfy.settings


def index(request):
    return render(request, 'grade/index.html')

def openTngo(request):
    context = {'tango_address': vrfy.settings.TANGO_ADDRESS, 'key': vrfy.settings.TANGO_KEY}
    return render(request, 'grade/open.html', context)
