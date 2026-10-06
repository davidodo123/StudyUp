# G07 · Publicar un servicio de práctica y acceder desde la web

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 45–60 minutos  
**Requisitos:** G05 o G06 funcional; permiso para modificar tu Security Group.  
**Recursos:** EC2 existente; servidor HTTP temporal en puerto 8000.  
**Resultado:** Página de prueba accesible desde el navegador con acceso limitado a tu IP.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivo y arquitectura

```text
Navegador Windows → http://IPv4:8000 → regla TCP/8000 desde Mi IP → Ubuntu → página
```

Usaremos datos ficticios y un servidor temporal. El módulo `http.server` de Python no está recomendado para producción. HTTP no cifra el tráfico; esta página no contendrá credenciales ni datos personales. [Python: http.server](https://docs.python.org/3/library/http.server.html).

## 2. Prepara una carpeta exclusiva

En **Ubuntu EC2**, por SSH o terminal remota de VS Code:

```bash
python3 --version
mkdir -p ~/practicas-aws/web-demo
cd ~/practicas-aws/web-demo
```

La primera orden comprueba Python; las siguientes crean y abren una carpeta exclusiva para contenido web. Si Python falta, instala solo en Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y python3
```

`apt-get update` actualiza el índice; `install` añade el paquete. Si falla la red, revisa salida y conectividad con el docente.

Pega **completo** este bloque en Ubuntu para crear la página:

```bash
cat > index.html <<'HTML'
<!doctype html>
<html lang="es">
<meta charset="utf-8">
<title>Laboratorio FP</title>
<h1>Servicio web en Ubuntu EC2</h1>
<p>G07: conexión desde Windows 11 comprobada.</p>
</html>
HTML
```

`cat >` escribe el archivo; `HTML` delimita su contenido. Nunca sirvas tu carpeta personal completa ni una carpeta que contenga `.pem` o credenciales.

## 3. Arranca y prueba el servidor localmente

```bash
python3 -m http.server 8000 --bind 0.0.0.0 --directory /home/ubuntu/practicas-aws/web-demo
```

`-m` ejecuta el módulo, `8000` es el puerto, `--bind 0.0.0.0` escucha en todas las interfaces IPv4 y `--directory` limita el contenido a la carpeta indicada. La terminal queda ocupada: es lo esperado.

Abre una **segunda terminal Ubuntu** y comprueba:

```bash
curl -I http://127.0.0.1:8000/
ss -ltn | grep ':8000'
```

`curl -I` consulta cabeceras; espera un estado HTTP 200. `ss -ltn` lista puertos TCP en escucha y `grep` filtra 8000. `127.0.0.1` es la propia EC2 cuando lo usas dentro de Ubuntu.

## 4. Permite el acceso desde tu equipo

1. En la consola abre el **Security Group asociado a tu EC2**, no otro de nombre parecido.
2. Edita las reglas de entrada.
3. Conserva SSH y añade **Custom TCP**, puerto **8000**, origen **My IP**, con `/32`.
4. Guarda las reglas.
5. En **PowerShell de Windows**:

```powershell
$ec2Host = 'IP_PUBLICA_REAL'
Test-NetConnection -ComputerName $ec2Host -Port 8000
```

Sustituye el marcador por la IPv4 actual. Busca `TcpTestSucceeded : True`.

## 5. Abre la página desde Windows

En Edge o Chrome escribe `http://IP_PUBLICA_REAL:8000/`, sustituyendo la IP. Debes ver «Servicio web en Ubuntu EC2». Utiliza expresamente **http**, no https; todavía no has configurado TLS.

> **Qué está ocurriendo**  
> El navegador llega por un puerto diferente a SSH. Abrir TCP/22 no abre TCP/8000. En Windows, `localhost` se refiere a Windows; en Ubuntu, a Ubuntu.

> **Si algo falla**  
> Si la prueba local falla, comprueba que el proceso está activo y la ruta existe. Si local funciona y TCP desde Windows falla, revisa IP actual, grupo asociado y origen Mi IP. Si Ubuntu tiene firewall activo, pide al docente revisar sus reglas: no lo desactives. Si el puerto está ocupado, identifica el proceso antes de elegir otro y alinea servidor, regla y URL.

## 6. Retira la exposición temporal y cierra

1. En la terminal del servidor pulsa **Ctrl+C**.
2. Comprueba que ya no aparece el puerto con `ss -ltn`.
3. En tu grupo elimina **solo la regla TCP/8000 de esta práctica**; conserva SSH.
4. Guarda el HTML para futuras consultas.
5. Detén EC2 si termina la sesión y pulsa End Lab.

**Entrega:** página visible, explicación de puerto, dirección de escucha y regla; sin datos sensibles. **Resumen:** has recorrido navegador → red → aplicación. **Reto:** explica por qué un servidor enlazado a `127.0.0.1` no respondería directamente por la IP pública aunque abras el grupo.

