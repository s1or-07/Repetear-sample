
Una herramienta ligera inspirada en Burp Suite Repeater, desarrollada en Python con PyQt5. Permite construir, modificar y enviar solicitudes HTTP manualmente, y visualizar sus respuestas en distintos formatos.

## 📦 Requisitos

- Python 3.8+
- PyQt5
- requests

Instalación de dependencias:

```shell
pip install -r requirements.txt
```

## 🚀 Ejecución

```shell
python repetear.py
```

## 🖥️ Funcionalidades principales

✅ Envío de solicitudes **GET** y **POST**
✅ Análisis visual dividido en pestañas:

- **Pretty**: Cuerpo legible
- **Raw**: Encabezados + cuerpo sin formato
- **Hex**: Representación hexadecimal
- **Render**: Intento de visualización HTML (si aplica)

✅ Interfaz oscura moderna con diseño similar a Burp Suite
✅ Autodetección del protocolo (`http` / `https`) en función del encabezado `Host`
✅ Manejo de errores uniforme

## ✏️ ¿Cómo usarlo?

1. Escribe la solicitud completa en la pestaña **Request → Pretty**, incluyendo:

```
POST /path HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

param1=value1&param2=value2
```

2. Presiona **Send**.
3. Visualiza la respuesta en las pestañas de la derecha.
## 🔐 Consideraciones de seguridad

- Las validaciones de certificados están desactivadas (`verify=False` en `requests`) para facilitar auditorías.
- Requiere incluir explícitamente el encabezado `Host:` en la solicitud.
- No ejecuta JavaScript ni permite interacción activa con HTML renderizado (solo visual).
