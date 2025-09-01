from django import forms
from django.contrib.auth.models import User
from . import models


class PerfilForm(forms.ModelForm):
    """Formulário para dados do perfil"""
    class Meta:
        model = models.Perfil
        exclude = ('usuario',)  # o usuário será associado no view


class UserForm(forms.ModelForm):
    """Formulário para criação e atualização de usuário"""
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Senha'
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmação de senha'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario  # usuário logado (None se for cadastro)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'password2', 'email')

    def clean(self):
        cleaned = self.cleaned_data
        username = cleaned.get('username')
        email = cleaned.get('email')
        password = cleaned.get('password')
        password2 = cleaned.get('password2')

        errors = {}

        # Usuário logado: atualização
        if self.usuario:
            if User.objects.filter(username=username).exclude(pk=self.usuario.pk).exists():
                errors['username'] = 'Usuário já existe'
            if User.objects.filter(email=email).exclude(pk=self.usuario.pk).exists():
                errors['email'] = 'E-mail já existe'
            if password and password != password2:
                errors['password'] = errors['password2'] = 'As senhas não conferem'
            if password and len(password) < 6:
                errors['password'] = 'Sua senha precisa ter pelo menos 6 caracteres'

        # Usuário novo: cadastro
        else:
            if User.objects.filter(username=username).exists():
                errors['username'] = 'Usuário já existe'
            if User.objects.filter(email=email).exists():
                errors['email'] = 'E-mail já existe'
            if not password:
                errors['password'] = 'Este campo é obrigatório'
            if not password2:
                errors['password2'] = 'Este campo é obrigatório'
            if password and password2 and password != password2:
                errors['password'] = errors['password2'] = 'As senhas não conferem'
            if password and len(password) < 6:
                errors['password'] = 'Sua senha precisa ter pelo menos 6 caracteres'

        if errors:
            raise forms.ValidationError(errors)
