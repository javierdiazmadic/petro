# 🚀 GitHub Setup - Cómo Subir a GitHub

## Paso 1: Crear Repositorio en GitHub

1. Abre https://github.com/new
2. Rellena:
   - **Repository name**: `petro`
   - **Description**: `AI system for fuel price prediction in Spain (XGBoost, LightGBM, RandomForest)`
   - **Public** o **Private** (tu elección)
   - ✅ Add README.md (opcional, ya existe)
   - ✅ Add .gitignore (ya existe)

3. Click **Create repository**

## Paso 2: Conectar Repositorio Local a GitHub

```bash
cd /home/administrador/Desktop/petro

# Cambiar la rama a 'main' (opcional)
git branch -M main

# Agregar remote
git remote add origin https://github.com/TU_USUARIO/petro.git

# Subir código
git push -u origin main
```

**Nota**: Reemplaza `TU_USUARIO` con tu usuario de GitHub.

## Paso 3: Generar Token de Acceso (si es repositorio privado)

Si obtienes error `403` o de autenticación:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **Generate new token (classic)**
3. Nombre: `petro-cli`
4. Permisos: ☑️ repo (full control)
5. Click **Generate token**
6. Copia el token

Luego usa:
```bash
git remote remove origin
git remote add origin https://TU_TOKEN@github.com/TU_USUARIO/petro.git
git push -u origin main
```

## Paso 4: Proteger la Rama Main (Recomendado)

1. GitHub → petro → Settings → Branches
2. **Add rule**
3. Pattern: `main`
4. ☑️ Require a pull request before merging
5. ☑️ Require status checks to pass
6. Save

## Paso 5: Configurar GitHub Actions (CI/CD Opcional)

Crear archivo `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: make test
```

## ✅ Verificar que Subió Correctamente

```bash
# Ver remote
git remote -v

# Ver commits en GitHub
git log --oneline | head -5

# Abrir en navegador
open https://github.com/TU_USUARIO/petro
```

## 📝 Archivo README en GitHub

El README.md ya tiene:
- ✅ Descripción del proyecto
- ✅ Tabla de fases
- ✅ Stack tecnológico
- ✅ Instrucciones de setup
- ✅ Cómo contribuir

---

## 🔐 Secretos (si necesitas CI/CD)

GitHub → Settings → Secrets and variables → Actions

Agregar (opcional):

```
GCP_PROJECT_ID=tu-proyecto-gcp
GCP_SA_KEY=<contenido de tu service account JSON>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

---

## 📊 Próximos Pasos

Después de subir a GitHub:

1. **Compartir con equipo**:
   - Settings → Collaborators → Add people

2. **Configurar discussions** (para comunidad):
   - Settings → Discussions (enable)

3. **Crear releases**:
   - Releases → Create a new release → v1.0.0

4. **Agregar badges** a README:
   ```markdown
   ![Python](https://img.shields.io/badge/python-3.12+-blue)
   ![License](https://img.shields.io/badge/license-MIT-green)
   ![Status](https://img.shields.io/badge/status-Active-brightgreen)
   ```

---

## 🎯 Comandos Útiles Después

```bash
# Ver cambios sin subir
git status

# Subir cambios (después de hacer commits)
git push

# Bajar cambios de GitHub
git pull

# Crear rama nueva
git checkout -b feature/nueva-funcionalidad

# Push de rama
git push -u origin feature/nueva-funcionalidad

# Ver todas las ramas
git branch -a
```

---

## ✅ Checklist

- [ ] Repositorio creado en GitHub
- [ ] Remote agregado localmente
- [ ] Código subido (`git push`)
- [ ] README visible en GitHub
- [ ] Branch protection configurada (opcional)
- [ ] GitHub Actions setup (opcional)
- [ ] Secrets agregados si necesita CI/CD (opcional)

---

**¡Tu proyecto PETRO ya está en GitHub y disponible para el mundo!**

Comparte el link: `https://github.com/TU_USUARIO/petro`
