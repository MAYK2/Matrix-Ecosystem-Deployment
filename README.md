# Matrix Ecosystem Deployment 🌐🚀

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white)

Este repositorio es el **Orquestador Principal** del Ecosistema Matrix. Permite desplegar de forma unificada todos los microservicios y aplicaciones del sistema utilizando `Docker Compose` y `Git Submodules`.

## 📦 Sistemas Incluidos

Este orquestador levanta automáticamente los siguientes módulos:
1. **Hub Central (SSO)** (`:5050`) - Gestión de identidad y autenticación.
2. **Sistema OEE** (`:5051`) - Monitoreo de Eficiencia General de Equipos.
3. **Gestión de Inventario (ERP)** (`:5052`) - Control de stock, facturación y presupuestos.
4. **Control de Asistencia** (`:5053`) - Biometría facial con DeepFace y OpenCV.
5. **Gestor de Turnos** (`:5054` / `:5055`) - Frontend en Next.js y Backend en FastAPI para citas.
6. **Base de Datos Unificada** (`:3306`) - MySQL 8.0 con inicialización automática para cada módulo.

## 🚀 Cómo Desplegar (Para Evaluadores / Portfolio)

1. **Clonar este repositorio con todos sus submódulos:**
   Es crucial agregar `--recursive` para que descargue el código de los 4 repositorios enlazados.
   ```bash
   git clone --recursive https://github.com/MAYK2/Matrix-Ecosystem-Deployment.git
   cd Matrix-Ecosystem-Deployment
   ```
   *(Si ya lo clonaste sin recursividad, ejecuta: `git submodule update --init --recursive`)*

2. **Copiar las variables de entorno:**
   ```bash
   cp .env.example .env
   ```

3. **Construir y Levantar todo el ecosistema:**
   Dependiendo de la velocidad de conexión y CPU (la instalación de OpenCV/DeepFace toma unos minutos), este comando dejará todo el ecosistema funcionando:
   ```bash
   docker-compose up --build -d
   ```

4. **Verificar el estado de los contenedores:**
   ```bash
   docker-compose ps
   ```

Una vez que los contenedores estén corriendo, podrás acceder a los diferentes sistemas desde `http://localhost:5050` hasta `http://localhost:5055`. Todos estarán interconectados a la misma base de datos y compartirán el inicio de sesión gracias al Hub.

---
**Desarrollado por MAYK2.**
