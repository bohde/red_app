from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django import forms

from models import MatrixUploadFileForm, MatrixSet, matrix_select_from_model

severities = [["low", "med"] + ["high"] * 3,
              ["low"] + ["med"] * 2 + ["high"] * 2,
              ["low"] + ["med"] * 3 + ["high"],
              ["low"] * 3 + ["med"] * 2,
              ["low"] * 4 + ["med"]]

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
    """
    hss - c1, l1
    hs - c1, l2
    uss - c2, l1
    us - c2,l2
    """
    ms = MatrixSet.objects.get(pk=id)
    f = request.session.get('functions', [])
    rep = ms.run_report(f)
    # put the 5x5 matrices in (val, severity) format
    vals = (zip(*f) for f in zip(rep, severities))
    return render_to_response("fever_chart.html", {"id":id, "pd":pd, "report":vals})

def run_text_report(request, id, pd):
    return render_to_response("risk_report.txt", locals(), mimetype="text/plaintext")
