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
print ("\n")
print ("\n")



import shutil

def show_info_side_by_side_dynamic():
    pl_text = """
=============================================
   📖  Program do głoskowania wyrazów
=============================================

Program literuje (głoskuje) wyrazy i następnie
wymawia je w oryginalnym języku.

Prosze wybrac język wyrazów i głoskowania

Działanie programu:
 - Wyrazy są wybierane losowo z dostępnych plików
   (w formacie MorseCode.World).
 - Można ustalić maksymalną długość wyrazu.

Sterowanie:
 - Klawisze  -  oraz  +  → zmiana odstępów
   pomiedzy literami
 - Klawisze S oraz  F → zmiana czasu rozpoznawania
 - Klawisz K → zatrzymanie programu

Autorzy:
 M0RPA oraz SP9TEM
=============================================
"""

    en_text = """
=============================================
   📖  Word Spelling (Phonetics) Program
=============================================

This program spells out words letter by letter
and then pronounces them in the original language.

Select language of words and phonetics

Program operation:
 - Words are randomly selected from available files
   (in MorseCode.World format).
 - Maximum word length can be specified.

Controls:
 - Keys  -  and  +  → decrease or increase spacing
   between letters
 - Key S and  F → decrease or increase recognition time
 - Key K → stop the program

Authors:
 M0RPA and SP9TEM
=============================================
"""

    # Podziel na linie
    pl_lines = pl_text.strip().split("\n")
    en_lines = en_text.strip().split("\n")

    # Sprawdź szerokość terminala
    terminal_width = shutil.get_terminal_size((120, 20)).columns

    # Ustal szerokość kolumny: połowa terminala minus margines
    col_width = terminal_width // 2 - 2

    # Wypisz linie obok siebie
    for i in range(max(len(pl_lines), len(en_lines))):
        pl_line = pl_lines[i] if i < len(pl_lines) else ""
        en_line = en_lines[i] if i < len(en_lines) else ""
        print(f"{pl_line:<{col_width}}  {en_line:<{col_width}}")

# Wywołanie funkcji
show_info_side_by_side_dynamic()

print ("\n")
print ("\n")

    
# Wprowadzanie długości słowa
dlugosc_slowa = int(input("Podaj maksymalna długość słowa /word max length: "))

# Wprowadzanie języka
jezyk_slowo = input("Podaj język słowa/ Language of words (np. en/pl): ")

# Wprowadzenie jezyka glosek
jezyk_glosek = input("Podaj język głoskowania/Phonetics Language (np. en/pl): ")


# Wybór pliku w zależności od języka
if jezyk_slowo == "en":
    nazwa_pliku = "slowa_en.txt"
else:
    nazwa_pliku = "slowa_pl.txt"

# Wybor pliku wav glosek
if jezyk_glosek == "pl":
    nazwa = ""
else:
    nazwa = "_phonic"

#print("Długość słowa:", dlugosc_slowa)
#print("Język słowa:", jezyk_slowo)
#print("Wybrany plik:", nazwa_pliku)



# ----------------- Inicjalizacja -----------------
pygame.init()
pygame.mixer.init()

folder = "gloski"


#__________________ Pomocnicze --------------------------
recogn = 0.2
odstep = 0.2
koniec = False


def klawisz(zdarzenie):
    global recogn
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
    if zdarzenie.name == 'f':
        if recogn + inkrementacja <= 4.0:
            recogn = recogn + inkrementacja
            print("Recognition: {:.1f}".format(recogn))
    if zdarzenie.name == 's':
        if recogn - inkrementacja >= 0:
            recogn = recogn - inkrementacja
            print("Recognition: {:.1f}".format(recogn))
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
    if dlugosc_slowa >= len(zestaw[0]):
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
            #if jezyk_slowo == "en":
            #    plik_wav = os.path.join(folder, f"{litera}_phonic.wav")
            #else:
            #    plik_wav = os.path.join(folder, f"{litera}.wav")
            plik_wav = os.path.join(folder, f"{litera}{nazwa}.wav")
            if os.path.exists(plik_wav):
                pygame.mixer.music.load(plik_wav)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(odstep)
            else:
                print(f"Brak pliku dla litery: {litera}")
            time.sleep(0.05)

    # Całe słowo
    #print(slowo)
    time.sleep(recogn)
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
