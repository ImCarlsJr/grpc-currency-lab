import time
from concurrent import futures
import grpc
import currency_pb2
import currency_pb2_grpc
import requests 

# Tasas simuladas (Incluye JPY para el desafío y es el fallback)
SIMULATED_RATES = {
    "USD": {"EUR": 0.92, "GBP": 0.78, "JPY": 145.00, "USD": 1.0}, 
    "EUR": {"USD": 1.087, "GBP": 0.85, "JPY": 158.00, "EUR": 1.0},
    "GBP": {"USD": 1.28, "EUR": 1.17, "JPY": 185.00, "GBP": 1.0},
    "JPY": {"USD": 0.0069, "EUR": 0.0063, "GBP": 0.0054, "JPY": 1.0},
}

SUPPORTED = [
    ("USD", "United States Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("JPY", "Japanese Yen"),
]

class CurrencyConverterServicer(currency_pb2_grpc.CurrencyConverterServicer):
    
    def _get_real_rate(self, from_c, to_c):
        """Intenta obtener la tasa real desde Frankfurter API (Extensión)"""
        try:
            url = f"https://api.frankfurter.app/latest?from={from_c}&to={to_c}"
            response = requests.get(url, timeout=3)
            response.raise_for_status() 
            
            data = response.json()
            if to_c in data.get('rates', {}):
                return data['rates'][to_c]
        
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con Frankfurter API: {e}")
        except Exception as e:
            print(f"Error consultando API externa: {e}")
        return None

    def _lookup_rate(self, from_c, to_c):
        """Lógica común para buscar la tasa (Simulada o Real)"""
        rate = None
        # 1. Búsqueda local/simulada
        if from_c in SIMULATED_RATES and to_c in SIMULATED_RATES[from_c]:
            rate = SIMULATED_RATES[from_c][to_c]
            print(f"Usando tasa simulada: {from_c}->{to_c}")
        elif to_c in SIMULATED_RATES and from_c in SIMULATED_RATES[to_c]:
            rate = 1.0 / SIMULATED_RATES[to_c][from_c]
            print(f"Usando tasa simulada (invertida): {from_c}->{to_c}")
        
        # 2. Búsqueda en API Real (si no está localmente)
        if rate is None:
            print(f"Consultando API real para: {from_c}->{to_c}...")
            rate = self._get_real_rate(from_c, to_c)
        
        return rate


    def Convert(self, request, context):
        from_c = request.from_currency.upper()
        to_c = request.to_currency.upper()
        amt = request.amount
        
        rate = self._lookup_rate(from_c, to_c)

        if rate is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Rate not found for {from_c} -> {to_c}")
            return currency_pb2.ConvertReply()

        converted = amt * rate
        return currency_pb2.ConvertReply(
            converted_amount=converted,
            rate=rate,
            from_currency=from_c,
            to_currency=to_c
        )

    # NUEVO MÉTODO RPC: GetRate (Solo devuelve la tasa, no la conversión)
    def GetRate(self, request, context): 
        from_c = request.from_currency.upper()
        to_c = request.to_currency.upper()
        
        rate = self._lookup_rate(from_c, to_c)

        if rate is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Rate not found for {from_c} -> {to_c}")
            return currency_pb2.RateReply()

        return currency_pb2.RateReply(rate=rate)


    def GetSupportedCurrencies(self, request, context):
        for code, name in SUPPORTED:
            yield currency_pb2.Currency(code=code, name=name)

    def StreamRates(self, request, context):
        try:
            while True:
                for from_c, targets in SIMULATED_RATES.items():
                    for to_c, rate in targets.items():
                        if from_c == to_c: continue
                        
                        yield currency_pb2.ConvertReply(
                            converted_amount=rate, 
                            rate=rate,
                            from_currency=from_c,
                            to_currency=to_c
                        )
                        time.sleep(0.5) 
        except Exception:
            pass 

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    currency_pb2_grpc.add_CurrencyConverterServicer_to_server(CurrencyConverterServicer(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    server.start()
    print(f"gRPC CurrencyConverter server started on {listen_addr}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server stopping")

if __name__ == "__main__":
    serve()