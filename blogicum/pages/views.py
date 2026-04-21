from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
def page_not_found(request, exception):
    # Объект исключения передается автоматически (свойство handler404)
    return render(request, 'pages/404.html', status=404)

def server_error(request):
    return render(request, 'pages/500.html', status=500)

def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


class AboutPage(TemplateView):
    template_name = 'pages/about.html'
