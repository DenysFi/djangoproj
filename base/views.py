from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

#LoginRequiredMixin проверяет, авторизирован ли пользователь, если нет, его направляет на страничку со входом 

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

# регистрация
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request,user)
        return super(RegisterPage,self).form_valid(form)

    #если пользователь вбивает в адрессную строку login и при этом он авторизирован, его выбивает на старницу с заданиями 
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage,self).get(*args, **kwargs)

# вывод задач для пользователя 
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs) :
       context = super().get_context_data(**kwargs)
       context['tasks'] =  context['tasks'].filter(user = self.request.user)
       context['count'] =  context['tasks'].filter(complete = False).count()

       search_input = self.request.GET.get('search-area') or ''
       if search_input:
             context['tasks'] =  context['tasks'].filter(title__startswith = search_input)
       context['search_input'] = search_input
       return context


class TaskDetale(LoginRequiredMixin,DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

#создание задачи
class TaskCreate(LoginRequiredMixin,CreateView):
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(TaskCreate,self).form_valid(form)

#обновление задачи
class TaskUptade(LoginRequiredMixin,UpdateView):
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks')

# удаление задачи
class DeleteView(LoginRequiredMixin,DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')