# Kuppelstopper3.0

## BUGS & TODOS 3.0
- die tabellen laden immer und resizen die Spaltengröße wenn das fenster zu klein ist
- Damenwertung
- Konfig über Setup laden
- Icons
- UI für Auswertungsdisplay
- Testzeiten Auswertung Display Bug
- Excel als Backup

## Features 4.0
- Trainingsmodus ohne großen Display
- Kleiner fix verbauter Display für Zeitenanzeige







# Dateistruktur
/gui/auswertung_view.py             Anzeigefenster GUI, ruft nur Manager-Methoden auf
/gui/custom_table.py                GUI für Custom Table
/gui/main_view.py                   Hauptfenster GUI, ruft nur Manager-Methoden auf
managers/gruppen_manager.py         Logikfunktionen für Gruppe 
managers/durchngang_manager.py      Logikfunktionen für Durchgang  
managers/zeitnehmung_manager.py     Logikfunktionen für Zeitnehmung           
models.py                           Abbildung eines Models
paths.py                            Definiert die Speicherorte der Config- und Sicherungsdatein
main.py                             Start der Anwednung




