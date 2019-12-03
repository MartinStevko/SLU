from django.contrib.admin.apps import AdminConfig


class OrderedAdminSiteConfig(AdminConfig):
    default_site = 'app.admin.OrderedAdminSite'
