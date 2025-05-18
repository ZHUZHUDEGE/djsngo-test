from django.shortcuts import render

# Create your views here.
def index(request):
    # return HttpResponse('Hello, Django!')
    return render(request, 'hello_django/index.html')

def find_all(request):
    return render(request, 'hello_django/find_all.html')