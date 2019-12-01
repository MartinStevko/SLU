from django.urls import path

from content.views import ContentView, ContactView, DumpdataView

app_name = 'content'

urlpatterns = [
    path('dumpdata/all/', DumpdataView.as_view()),
    path('ultimate/', ContentView.as_view(title='ultimate'), name='ultimate'),
    path('rules/', ContentView.as_view(title='rules'), name='rules'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('', ContentView.as_view(title='news'), name='home'),
]
