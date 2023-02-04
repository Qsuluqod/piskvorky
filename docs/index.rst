.. Piškvorky documentation master file, created by
   sphinx-quickstart on Sat Feb  4 01:16:56 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dokumentace projektu Piškovrky
=========

Program vznikl jako zápočtový program pro předmět programování 1 na MatFyzu.

Uživatelský návod
======================================================
Po spuštění skriptu main.py se v konzoli program zeptá, jaký chce uživatel hrát herní režim. Jednotlivé herní
režimy jsou očíslovány. Po zadání příslušného čísla se spustí daný herní režim. Herní režimy jsou pojmenovány
přímočaře a je jasné, co jaký herní režim znamená, proto zde nejsou více popsány. Pokud uživatel je dále v programu
vyzván k tomu, aby zadával souřadnice, musí je zadat způsobem jaký:

a) bude obsahovat číslo a písmeno v jakékomkoliv pořadí

b) může obsahovat mezeru, čárku nebo nějaké další nečíselné a nepísmené znaky jako oddělovací znaky

V případě zadání špatného vstupu, program vyzve uživatele k opětovnému zadání vstupu.

Na konci hry, se program zeptá znovu uživatele na to, jaký chce hrát herní režim a celý program se opakuje.

Schéma programu
==================
Hlavní řídící struktura je třída Game, jejíž jediná instance se vytváří v třídě UI. Třída Game má svoji instanci
třídi Board, kde je reprezentováno pole a svoji instanci třídy MiniMax. Třída Game pak sama bere vstup od hráče,
pokud táhne hráč nebo volá MiniMax, pokud chce získat tahy počítače. Třída MiniMax si pak v každém svém volání předává
instanci třídy Board, jako informaci o stavu hry v daném uzlu minimaxového stromu. Třídá Game pak řídí běh hry,
kontroluje, jestli někdo nevyhrál a popřípadě ukončí hru.

Jednotlivé struktury programu
==================
.. toctree::
   :maxdepth: 2

   modules

Indexy a tabulky
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
