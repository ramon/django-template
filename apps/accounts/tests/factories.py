"""Factories dos modelos de accounts, para os testes nao construirem objetos a mao."""

from typing import Any

import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Profile, User


class UserFactory(DjangoModelFactory[User]):
    class Meta:
        model = User
        skip_postgeneration_save = True

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    # celular de Sao Paulo em E.164; o PhoneNumberMixin valida o formato ao ler.
    phone_number = factory.Sequence(lambda n: f"+55119{n:08d}")
    password = "senha-de-teste-123"

    @classmethod
    def _create(cls, model_class: type[User], *args: Any, **kwargs: Any) -> User:
        """
        Usa o create_user do manager, nao o objects.create padrao do factory_boy.

        So o create_user hasheia a senha e cria o Profile associado -- sem ele o
        usuario nasce sem perfil e com a senha em texto puro.
        """
        password = kwargs.pop("password")
        return model_class.objects.create_user(password=password, **kwargs)


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class ProfileFactory(DjangoModelFactory[Profile]):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    birth_date = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)

    @classmethod
    def _create(cls, model_class: type[Profile], *args: Any, **kwargs: Any) -> Profile:
        """
        Atualiza o perfil que o create_user ja criou, em vez de inserir outro.

        Profile.user e' OneToOne: um segundo insert para o mesmo usuario violaria
        a constraint.
        """
        user = kwargs.pop("user")
        profile, _ = model_class.objects.update_or_create(user=user, defaults=kwargs)
        return profile
