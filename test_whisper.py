import whisper

try:
    print("Intentando cargar el modelo 'tiny' de Whisper...")
    model = whisper.load_model("tiny", device="cpu")
    print("¡Éxito! El modelo se cargó correctamente.")
    print(f"La función 'load_model' fue encontrada en el módulo: {whisper.__file__}")
except AttributeError:
    print("\n¡ERROR! El atributo 'load_model' no fue encontrado.")
    print("Esto significa que se está importando un módulo 'whisper' incorrecto.")
    import sys
    print("\nPython está buscando módulos en estas rutas (sys.path):")
    for path in sys.path:
        print(path)
except Exception as e:
    print(f"\nOcurrió otro error: {e}")