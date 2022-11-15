from django.http import JsonResponse
from django.shortcuts import render
from bill_data.models import bill_data
from django.core import serializers

def dashboard_with_pivot(request):
    return render(request, 'dashboard_with_pivot.html', {})

def pivot_data(request):
    dataset = bill_data.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)