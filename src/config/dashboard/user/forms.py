from django import forms
from config.user.models import User, Role, AgentInformation

class RoleChoiceField(forms.ModelChoiceField):
    def name_from_instance(self, obj):
        return obj.name

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), required=False, label="Пароль")

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        user.is_active = True
        user.is_staff = True
        if commit:
            user.save()
        return user
    
    class Meta:
        model = User
        fields = "__all__"
        exclude = ("status", "image", 'location', 'role', 'password')
        labels = {
            "firstname": "Имя",
            "lastname": "Фамилия",
            "phone_number": "Номер телефона",
            "username": "Имя пользователя",
            # "email": "Электронный адрес",
            "image": "Изображение профиля",
        }
        widgets = {
            "firstname": forms.TextInput(attrs={"class": "form-control"}),
            "lastname": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            # "email": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserProfileForm(forms.ModelForm):
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ("firstname", 'lastname', "phone_number", "username")
        labels = {
            "firstname": "Имя",
            "lastname": "Фамилия",
            "phone_number": "Номер телефона",
            "username": "Имя пользователя",
            # "email": "Электронный адрес",
            "image": "Изображение профиля",
        }
        widgets = {
            "firstname": forms.TextInput(attrs={"class": "form-control"}),
            "lastname": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            # "email": forms.TextInput(attrs={"class": "form-control"}),
        }
        
class AgentInformationForm(forms.ModelForm):
    is_merried = forms.ChoiceField(
        label="Семейное положение", required=True, choices=[(1, "Not Merried"), (2, "Merried"), (3, "Divorced")],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    birthday = forms.DateField(
        label="Дата рождения", required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['agent'] = self.instance.agent
    
    def save(self, commit=True):
        agent = super().save(commit=False)
        if commit:
            agent.save()
        return agent
    
    class Meta:
        model = AgentInformation
        fields = "__all__"
        exclude = ("agent", )
        labels = {
            "passport": "Паспорт",
            "inn": "ИНН",
            "dad_name": "Имя отца",
            "dad_phone": "Телефонный номер отца",
            "mom_name": "Имя матери",
            "mom_phone": "Телефонный номер матери",
            
        }
        widgets = {
            "passport": forms.TextInput(attrs={"class": "form-control"}),
            "inn": forms.TextInput(attrs={"class": "form-control"}),
            "dad_name": forms.TextInput(attrs={"class": "form-control"}),
            "dad_phone": forms.TextInput(attrs={"class": "form-control"}),
            "mom_name": forms.TextInput(attrs={"class": "form-control"}),
            "mom_phone": forms.TextInput(attrs={"class": "form-control"}),
        }