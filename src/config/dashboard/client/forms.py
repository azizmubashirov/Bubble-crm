from django import forms
from config.client.models import Client

class RoleChoiceField(forms.ModelChoiceField):
    def name_from_instance(self, obj):
        return obj.name

class ClientForm(forms.ModelForm):
    # location = forms.JSONField(required=False, disabled=True)
    # latitude = forms.CharField(
    #     max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'})
    # )
    # longitude = forms.CharField(
    #     max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'})
    # )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.initial['latitude'] = self.instance.location.get("latitude", {})
        # self.initial['longitude'] = self.instance.location.get("longitude", {})
        self.initial['agent'] = self.instance.agent

    def clean(self):
        cleaned_data = self.cleaned_data
        # cleaned_data['location'] = {
        #     "latitude": self.cleaned_data.get('latitude'),
        #     "longitude": self.cleaned_data.get('longitude')
        # }
        return cleaned_data
    
    class Meta:
        model = Client
        fields = "__all__"
        exclude = ("location",)
        labels = {
            "firstname": "Имя",
            "lastname": "Фамилия",
            "company_name": "Название компании",
            "inn": "ИНН",
            # "email": "Электронная почта",
            "address": "Адрес",
            "location_link": "Локация",
        }
        widgets = {
            "firstname": forms.TextInput(attrs={"class": "form-control", 'placeholder': 'Имя'}),
            "lastname": forms.TextInput(attrs={"class": "form-control", 'placeholder': 'Фамилия'}),
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "inn": forms.TextInput(attrs={"class": "form-control", 'required': False}),
            # "email": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control", 'required':False}),
            "location_link": forms.TextInput(attrs={"class": "form-control", 'required':False}),
        }