from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import pre_save
from django.dispatch import receiver

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('É obrigatório um email válido')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save()
        print('------------criando user')
        return user
    # create_super_user para criar super usuário   
    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    last_name = models.CharField(max_length=255, verbose_name="Sobrenome")
    first_name = models.CharField(max_length=255, verbose_name="Nome")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_staff = models.BooleanField(default=False, verbose_name="Usuário Master")
    objects = UserAccountManager()
    # SETA O CAMPO UTILIZADO NO LOGIN
    USERNAME_FIELD = 'email'
    # SETAR O CAMPOS OBRIGATÓRIOS: so add na array
    # REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.first_name + ' ' +self.last_name

    def get_short_name(self):
        return self.first_name

    class Meta:
        # managed = True
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email


# Create your models here.
# @receiver(pre_save, sender=UserAccount)
# def create_pagseguro_plan(sender, instance, **kwargs):
#     if instance:
#         return self
#     else:

#         create_plan(instance)