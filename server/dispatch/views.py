# Create your views here.
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from dispatch.forms import PackageForm, CourierForm
from dispatch.models import Package, Courier, Client
from dispatch.models import ETurtleGroup as Group
from utils import AdminOr404Mixin, WebLoginRequiredMixin
from registration.signals import user_registered
from django.dispatch import receiver


#signal catch for user registration
@receiver(user_registered)
def set_group_of_registered_user(sender, **kwargs):
    user = kwargs.get('user')
    user.groups.add(Group.client())

class PackageListView(WebLoginRequiredMixin, ListView):
    model = Package

    def get_queryset(self):
        queryset = super(PackageListView,self).get_queryset()

        if not self.request.user.has_perm('dispatch.eturtle_admin'):
            queryset = queryset.filter(client = self.request.user)

        return queryset

class PackageCreateView(WebLoginRequiredMixin, CreateView):
    form_class = PackageForm
    template_name = 'dispatch/package_create.html'

    def form_valid(self, form):
        self.package = form.save(commit=False)
        self.package.client = self.request.user
        self.package.save()
        return super(PackageCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('package_list', kwargs={})

class CourierListView(AdminOr404Mixin, ListView):
    model = Courier

class CourierCreateView(WebLoginRequiredMixin, CreateView):
    form_class = CourierForm
    template_name = 'dispatch/courier_create.html'

    def form_valid(self, form):
        self.courier = form.save(commit=False)
        self.courier.set_password(form.cleaned_data.get('pw1'))
        self.courier.save()
        self.courier.groups.add(Group.courier())
        return super(CourierCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('courier_list', kwargs={})

class ClientListView(AdminOr404Mixin, ListView):
    model = Client