import sys
import os
import time
import pygame
import random
import keyboard
import threading
from io import BytesIO
from typing import List, Set
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

folder = "gloski"


#__________________ Pomocnicze --------------------------
odstep = 0.2
koniec = False


def klawisz(zdarzenie):
    global odstep
    global koniec
    inkrementacja = 0.05
    if zdarzenie.name == '+':
        if odstep + inkrementacja <= 4.0:
            odstep = odstep + inkrementacja
            print("Odstep: {:.1f}".format(odstep))
    if zdarzenie.name == '-':
        if odstep - inkrementacja >= 0:
            odstep = odstep - inkrementacja
            print("Odstep: {:.1f}".format(odstep))
    if zdarzenie.name == "k":
        koniec = True

def kontroler():
    keyboard.on_press(klawisz, suppress=True)


# ----------------- Wczytywanie słów -----------------
def parsuj_linie(linia: str) -> List[str]:
    # Usun biale znaki
    linia = linia.strip()

    # Sprawdz czy format linii sie zgadza
    if not linia.startswith('{') or not linia.endswith('}'):
        return []

    # Usun nawiaski
    zawartosc = linia[1:-1].strip()

    # Wyselekcjonuj slowa (fonetyczne | pisane)
    para = [wyraz.strip() for wyraz in zawartosc.split('|') if wyraz.strip()]

    return para


def czytaj_zestawy_slow_z_pliku(nazwa_pliku: str) -> List[List[str]]:
    pary_slow = []

    try:
        with open(nazwa_pliku, 'r', encoding='utf-8') as plik:
            for nr_linii, linia in enumerate(plik, 1):
                lista_slow = parsuj_linie(linia)
                if len(lista_slow) == 2:  # Only add if exactly 2 words
                    pary_slow.append(lista_slow)
                elif lista_slow and len(lista_slow) != 2:  # Warn if wrong number of words
                    print(f"Uwaga: Linia {nr_linii} ma {len(lista_slow)} slowa, spodziewane 2: {linia.strip()}")
                elif linia.strip():  # Warn about non-empty lines that couldn't be parsed
                    print(f"Uwaga: Linia {nr_linii} nie mogla byc sparsowana: {linia.strip()}")

    except FileNotFoundError:
        print(f"Blad: Plik '{nazwa_pliku}' nie znaleziony.")
        return []
    except Exception as e:
        print(f"Blad odczytu pliku '{nazwa_pliku}': {e}")
        return []

    return pary_slow


def przechowaj_w_pliku(tts, uchwyt):
    uchwyt.seek(0)
    tts.write_to_fp(uchwyt)
    uchwyt.seek(0)


wszystkie_slowa = czytaj_zestawy_slow_z_pliku(nazwa_pliku)

slowa = []
for zestaw in wszystkie_slowa:
    if dlugosc_slowa == len(zestaw[0]):
        slowa.append(zestaw)


# ----------------- Czytanie słów -----------------
#print(f"\nZnalezione słowa {dlugosc_slowa}-literowe:")
#print(slowa)

slowar = random.sample(slowa, len(slowa))

# Wystartuj drugi watek kontrolujacy klawisze
drugi_watek = threading.Thread(target=kontroler)
drugi_watek.start()

for index, slowo in enumerate(slowar):
    if koniec:
        break
    time.sleep(0.5)
#    print(f"\nCzytam słowo: {slowo}")

# Iteracja po literach w słowie
    for i, litera in enumerate(slowo[0]):
        if litera.isalpha():  # Pomijamy znaki inne niż litery
            plik_wav = os.path.join(folder, f"{litera}.wav")
            if os.path.exists(plik_wav):
                pygame.mixer.music.load(plik_wav)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(odstep)
            else:
                print(f"Brak pliku dla litery: {litera}")
            time.sleep(0.05)

    # Całe słowo
    tts = gTTS(text=slowo[1], lang=jezyk_slowo)
    uchwyt_pliku = BytesIO()
    przechowaj_w_pliku(tts, uchwyt_pliku)
    pygame.mixer.music.load(uchwyt_pliku)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)

drugi_watek.join()

# ----------------- Sprzątanie -----------------
pygame.mixer.music.stop()
time.sleep(0.2)
pygame.quit()
