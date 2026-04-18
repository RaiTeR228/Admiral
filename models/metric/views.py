from django.shortcuts import render

from django.shortcuts import render
from django.views import View

class StatsDashboardView(View):
    template_name = 'metric/dashboard.html'
    
    def get(self, request):
        context = {
            'api_url': 'api/stats/list/',  
        }
        return render(request, self.template_name, context)