"""Local Daily Scheduler - Ejecuta entrenamiento local y pushea a GitHub."""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
import schedule
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_training():
    """Ejecutar pipeline completo de entrenamiento."""
    logger.info("=" * 80)
    logger.info(f"🤖 INICIANDO ENTRENAMIENTO - {datetime.utcnow().isoformat()}")
    logger.info("=" * 80)
    
    try:
        # Ejecutar daily_training.py
        logger.info("📊 ETAPA 1: Ejecutando entrenamiento...")
        result = subprocess.run(
            [sys.executable, "scripts/daily_training.py"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Error en entrenamiento: {result.stderr}")
            return False
        
        logger.info("✅ Entrenamiento completado")
        
        # Ejecutar export_models.py
        logger.info("💾 ETAPA 2: Exportando modelos...")
        result = subprocess.run(
            [sys.executable, "scripts/export_models.py"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Error en exportación: {result.stderr}")
            return False
        
        logger.info("✅ Modelos exportados")
        
        # Ejecutar generate_report.py
        logger.info("📝 ETAPA 3: Generando reporte...")
        result = subprocess.run(
            [sys.executable, "scripts/generate_report.py"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Error en reporte: {result.stderr}")
            return False
        
        logger.info("✅ Reporte generado")
        
        # Git commit y push
        logger.info("🔄 ETAPA 4: Subiendo a GitHub...")
        repo_path = os.path.dirname(os.path.dirname(__file__))
        
        os.chdir(repo_path)
        
        # Git add
        subprocess.run(["git", "add", "-A"], check=True)
        
        # Git commit
        commit_msg = f"🤖 Auto: Daily training & data update {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            logger.error(f"❌ Error en commit: {result.stderr}")
            return False
        
        # Git push
        result = subprocess.run(
            ["git", "push", "origin", "master"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Error en push: {result.stderr}")
            return False
        
        logger.info("✅ Cambios subidos a GitHub")
        
        logger.info("=" * 80)
        logger.info(f"🏁 ENTRENAMIENTO COMPLETADO - {datetime.utcnow().isoformat()}")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error no previsto: {e}", exc_info=True)
        return False

def schedule_training():
    """Programar entrenamiento diario."""
    logger.info("🤖 Iniciando scheduler local...")
    logger.info("📅 Entrenamiento programado para: 3:00 AM UTC")
    
    # Programar para 3:00 AM UTC
    schedule.every().day.at("03:00").do(run_training)
    
    logger.info("⏰ Scheduler activo. Esperando próximo entrenamiento...")
    
    # Loop continuo
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    except KeyboardInterrupt:
        logger.info("⏹️ Scheduler detenido por el usuario")

if __name__ == "__main__":
    try:
        schedule_training()
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)
        sys.exit(1)
