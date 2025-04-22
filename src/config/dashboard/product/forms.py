from typing import Any
from django import forms
from config.products.models import Type, Categories, Products, ProductionProduct, Currency, ProductionProductInfo
from django.forms import formset_factory

from django import forms



class ProductionProductForm(forms.Form):
    amount = forms.IntegerField(label='Кол-во (кг)', required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'style': '50%'}))
    amount_m = forms.IntegerField(label='Кол-во (м²)', required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'style': '50%'}))
    stock_product = forms.ModelChoiceField(queryset=Products.objects.all(), label='Продукт со склада', required=False)
    used_amount = forms.IntegerField(label='Использованно', required=False)
    defect_amount = forms.IntegerField(label='Кол-во брак', required=False)
    
    


class CurrencyForm(forms.ModelForm):
    amount = forms.IntegerField(label='Курс доллара (so\'m)', required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width:25%'}))

    class Meta:
        model = Currency
        fields = '__all__'
        exclude = ('name', )


class TypeForm(forms.ModelForm):

    def save(self, commit=True):
        type_one = super().save(commit=False)
        if commit:
            type_one.save()
        return type_one

    class Meta:
        model = Type
        fields = "__all__"
        labels = {
            "name": "Название типа",
            "description": "Описание типа",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Пример: kg"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Пример: Единица измерения в килограммах"})
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = "__all__"
        exclude = ("image", 'parent')
        labels = {
            "name": "Название категории",
            "image": "Изображение",
            "type": "Вид категории"
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-control"})
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = "__all__"
        exclude = ("images", "type")
        labels = {
            "name": "Название продукта",
            "image": "Image",
            "category": "Категория продукта",
            "price": "Цена ($)",
            "amount": "Кол-во",
            "defect": "Кол-во брака (kg)"
        }

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "$",
                "style": "border: 1px solid #ccc; background-color: #f9f9f9; color: #333;width:15%;"
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "style": "border: 1px solid #ccc; background-color: #f9f9f9; color: #333;width:30%;"
            }),
            "defect": forms.NumberInput(attrs={
                "class": "form-control",
                "style": "border: 1px solid #ccc; background-color: #f9f9f9; color: #333;width:30%;"
            }),
            "category": forms.Select(attrs={"class": "form-control"})
        }


class ProductInfoForm(forms.ModelForm):
    class Meta:
        model = ProductionProductInfo
        fields = "__all__"
        exclude = ("images", "price", 'currency')
        labels = {
            "name": "Название продукта",
            "image": "Изображение",
            "category": "Категория продукта",
            'norm': "Норма (м²)"
        }

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            'norm': forms.NumberInput(attrs={"class": "form-control"})
        }
        
class ProductProdactionCreateForm(forms.ModelForm):
    class Meta:
        model = ProductionProduct
        fields = ('production_product', 'amount')
        labels = {
            "production_product": "Выберите продукт",
            "amount": "Кол-во",
        }

        widgets = {
            "production_product": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"})
        }
    
    def clean(self) -> dict[str, Any]:
        clean_data = self.cleaned_data
        clean_data['status'] = 2
        return clean_data
    
    def save(self, commit=True, *args, **kwargs):
        model = super().save(commit=False)
        model.status = self.cleaned_data['status']
        if commit:
            model.save()
        return model
