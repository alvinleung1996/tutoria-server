from django.views.generic.base import TemplateView
from django.conf import settings
from django.urls import reverse

class IndexView(TemplateView):

    template_name = 'tutoriaserver/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rootPath'] = reverse('index')
        # TODO: prevent hard coding
        context['apiRootPath'] = '/api/'
        context['staticRootPath'] = settings.STATIC_URL + 'tutoriaserver/'
        return context
