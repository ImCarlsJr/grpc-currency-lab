Aquí tienes el `README.md` actualizado con todas las implementaciones realizadas, el desafío de protocolo completado, y las respuestas a las preguntas de control.

```markdown
# Laboratorio: Servicio de Conversión de Monedas con gRPC

Este laboratorio guía a los estudiantes en la creación, implementación y uso de un servicio gRPC en Python.

## Resumen del Laboratorio

**Objetivo:** Construir un servicio gRPC que convierta una cantidad entre monedas (p. ej. USD → EUR).

**RPCs Iniciales:**
1.  **Convert** (Unary): Convierte una cantidad con una tasa dada por el servidor.
2.  **GetSupportedCurrencies** (Server-Streaming): El servidor envía la lista de monedas soportadas.
3.  **StreamRates** (Server-Streaming - Opcional): Envía actualizaciones periódicas de tasas simuladas.

---

##  Modificaciones e Implementaciones Realizadas 

He expandido el servicio original para cumplir con todas las actividades sugeridas, logrando un servicio más robusto y conectado al mundo real.

### 1. Extensión de Protocolo 

Se agregó una nueva función RPC al servicio `CurrencyConverter`:

* **Nuevo RPC:** **`GetRate`** (Unary)
    * **Función:** Devuelve solo la tasa de conversión (ej., 1 USD = 0.92 EUR), sin realizar el cálculo de la cantidad.
    * **Mensajes:** Utiliza `RateRequest` (input) y `RateReply` (output).

### 2. Integración de API en Tiempo Real (Extensión)

* **API Utilizada:** Se implementó la conexión a la **Frankfurter API** para obtener tasas de cambio en tiempo real.
* **Lógica en `server.py`:** El método `Convert` (y `GetRate`) primero busca la tasa en el diccionario `SIMULATED_RATES` y, si no la encuentra (p. ej., para `USD -> CAD`), consulta automáticamente la API externa usando la librería `requests`.

### 3. Modificación de Tasas y Funcionalidad

* Se agregó soporte completo para la nueva moneda **Yen Japonés (JPY)**, actualizando las listas de monedas soportadas (`SUPPORTED`) y las tasas simuladas (`SIMULATED_RATES`).

---

## 1. Estructura del Proyecto

```

grpc-currency-lab/
├─ proto/
│  └─ currency.proto
├─ server.py
├─ client.py
├─ requirements.txt
├─ currency\_pb2.py      \<-- Archivo Generado
├─ currency\_pb2\_grpc.py \<-- Archivo Generado
└─ README.md

````

## 2. Definición del Servicio (.proto)

El archivo `proto/currency.proto` define los mensajes y servicios. La versión final incluye la nueva funcionalidad `GetRate`.

## 3. Preparación del Entorno

Se recomienda usar un entorno virtual (Conda o venv).

### Instalación de dependencias

```bash
pip install -r requirements.txt
````

O manualmente:

```bash
pip install grpcio grpcio-tools protobuf requests
```

## 4\. Generación de Stubs (Código Python desde Proto)

Para que Python entienda el archivo `.proto` (incluyendo `GetRate`), es **OBLIGATORIO** recompilar.

```bash
python -m grpc_tools.protoc -I ./proto --python_out=. --grpc_python_out=. proto/currency.proto
```

## 5\. Implementación del Servidor (`server.py`)

El servidor implementa la clase `CurrencyConverterServicer`.

  - Usa un diccionario `SIMULATED_RATES` para las tasas de cambio (incluyendo JPY).
  - **Recurre a Frankfurter API si la tasa no es local.**
  - Escucha en el puerto `50051`.

Para iniciarlo:

```bash
python server.py
```

## 6\. Implementación del Cliente (`client.py`)

El cliente se conecta al servidor y realiza llamadas a los 6 métodos definidos, incluyendo pruebas para `GetRate` y la conexión API Real.

Para ejecutarlo (en otra terminal):

```bash
python client.py
```

-----

## 8\.  Respuestas a las Preguntas de Control

### ¿Qué diferencia hay entre una RPC unary y server-streaming?

  * **RPC Unary** (`Convert`, `GetRate`): Es el modelo más simple. El **cliente envía un único mensaje** al servidor, y el **servidor responde con un único mensaje** al cliente. Este modelo se utiliza para solicitudes/respuestas simples, como una única conversión o la obtención de una sola tasa.
  * **RPC Server-Streaming** (`GetSupportedCurrencies`, `StreamRates`): El **cliente envía un único mensaje** al servidor, pero el **servidor responde con una secuencia (stream) de mensajes**. Este modelo es ideal para enviar grandes listas de datos (como monedas soportadas) o feeds de datos continuos (como actualizaciones de tasas) a lo largo del tiempo.

### ¿Cómo manejarías el caso de una tasa no encontrada en el servidor?

El manejo de errores en gRPC es gestionado por el objeto `context` dentro del método del servidor:

1.  Se verifica si la tasa (`rate`) es `None` después de buscar en las tasas simuladas y en la API real.
2.  Si la tasa no se encuentra, se establece un código de estado de error RPC estándar:
      * `context.set_code(grpc.StatusCode.NOT_FOUND)`
3.  Se proporciona información detallada sobre el error para el cliente:
      * `context.set_details(f"Rate not found for {from_c} -> {to_c}")`
4.  Se devuelve un objeto de respuesta vacío (`currency_pb2.ConvertReply()`) para finalizar la llamada RPC con el código de error.

Esto permite al cliente capturar el error como un `grpc.RpcError` y manejarlo de forma elegante (ej., mostrando un mensaje de error legible en lugar de fallar).

```
```