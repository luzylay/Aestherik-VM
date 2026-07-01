import os
import subprocess
import sys

def main():
    print("=" * 60)
    print(" Generación de Certificados SSL/TLS Autofirmados ")
    print("=" * 60)

    # Definir rutas
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    certs_dir = os.path.join(base_dir, "certs")

    # Crear carpeta certs si no existe
    if not os.path.exists(certs_dir):
        os.makedirs(certs_dir)
        print(f"Carpeta creada: {certs_dir}")

    key_file = os.path.join(certs_dir, "key.pem")
    cert_file = os.path.join(certs_dir, "cert.pem")

    # Si ya existen, preguntar si sobreescribir (o directamente notificar)
    if os.path.exists(key_file) and os.path.exists(cert_file):
        print("Los certificados SSL ya existen en la carpeta 'certs/'.")
        ans = input("¿Deseas sobreescribirlos? (s/n): ").strip().lower()
        if ans != 's':
            print("Operación cancelada. Usando certificados existentes.")
            return

    # Intentar ejecutar openssl
    try:
        print("Ejecutando OpenSSL para generar la llave y el certificado...")
        cmd = [
            "openssl", "req", "-x509", "-nodes", "-days", "365", 
            "-newkey", "rsa:2048", 
            "-keyout", key_file, 
            "-out", cert_file,
            "-subj", "/C=PE/ST=Lima/L=Lima/O=CallCenterInteligente/OU=IT/CN=localhost"
        ]
        
        # Ejecutar comando
        subprocess.run(cmd, check=True)
        
        print("\n[ÉXITO] Certificados generados correctamente:")
        print(f"  - Llave privada: {key_file}")
        print(f"  - Certificado público: {cert_file}")
        print("\nRecuerda que estos certificados son autofirmados para propósitos de prueba/desarrollo.")
        
    except FileNotFoundError:
        print("\n[ERROR] No se pudo encontrar el comando 'openssl' en el PATH del sistema.")
        print("Por favor, instala OpenSSL en tu sistema y vuelve a intentarlo.")
        print("Comando de instalación recomendado:")
        print("  - Ubuntu/Debian: sudo apt-get install openssl")
        print("  - Windows (Git Bash): viene integrado por defecto.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error al ejecutar OpenSSL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
