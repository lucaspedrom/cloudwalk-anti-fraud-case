"""
🚀 CloudWalk Technical Assessment — Quick Launcher
"""

import os
import sys
import subprocess

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)
    sys.path.insert(0, os.path.join(root_dir, "src"))

    print("\n" + "="*80)
    print("🛡️ CLOUDWALK ANTI-FRAUD INTELLIGENCE — INICIALIZADOR AUTOMÁTICO")
    print("="*80)

    # 1. Alimentação / Validação do Banco de Dados
    print("\n[1/2] Verificando integridade da base de dados e ingestão de transações...")
    try:
        from ingest_data import run_ingestion
        run_ingestion(verbose=True)
    except Exception as e:
        print(f"⚠️ Erro ao verificar dados: {e}")
        print("Tentando prosseguir com o dashboard...")

    # 2. Inicialização do Dashboard Streamlit
    print("\n[2/2] Iniciando o Dashboard Streamlit...")
    dashboard_path = os.path.join("src", "dashboard.py")
    
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
    print(f"Executando comando: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro ao executar o Streamlit: {e}")
        print("\nAlternativa manual:")
        print("  streamlit run src/dashboard.py")
        print("ou com uv:")
        print("  uv run streamlit run src/dashboard.py")

if __name__ == "__main__":
    main()
