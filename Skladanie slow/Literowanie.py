import sys
import os
import time
import pygame
import random

from gtts import gTTS

# ----------------- Parametry wejściowe -----------------
if len(sys.argv) != 4:
    print("Użycie: python program.py <dlugosc_slowa> <jezyk_slowo> <plik_tekstowy>")
    sys.exit(1)

try:
    dlugosc_slowa = int(sys.argv[1])
    jezyk_slowo = sys.argv[2]
    nazwa_pliku = sys.argv[3]
except Exception as e:
    print(f"Błąd w parametrach: {e}")
    sys.exit(1)

# ----------------- Inicjalizacja -----------------
pygame.init()
pygame.mixer.init()

folder = "temp_litery"
os.makedirs(folder, exist_ok=True)

# ----------------- Wczytywanie słów -----------------
slowa = []
try:
    with open(nazwa_pliku, "r", encoding="utf-8") as plik:
        for linia in plik:
            for slowo in linia.split():
                slowo_czyste = slowo.strip(".,;!?()[]{}\"'").lower()
                if slowo_czyste.isalpha() and len(slowo_czyste) == dlugosc_slowa:
                    slowa.append(slowo_czyste)
except FileNotFoundError:
    print(f"Nie znaleziono pliku: {nazwa_pliku}")
    sys.exit(1)

# ----------------- Czytanie słów -----------------
#print(f"\nZnalezione słowa {dlugosc_slowa}-literowe:")
#print(slowa)

slowar = random.sample(slowa, len(slowa))
for index, slowo in enumerate(slowar):
    time.sleep(0.5)
#    print(f"\nCzytam słowo: {slowo}")

# Iteracja po literach w słowie
    for i, litera in enumerate(slowo):
        if litera.isalpha():  # Pomijamy znaki inne niż litery
            plik_wav = os.path.join(folder, f"{litera}.wav")
            if os.path.exists(plik_wav):
                pygame.mixer.music.load(plik_wav)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.2)
            else:
                print(f"Brak pliku dla litery: {litera}")


            time.sleep(0.05)

    # Całe słowo
    tts = gTTS(text=slowo, lang=jezyk_slowo)
    plik_mp3 = os.path.join(folder, f"{index}_slowo.mp3")
    tts.save(plik_mp3)
    pygame.mixer.music.load(plik_mp3)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)

# ----------------- Sprzątanie -----------------
pygame.mixer.music.stop()
time.sleep(0.2)

for plik in os.listdir(folder):
    os.remove(os.path.join(folder, plik))
os.rmdir(folder)
pygame.quit()
