from django import forms
from config.order.models import Order, OrderItem, Payment
from config.client.models import Client
from config.user.models import User

class PaymenttChoiceField(forms.ModelChoiceField):
    def name_from_instance(self, obj):
        return obj.name

class ClientChoiceField(forms.ModelChoiceField):
    def name_from_instance(self, obj):
        return f"{obj.firstname} {obj.lastname} {obj.company_name} {obj.inn}"

class OrderForm(forms.ModelForm):
    price_type = forms.ChoiceField(
        label="Вид цены", required=True, choices=[('A', "A"), ("B", "B"), ('C', "C")],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    client = ClientChoiceField(
        label="Клиент", required=True, queryset=Client.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'data-control':"select2", 'data-placeholder':"Select an Client"})
    )
    location = forms.CharField(
        label="локации",
        max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
   
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if request:
            self.fields['client'].queryset = Client.objects.filter(agent_id=request.user.id)
        if self.instance.client_id:
            self.fields['client'].queryset = Client.objects.filter(agent_id=request.user.id)
            self.initial['client'] = self.instance.client_id
        

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['agent'] = self.instance.agent
        return cleaned_data
    
    class Meta:
        model = Order
        fields = "__all__"
        exclude = ("status", )
        labels = {
            "discount": "Скидка %",
            'qqs': 'НДС'
            
        }
        widgets = {
            "discount": forms.NumberInput(attrs={"class": "form-control", 'placeholder': 'discount %'}),
            'qqs': forms.CheckboxInput(attrs={"class": "form-check-input"})
        }
        
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = "__all__"
        labels = {
            "name": "Имя",
            
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", 'placeholder': 'Имя'})
        }