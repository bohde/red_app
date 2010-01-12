from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from models import MatrixUploadFileForm, MatrixSet

def index(request):
    return render_to_response('index.html')

def upload(request):
    if request.method == 'POST':
        form = MatrixUploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()
            return HttpResponseRedirect(reverse('red-display-matrix', args=(data.id,), current_app='red'))
    else:
        form = MatrixUploadFileForm()
    return render_to_response('upload.html', {'form':form})

def display_matrices(request):
    matrices = MatrixSet.objects.all()
    return render_to_response('matrices.html', {'matrices':matrices})

def display_matrix(request, id):
    return HttpResponse("I display a matrix stuff")
