# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Master


def index(request):
    return HttpResponse("Test for EagleEye.")


def home(request):
    posts = Master.objects.all()
    return render(request, 'home.html', {'posts' : posts})
