from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django import forms

from models import MatrixUploadFileForm, MatrixSet, matrix_select_from_model

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


pd_choices = (
    ("hs", "Human Centric, System Level"),
    ("hss", "Human Centric, Subsystem Level"),
    ("us", "Unmanned, System Level"),
    ("uss", "Unmanned, Subsystem Level"))

def display_matrix(request, id):
    return render_to_response('pd_choices.html', {'id':int(id), 'choices':pd_choices})

def display_matrix_functions(request, id, pd):
    if request.method == 'POST':
        form = matrix_select_from_model(id)(request.POST)
        if form.is_valid():
            request.session['functions'] = [int(x) for x in  form.cleaned_data['choices']]
            return HttpResponseRedirect(reverse('red-fever-report', args=(id, pd), current_app='red'))
    else:
        form = matrix_select_from_model(id)()
    return render_to_response('functions.html', {'id':id, 'pd':pd, 'form':form})


def run_fever_report(request, id, pd):
    print request.session.get('functions', [])
    return render_to_response("fever_chart.html", locals())

def run_text_report(request, id, pd):
    return render_to_response("risk_report.txt", locals(), mimetype="text/plaintext")
