from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from Administracion.models import Cliente, Cuenta, Transaccion
from .forms import ClienteForm, CuentaForm, TransaccionForm, TransferenciaForm

def registrar_cliente(request):

    form = ClienteForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('registrar_clientes')

    return render(request, 'registro_clientes.html', {'form': form})


def registrar_cuenta(request):

    form = CuentaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('registrar_cuentas')

    return render(request, 'registro_cuentas.html', {'form': form})


def registrar_transaccion(request):

    form = TransaccionForm(request.POST or None)

    if form.is_valid():
        try:
            with transaction.atomic():
                transaccion = form.save(commit=False)
                cuenta = transaccion.cuenta
                
                if transaccion.tipo == 'retiro':
                    if cuenta.saldo < transaccion.monto:
                        messages.error(request, f'Fondos insuficientes. Saldo actual: Q {cuenta.saldo}')
                        return render(request, 'registro_transaccion.html', {'form': form})
                    cuenta.saldo -= transaccion.monto
                elif transaccion.tipo == 'deposito':
                    cuenta.saldo += transaccion.monto
                
                cuenta.save()
                transaccion.save()
                
                messages.success(request, f'Transacción de {transaccion.get_tipo_display()} por Q {transaccion.monto} realizada con éxito.')
                return redirect('registrar_transaccion')
        except Exception as e:
            messages.error(request, f'Error al procesar la transacción: {str(e)}')

    return render(request, 'registro_transaccion.html', {'form': form})


def consulta_clientes(request):
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    return render(request, 'consulta_clientes.html', {'clientes': clientes})


def consulta_cuentas_cliente(request, dpi):
    cliente = Cliente.objects.get(dpi=dpi)
    cuentas = Cuenta.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    return render(request, 'consulta_cuentas_cliente.html', {'cliente': cliente, 'cuentas': cuentas})

from django.utils.dateparse import parse_date

def consulta_transacciones_cuenta(request, numero_cuenta):
    cuenta = Cuenta.objects.get(numero_cuenta=numero_cuenta)
    
    # Obtener todas las transacciones ordenadas cronológicamente inverso (más recientes primero)
    transacciones_todas = list(Transaccion.objects.filter(cuenta=cuenta).order_by('-fecha'))
    
    # El saldo actual de la cuenta es el saldo después de la transacción más reciente
    saldo_iterador = cuenta.saldo
    
    # Calcular el saldo histórico para cada transacción (hacia atrás)
    for t in transacciones_todas:
        t.saldo_historico = saldo_iterador
        # Para saber el saldo ANTES de esta transacción, hacemos la operación inversa
        if t.tipo == 'deposito':
            saldo_iterador -= t.monto
        elif t.tipo == 'retiro':
            saldo_iterador += t.monto
            
    # Aplicar filtros de fecha si existen
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    transacciones_filtradas = transacciones_todas
    
    if fecha_inicio:
        inicio = parse_date(fecha_inicio)
        if inicio:
            transacciones_filtradas = [t for t in transacciones_filtradas if t.fecha.date() >= inicio]
            
    if fecha_fin:
        fin = parse_date(fecha_fin)
        if fin:
            transacciones_filtradas = [t for t in transacciones_filtradas if t.fecha.date() <= fin]
        
    return render(request, 'consulta_transacciones_cuenta.html', {
        'cuenta': cuenta, 
        'transacciones': transacciones_filtradas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })

def registrar_transferencia(request):
    form = TransferenciaForm(request.POST or None)

    if form.is_valid():
        cuenta_origen = form.cleaned_data['cuenta_origen']
        cuenta_destino = form.cleaned_data['cuenta_destino']
        monto = form.cleaned_data['monto']
        descripcion = form.cleaned_data['descripcion'] or f'Transferencia a {cuenta_destino.numero_cuenta}'

        try:
            with transaction.atomic():
                # Actualizar saldos
                cuenta_origen.saldo -= monto
                cuenta_origen.save()
                
                cuenta_destino.saldo += monto
                cuenta_destino.save()

                # Crear transacción de retiro
                Transaccion.objects.create(
                    cuenta=cuenta_origen,
                    tipo='retiro',
                    monto=monto,
                    descripcion=descripcion
                )

                # Crear transacción de depósito
                Transaccion.objects.create(
                    cuenta=cuenta_destino,
                    tipo='deposito',
                    monto=monto,
                    descripcion=f'Transferencia desde {cuenta_origen.numero_cuenta}'
                )

            messages.success(request, f'Transferencia de Q {monto} realizada con éxito.')
            return redirect('registrar_transferencia')
        except Exception as e:
            messages.error(request, f'Error al realizar la transferencia: {str(e)}')

    return render(request, 'registro_transferencia.html', {'form': form})