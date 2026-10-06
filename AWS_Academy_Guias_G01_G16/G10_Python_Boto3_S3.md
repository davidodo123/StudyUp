# G10 · Python, Boto3 y S3 desde Ubuntu

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 60–75 minutos  
**Requisitos:** G09 con descarga S3 funcional; G06 recomendable para editar.  
**Recursos:** EC2, entorno virtual Python y el bucket existente.  
**Resultado:** Programa que descarga el CSV y comprueba sus registros sin mostrar credenciales.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivo

```text
Python en Ubuntu → Boto3 → rol de instancia → S3 → CSV local
```

Usarás Boto3, el SDK de AWS para Python. No introducirás credenciales en el programa: Boto3 puede obtenerlas del perfil de la instancia. [AWS: credenciales de Boto3](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html).

## 2. Crea un entorno virtual

En **Ubuntu EC2**:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip
cd ~/practicas-aws
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install boto3
python -c "import sys; print(sys.executable)"
```

Los paquetes del sistema aportan Python y `venv`; el entorno `.venv` separa dependencias del sistema. `source` lo activa; `python -m pip` instala en el intérprete activo. La última salida debe terminar en `/practicas-aws/.venv/bin/python`. No uses `sudo pip` ni `--break-system-packages`. [Python: entornos virtuales](https://docs.python.org/3/library/venv.html).

Si `.venv` ya existe, reutilízalo activándolo, sin recrearlo. El docente debe fijar las versiones ensayadas antes de impartir la guía; la instalación no presupone que todos los días haya la misma versión.

## 3. Carga configuración y crea el programa

```bash
source ~/practicas-aws/lab.env
mkdir -p ~/practicas-aws/scripts ~/practicas-aws/datos/raw
```

En VS Code **remoto**, crea `/home/ubuntu/practicas-aws/scripts/descargar_s3.py`. Si trabajas solo por SSH, usa `nano` con esa ruta; guarda con Ctrl+O, Intro y sal con Ctrl+X. Pega este código **en el archivo**, no línea a línea en la terminal:

```python
import csv
import os
from pathlib import Path
import boto3
from botocore.exceptions import BotoCoreError, ClientError

base = Path.home() / "practicas-aws"
destino = base / "datos/raw/metricas_raw.csv"
destino.parent.mkdir(parents=True, exist_ok=True)
region = os.environ.get("AWS_REGION")
bucket = os.environ.get("BUCKET")
if not region or not bucket or bucket == "NOMBRE_REAL_DEL_BUCKET":
    raise SystemExit("Carga lab.env y revisa la región y el bucket.")

try:
    sesion = boto3.Session(region_name=region)
    identidad = sesion.client("sts").get_caller_identity()
    print("Sesión de rol:", ":assumed-role/" in identidad["Arn"])
    sesion.client("s3").download_file(
        bucket, "raw/metricas/metricas_raw.csv", str(destino)
    )
except ClientError as error:
    raise SystemExit("Operación AWS fallida: " + error.response["Error"]["Code"])
except BotoCoreError as error:
    raise SystemExit("Revisa conexión y perfil IAM: " + type(error).__name__)

with destino.open(encoding="utf-8-sig", newline="") as archivo:
    filas = list(csv.DictReader(archivo))
print("Descarga completada:", destino.name)
print("Registros:", len(filas))
print("Columnas:", ", ".join(filas[0].keys()) if filas else "archivo vacío")
```

| Parte | Qué hace |
|---|---|
| `os.environ` | Lee configuración de esta terminal |
| `boto3.Session` | Crea una sesión de SDK con región; no contiene claves manuales |
| `get_caller_identity` | Comprueba identidad; se imprime solo un booleano |
| `download_file` | Descarga una clave de S3 a una ruta local |
| Excepciones | Muestran código o tipo de error, sin volcar respuesta completa |
| `csv.DictReader` | Lee cada registro con nombres de columnas |
| `utf-8-sig` | Admite CSV UTF-8 con o sin marca BOM de Windows |

[AWS: descarga de archivos con Boto3](https://docs.aws.amazon.com/boto3/latest/guide/s3-example-download-file.html).

## 4. Ejecuta y comprueba

```bash
cd ~/practicas-aws
source .venv/bin/activate
source lab.env
python scripts/descargar_s3.py
```

**Resultado esperado:** sesión de rol `True`, descarga completada, **15 registros** y seis columnas: `id`, `fecha`, `centro`, `servicio`, `peticiones`, `latencia_ms`.

> **Qué está ocurriendo**  
> El programa valida transporte y estructura, pero todavía no limpia los datos. Una descarga correcta no convierte los 15 registros en datos válidos.

## 5. Si algo falla

| Error | Qué revisar |
|---|---|
| `ModuleNotFoundError: boto3` | Entorno `.venv` activo y paquete instalado en ese Python |
| Falta configuración | Ejecuta `source lab.env` en la misma terminal que lanza Python |
| `NoCredentialsError` | Perfil IAM de EC2 y comprobaciones de G09 |
| `AccessDenied` | Permisos del rol sobre ese bucket/objeto; no cambies acceso público |
| `404` o `NoSuchKey` | Nombre exacto del bucket y clave de G08 |
| Registros distintos de 15 | Revisa el CSV utilizado antes de continuar con resultados esperados |

## 6. Entrega, cierre y resumen

Entrega el programa y una salida resumida, sin claves ni ARN. Conserva el CSV y el entorno para G11. Cierra la sesión remota, detén EC2 si terminas y pulsa End Lab.

**Resumen:** has programado el acceso autenticado al Data Lake. **Reto:** explica qué cambiarías para descargar otro objeto manteniendo la misma identidad y región.

