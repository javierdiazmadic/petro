# 🚀 Instrucciones para Subir a GitHub

Este documento contiene los pasos exactos para subir el repositorio PETRO a GitHub.

---

## 📋 Requisitos Previos

1. **Cuenta GitHub** creada
2. **Git configurado** en tu máquina
3. **SSH keys** configuradas (recomendado) o **Personal Access Token**

---

## ✅ Paso 1: Configurar Git (Si no lo has hecho)

```bash
# Configurar usuario global
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@example.com"

# Verificar configuración
git config --global --list
```

---

## 📱 Paso 2: Crear Repositorio en GitHub

1. **Ir a:** https://github.com/new
2. **Ingresar detalles:**
   - Nombre: `petro`
   - Descripción: "AI-powered fuel price prediction system for Spain"
   - Visibilidad: **Public**
   - **NO inicializar** con README.md

3. **Crear repositorio**

---

## 🔑 Paso 3: Configurar SSH (Recomendado)

```bash
# Generar SSH key
ssh-keygen -t ed25519 -C "tu.email@example.com"

# Agregar a ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copiar clave pública
cat ~/.ssh/id_ed25519.pub
```

**En GitHub:** Settings → SSH and GPG keys → New SSH Key

---

## 🔗 Paso 4: Conectar Repositorio Local

```bash
cd /home/administrador/Desktop/petro

# Cambiar remoto origin
git remote set-url origin git@github.com:USERNAME/petro.git

# Verificar
git remote -v
```

---

## 📤 Paso 5: Subir al Repositorio

```bash
# Subir todos los commits
git push -u origin master
```

---

## ✨ Paso 6: Verificar en GitHub

Ir a: https://github.com/USERNAME/petro

Verificar:
- ✅ README.md visible
- ✅ SUMMARY.md visible
- ✅ Commits históricos
- ✅ Carpetas y archivos

---

## 🎉 ¡Listo!

Tu repositorio PETRO está en GitHub.
