from django import forms
from Administracion.models import Cliente, Cuenta, Transaccion


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['nombre', 'dpi', 'telefono']


class CuentaForm(forms.ModelForm):

    class Meta:
        model = Cuenta
        fields = ['cliente', 'numero_cuenta', 'tipo_cuenta', 'saldo']


class TransaccionForm(forms.ModelForm):

    class Meta:
        model = Transaccion
        fields = ['cuenta', 'tipo', 'monto', 'descripcion']

class TransferenciaForm(forms.Form):
    cuenta_origen = forms.ModelChoiceField(queryset=Cuenta.objects.all(), label="Cuenta Origen")
    cuenta_destino = forms.ModelChoiceField(queryset=Cuenta.objects.all(), label="Cuenta Destino")
    monto = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label="Monto a Transferir")
    descripcion = forms.CharField(widget=forms.Textarea, required=False, label="Descripción (Opcional)")

    def clean(self):
        cleaned_data = super().clean()
        cuenta_origen = cleaned_data.get('cuenta_origen')
        cuenta_destino = cleaned_data.get('cuenta_destino')
        monto = cleaned_data.get('monto')

        if cuenta_origen and cuenta_destino and cuenta_origen == cuenta_destino:
            raise forms.ValidationError("La cuenta origen y la cuenta destino no pueden ser la misma.")
        
        if cuenta_origen and monto and cuenta_origen.saldo < monto:
            raise forms.ValidationError(f"Fondos insuficientes en la cuenta origen. El saldo actual es Q {cuenta_origen.saldo}.")
        
        return cleaned_data