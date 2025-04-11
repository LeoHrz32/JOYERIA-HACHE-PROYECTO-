import qrcode

info_producto = """Nombre: Zapatos deportivos
Código: ZD123
Precio: $120.000
Stock: 25 unidades"""

qr = qrcode.make(info_producto)
qr.save("producto_qr.png")
