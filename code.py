"""
Treino de leitura em voz alta: Português, English, Français.

Instalação:
    pip install SpeechRecognition pyaudio

Uso:
    python leitura.py              # escolhe o idioma e usa o texto de exemplo
    python leitura.py meutexto.txt # escolhe o idioma e usa o seu arquivo
"""
import re
import sys
import difflib
import speech_recognition as sr

IDIOMAS = {
    "1": ("Português", "pt-BR",
          "O sol nasceu cedo naquela manhã. As crianças correram para o jardim. "
          "Havia flores de todas as cores."),
    "2": ("English", "en-US",
          "The sun rose early that morning. The children ran into the garden. "
          "There were flowers of every color."),
    "3": ("Français", "fr-FR",
          "Le soleil s'est levé tôt ce matin-là. Les enfants ont couru dans le jardin. "
          "Il y avait des fleurs de toutes les couleurs."),
}


def escolher_idioma():
    print("Escolha o idioma:")
    for k, (nome, _, _) in IDIOMAS.items():
        print(f"  {k} - {nome}")
    while True:
        op = input("Opção: ").strip()
        if op in IDIOMAS:
            return IDIOMAS[op]


def dividir_frases(texto):
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [f.strip() for f in frases if f.strip()]


def palavras(frase):
    # trata apóstrofos (l'enfant, don't) como parte da palavra
    return re.findall(r"\w+(?:['’]\w+)*", frase.lower())


def comparar(esperado, falado):
    a, b = palavras(esperado), palavras(falado)
    problemas = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if op == "replace":
            problemas.append(f"❌ Disse '{' '.join(b[j1:j2])}' em vez de '{' '.join(a[i1:i2])}'")
        elif op == "delete":
            problemas.append(f"⚠️  Esqueceu: '{' '.join(a[i1:i2])}'")
        elif op == "insert":
            problemas.append(f"➕ Palavra a mais: '{' '.join(b[j1:j2])}'")
    return problemas


def ouvir(rec, mic, codigo):
    with mic as fonte:
        print("🎤 Pode ler...")
        audio = rec.listen(fonte, phrase_time_limit=20)
    try:
        return rec.recognize_google(audio, language=codigo)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Erro no serviço de voz (precisa de internet): {e}")
        return ""


def main():
    nome, codigo, texto = escolher_idioma()
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            texto = f.read()
    print(f"\nIdioma: {nome}")

    rec = sr.Recognizer()
    mic = sr.Microphone()
    with mic as fonte:
        rec.adjust_for_ambient_noise(fonte, duration=1)

    frases = dividir_frases(texto)
    acertos = 0

    for n, frase in enumerate(frases, 1):
        while True:
            print(f"\n[{n}/{len(frases)}] {frase}")
            cmd = input("Enter = ler | p = pular | s = sair: ").strip().lower()
            if cmd == "s":
                print(f"\nAcertou de primeira: {acertos}/{n - 1}")
                return
            if cmd == "p":
                break

            falado = ouvir(rec, mic, codigo)
            if not falado:
                print("Não entendi. Tente de novo.")
                continue

            print(f"Ouvi: {falado}")
            problemas = comparar(frase, falado)
            if not problemas:
                print("✅ Perfeito!")
                acertos += 1
                break
            for p in problemas:
                print(p)
            print("Vamos tentar de novo.")

    print(f"\nFim! Frases certas: {acertos}/{len(frases)}")


if __name__ == "__main__":
    main()