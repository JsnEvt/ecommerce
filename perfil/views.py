from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import copy

from . import models
from . import forms


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))
        self.perfil = None

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(usuario=self.request.user).first()
            self.template_name = 'perfil/atualizar.html'
            self.contexto = {
                'userform': forms.UserForm(data=self.request.POST or None,
                                           usuario=self.request.user,
                                           instance=self.request.user),
                'perfilform': forms.PerfilForm(data=self.request.POST or None,
                                               instance=self.perfil)
            }
        else:
            self.contexto = {
                'userform': forms.UserForm(data=self.request.POST or None),
                'perfilform': forms.PerfilForm(data=self.request.POST or None)
            }

        self.userform = self.contexto["userform"]
        self.perfilform = self.contexto["perfilform"]
        self.renderizar = render(self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        # Validação dos formulários
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            print('Formulários inválidos')
            return self.renderizar

        print('Formulários válidos')

        # Captura dados do userform
        user_data = self.userform.cleaned_data
        perfil_data = self.perfilform.cleaned_data
        username = user_data.get('username')
        password = user_data.get('password')
        email = user_data.get('email')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')

        if self.request.user.is_authenticated:
            # Usuário logado: atualizar
            usuario = get_object_or_404(User, username=self.request.user.username)
            usuario.username = username
            if password:
                usuario.set_password(password)
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        else:
            # Novo usuário: criar
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        # Autenticação
        if password:
            autentica = authenticate(self.request, username=username, password=password)
            if autentica:
                login(self.request, user=usuario)

        # Atualiza sessão
        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()

        return self.renderizar


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
                self.request,
                'Usuário ou senha inválidos.'
            )
            return redirect('perfil:criar')

        usuario = authenticate(
            self.request, username=username, password=password)

        if not usuario:
            messages.error(
                self.request,
                'Usuário ou senha inválidos.'
            )
            return redirect('perfil:criar')

        login(self.request, user=usuario)

        messages.success(
            self.request,
            'Você fez login no sistema e pode concluir sua compra.'
        )
        return redirect('produto:carrinho')

class Logout(View):
    def get(self, *args, **kwargs):
        carrinho = copy.deepcopy(self.request.session.get('carrinho'))

        logout(self.request)

        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        return redirect('produto:lista')