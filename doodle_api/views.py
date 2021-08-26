from django.shortcuts import render
from django.views import generic


class HomeView(generic.TemplateView):
    """ Index page """

    template_name = 'index.html'


