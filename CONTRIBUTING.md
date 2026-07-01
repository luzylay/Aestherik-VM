# Guía para Contribuyentes

¡Gracias por tu interés en contribuir a **Aestherik-VM**! Para mantener la calidad y consistencia del código, por favor lee las siguientes pautas antes de iniciar cualquier colaboración.

## 1. Código de Conducta
Al participar en este proyecto, te comprometes a seguir y respetar nuestro [Código de Conducta](CODE_OF_CONDUCT.md).

## 2. Cómo Contribuir

### Reportar Errores (Bugs)
Si encuentras un error o comportamiento inesperado:
1. Revisa las [Issues del repositorio](https://github.com/luzylay/Aestherik-VM/issues) para asegurarte de que no haya sido reportado previamente.
2. Crea un nuevo Issue describiendo:
   - El comportamiento actual vs. el comportamiento esperado.
   - Pasos detallados para reproducir el error.
   - Entorno de ejecución (versión de Docker, SO de la VM, etc.).

### Proponer Mejoras o Nuevas Características
1. Crea un Issue describiendo el valor que aportará la nueva característica.
2. Una vez discutido y aprobado por los mantenedores, puedes comenzar la implementación.

## 3. Flujo de Trabajo para Pull Requests (PR)

1. **Haz un Fork** del repositorio si no eres colaborador directo.
2. **Crea una Rama de Rama (Branch)** con un nombre descriptivo:
   - `feature/nueva-funcionalidad`
   - `bugfix/correccion-error`
   - `docs/mejora-documentacion`
3. **Desarrolla localmente**:
   - Asegúrate de seguir las buenas prácticas de Python (PEP 8).
   - Documenta los cambios importantes en el código.
4. **Verificación local**:
   - Revisa que no haya errores de sintaxis (`python -m py_compile ...`).
   - Verifica que los contenedores docker compilen y corran sin errores.
5. **Realiza tus Commits** utilizando mensajes claros y en español, por ejemplo:
   - `git commit -m "feat: agregar validación de logs en el worker"`
6. **Envía el Pull Request** apuntando a la rama `main`. Describe claramente tus cambios usando la plantilla de Pull Request provista.

## 4. Estándar de Código
- **Python**: Usar PEP 8 como guía de estilo.
- **HTML/CSS**: Mantener el diseño responsivo, semántico, con estilos en un solo archivo o clases reutilizables.
- **Seguridad**: Nunca expongas credenciales en commits. Utiliza siempre variables de entorno y el archivo `.env`.
