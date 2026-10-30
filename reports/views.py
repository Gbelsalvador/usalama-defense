from django.shortcuts import redirect, render
from .forms import ReportForm, anonymiser
from .models import Report

def report(request):
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Report.objects.create(texte=anonymiser(form.cleaned_data["texte"]),
                              type_arnaque=form.cleaned_data["type_arnaque"],
                              langue=request.LANGUAGE_CODE)
        return redirect("reports:thanks")
    return render(request, "reports/form.html", {"form": form})

def thanks(request):
    return render(request, "reports/thanks.html")
