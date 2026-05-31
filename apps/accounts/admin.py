from apps.accounts.models import Gender
from apps.accounts.models import Profile
from django.contrib import admin

@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    class Meta:
        model = Gender
        fields = '__all__'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    class Meta:
        model = Profile
        fields = '__all__'
