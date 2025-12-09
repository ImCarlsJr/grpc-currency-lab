import grpc
import currency_pb2
import currency_pb2_grpc
import time

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = currency_pb2_grpc.CurrencyConverterStub(channel)

    # 1) Prueba de Monedas Soportadas (Server Streaming)
    print("=" * 60)
    print("1. 🪙 OBTENER MONEDAS SOPORTADAS")
    try:
        for currency in stub.GetSupportedCurrencies(currency_pb2.Empty()):
            print(f" - [{currency.code}] {currency.name}")
    except grpc.RpcError as e:
        print("Error GetSupportedCurrencies:", e)

    # 2) Conversión con Tasa Simulada (JPY -> EUR)
    print("\n" + "=" * 60)
    print("2. ⚡ PRUEBA LOCAL (JPY -> EUR)")
    req_local = currency_pb2.ConvertRequest(from_currency="JPY", to_currency="EUR", amount=10000.0)
    try:
        reply_local = stub.Convert(req_local)
        print(f"   SOLICITUD: {req_local.amount:.0f} {req_local.from_currency}")
        print(f"   RESPUESTA: {reply_local.converted_amount:.4f} {req_local.to_currency} (Tasa: {reply_local.rate:.6f})")
    except grpc.RpcError as e:
        print(f"   Error: {e.details()}")

    # 3) Conversión con Tasa Real (USD -> CAD - Fuerza consulta a API)
    print("\n" + "=" * 60)
    print("3. 🌐 PRUEBA API REAL (USD -> CAD)")
    req_real = currency_pb2.ConvertRequest(from_currency="USD", to_currency="CAD", amount=100.0)
    try:
        reply_real = stub.Convert(req_real)
        print(f"   SOLICITUD: {req_real.amount} {req_real.from_currency}")
        print(f"   RESPUESTA: {reply_real.converted_amount:.4f} {req_real.to_currency} (Tasa: {reply_real.rate:.4f})")
    except grpc.RpcError as e:
        print(f"   Error: {e.details()}")

    # 4) DESAFÍO: Obtener SOLO Tasa (Nuevo método GetRate - EUR -> JPY)
    print("\n" + "=" * 60)
    print("4. 🔍 DESAFÍO GetRate (EUR -> JPY)")
    req_rate = currency_pb2.RateRequest(from_currency="EUR", to_currency="JPY") 
    try:
        reply_rate = stub.GetRate(req_rate)
        print(f"   SOLICITUD: 1 {req_rate.from_currency} -> {req_rate.to_currency}")
        print(f"   RESPUESTA: Tasa = {reply_rate.rate:.4f}")
    except grpc.RpcError as e:
        print(f"   Error GetRate: {e.details()}")


    # 5) Prueba de Manejo de Errores (Moneda inexistente)
    print("\n" + "=" * 60)
    print("5. ❌ PRUEBA DE ERROR (Moneda inexistente: USD -> XYZ)")
    req_error = currency_pb2.ConvertRequest(from_currency="USD", to_currency="XYZ", amount=1.0)
    try:
        stub.Convert(req_error)
    except grpc.RpcError as e:
        print(f"   ÉXITO: Se capturó el error RPC esperado.")
        print(f"   Detalle: {e.details()}")
        
    # 6) Escuchar StreamRates por 5 elementos
    print("\n" + "=" * 60)
    print("6. 📈 STREAM DE TASAS (5 items)")
    try:
        stream = stub.StreamRates(currency_pb2.Empty())
        for i, item in enumerate(stream):
            print(f"   TICKER #{i+1}: 1 {item.from_currency} = {item.rate:.4f} {item.to_currency}")
            if i >= 4:
                break
    except grpc.RpcError as e:
        print(f"   StreamRates error: {e}")
        
    print("=" * 60)

if __name__ == "__main__":
    run()