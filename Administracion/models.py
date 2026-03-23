from django.db import models

class Cliente(models.Model):

    dpi = models.CharField(max_length=15, primary_key=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Cuenta(models.Model):

    numero_cuenta = models.CharField(max_length=20, unique=True, primary_key=True)
    TIPOS = [
        ('ahorro', 'Ahorro'),
        ('monetaria', 'Monetaria')
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_cuenta = models.CharField(max_length=20, choices=TIPOS)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.numero_cuenta


class Transaccion(models.Model):

    TIPOS = [
        ('deposito', 'Deposito'),
        ('retiro', 'Retiro')
    ]

    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.monto}"
