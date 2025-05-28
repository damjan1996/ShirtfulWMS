# Shirtful WMS - Benutzerhandbuch

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Erste Schritte](#erste-schritte)
3. [Anmeldung](#anmeldung)
4. [Wareneingang](#wareneingang)
5. [Veredelung](#veredelung)
6. [Betuchung](#betuchung)
7. [Qualitätskontrolle](#qualitätskontrolle)
8. [Warenausgang](#warenausgang)
9. [Häufige Probleme](#häufige-probleme)
10. [Tastenkürzel](#tastenkürzel)

## Einführung

Das Shirtful Warehouse Management System (WMS) ist eine benutzerfreundliche Software zur Verwaltung des kompletten Warenflusses in der Textilveredelung. Das System besteht aus 5 Stationen:

- **Wareneingang**: Erfassung eingehender Pakete
- **Veredelung**: Druck und andere Veredelungsprozesse
- **Betuchung**: Stoffbearbeitung
- **Qualitätskontrolle**: Prüfung der Ware
- **Warenausgang**: Versandvorbereitung

## Erste Schritte

### System starten

1. **Desktop-Symbol** doppelklicken:
   - 📥 Wareneingang
   - 🎨 Veredelung
   - 🧵 Betuchung
   - 🔍 Qualitätskontrolle
   - 📦 Warenausgang

2. **Oder Batch-Datei** ausführen:
   - `run_wareneingang.bat`
   - `run_veredelung.bat`
   - etc.

### Bildschirmaufbau

Alle Anwendungen haben einen ähnlichen Aufbau:

```
┌─────────────────────────────────────┐
│ Header (Benutzer/Station)      [X]  │
├─────────────────────────────────────┤
│                                     │
│     Hauptbereich                    │
│     - Aktionsbuttons                │
│     - Statusanzeige                 │
│                                     │
├─────────────────────────────────────┤
│ Statistiken                         │
└─────────────────────────────────────┘
```

## Anmeldung

### RFID-Login

1. **RFID-Karte** an das Lesegerät halten
2. Warten bis der **grüne Haken** erscheint
3. Automatische Weiterleitung zum Hauptmenü

![Login-Bildschirm](images/login_screen.png)

### Sprache wechseln

Unten auf dem Login-Bildschirm:
- 🇩🇪 Deutsch
- 🇬🇧 English
- 🇹🇷 Türkçe
- 🇵🇱 Polski

### Probleme beim Login?

- **Rote X**: Unbekannte Karte → IT kontaktieren
- **Kein Piep**: Reader prüfen → USB-Verbindung
- **Keine Reaktion**: Karte näher halten

## Wareneingang

### Neue Lieferung starten

1. Button **"🚚 Neue Lieferung"** klicken
2. Formular ausfüllen:
   - **Lieferant**: Aus Liste wählen (DHL, UPS, etc.)
   - **Lieferschein-Nr.**: Optional eingeben
   - **Erwartete Pakete**: Anzahl (geschätzt)
   - **Notizen**: Optional
3. **"✓ Lieferung starten"** klicken

### Pakete scannen

1. Button **"📷 Paket scannen"** klicken
2. QR-Code vor die Kamera halten
3. Warten auf Piep-Ton
4. Bei neuem Paket:
   - **Bestellnummer** eingeben
   - **Kunde** eingeben
   - **Artikelanzahl** eingeben
   - **Priorität** wählen
5. **"✓ Registrieren"** klicken

### Manuelle Eingabe

Wenn QR-Code nicht lesbar:
1. **"⌨️ Manuelle Eingabe"** klicken
2. Neuer QR-Code wird generiert
3. Formular wie oben ausfüllen

### Lieferung abschließen

1. **"Lieferung abschließen"** klicken
2. Zusammenfassung prüfen
3. Bestätigen

**Tipp**: Immer Lieferung abschließen, bevor Sie sich abmelden!

## Veredelung

### Paket zur Veredelung

1. **"📦 Paket scannen"** klicken
2. QR-Code scannen
3. **Veredelungsart** wählen:
   - Siebdruck
   - Digitaldruck
   - Stickerei
   - Transferdruck
   - Flexdruck
   - Sublimation
4. **Geschätzte Dauer** eingeben (Minuten)
5. **"✓ Veredelung starten"** klicken

### Aktuelle Aufträge

Rechts sehen Sie alle laufenden Veredelungen:
- Paket-ID
- Veredelungsart
- Startzeit
- Geschätzte Dauer

### Veredelung abschließen

Pakete werden automatisch als "fertig" markiert, wenn die nächste Station sie scannt.

## Betuchung

### Paket in Betuchung nehmen

1. **"📦 Paket scannen"** klicken
2. QR-Code scannen
3. Paketdetails prüfen
4. Optional: **Notizen** hinzufügen
5. **"✓ In Betuchung nehmen"** klicken

### Status

- Grüne Meldung: Erfolgreich
- Rote Meldung: Fehler (z.B. Paket nicht gefunden)

## Qualitätskontrolle

### Paket prüfen

1. **"📦 Paket prüfen"** klicken
2. QR-Code scannen
3. Ware physisch prüfen
4. Entscheidung treffen:

#### Qualität OK

- Button **"✓ Qualität OK"** (grün) klicken
- Paket wird für Versand freigegeben

#### Nacharbeit erforderlich

1. Button **"✗ Nacharbeit"** (rot) klicken
2. **Fehlerarten** auswählen (Mehrfachauswahl):
   - Druckfehler
   - Farbabweichung
   - Positionsfehler
   - Stoffdefekt
   - Verschmutzung
   - Falsche Größe
   - Nahtfehler
   - Sonstiges
3. **Zusätzliche Bemerkungen** eingeben
4. **"Fehler bestätigen"** klicken

### Statistiken

Unten sehen Sie:
- ✓ OK: Anzahl freigegebener Pakete heute
- ✗ Nacharbeit: Anzahl fehlerhafter Pakete heute

## Warenausgang

### Pakete für Versand vorbereiten

1. **"📷 Paket scannen"** klicken
2. Mehrere Pakete nacheinander scannen
3. Gescannte Pakete erscheinen in der Liste rechts

### Pakete aus Liste entfernen

Falls versehentlich gescannt:
- **"✗"** Button neben dem Paket klicken

### Versand abschließen

1. **"🚚 Versand abschließen"** klicken
2. **Versandart** wählen:
   - DHL Express
   - DHL Standard
   - UPS
   - DPD
   - GLS
   - Hermes
   - Selbstabholung
3. Optional: **Tracking-Nummer** eingeben
4. **"✓ Versand bestätigen"** klicken

### Versandlabel

Nach Bestätigung werden automatisch Versandlabel gedruckt.

## Häufige Probleme

### QR-Code wird nicht erkannt

**Lösung:**
- Kamera-Linse reinigen
- Bessere Beleuchtung
- QR-Code glatt halten
- Näher/weiter weg halten
- Manuell eingeben als Notlösung

### RFID-Karte funktioniert nicht

**Lösung:**
- Karte direkt auf Reader legen
- 2 Sekunden warten
- Andere Seite versuchen
- IT kontaktieren wenn weiterhin Probleme

### Programm reagiert nicht

**Lösung:**
1. 30 Sekunden warten
2. Falls keine Reaktion: `Strg+Alt+Entf`
3. Task-Manager → Anwendung beenden
4. Neu starten

### Falsche Sprache

**Lösung:**
- Abmelden
- Auf Login-Bildschirm Flagge anklicken
- Neu anmelden

### Paket im falschen Status

**Lösung:**
- IT kontaktieren
- Paket-ID und Problem notieren
- Workaround: Manuell im nächsten Schritt scannen

## Tastenkürzel

| Taste | Funktion |
|-------|----------|
| `F11` | Vollbild ein/aus |
| `Esc` | Vollbild beenden |
| `Enter` | Bestätigen |
| `Tab` | Nächstes Feld |
| `Strg+C` | Kopieren |
| `Strg+V` | Einfügen |

## Best Practices

### Allgemein

1. **Immer anmelden** mit Ihrer persönlichen RFID-Karte
2. **Pakete sofort scannen** nach Erhalt
3. **Bei Problemen**: Notizen im System hinterlassen
4. **Pausen**: Nach 6 Stunden automatische Pausenerinnerung
5. **Abmelden**: Am Ende der Schicht

### Wareneingang

- Lieferschein mit System-Daten abgleichen
- Beschädigte Pakete fotografieren und notieren
- Lieferung zeitnah abschließen

### Veredelung

- Realistische Zeitschätzungen angeben
- Bei Problemen sofort Notiz hinterlassen
- Veredelungsart korrekt wählen

### Qualitätskontrolle

- Gründlich prüfen - lieber einmal zu viel
- Fehler detailliert beschreiben
- Bei Unsicherheit: Teamleiter fragen

### Versand

- Pakete vor Versand nochmals zählen
- Tracking-Nummern wenn möglich eingeben
- Versandart mit Lieferschein abgleichen

## Support

Bei Problemen:

1. **Neustart** versuchen
2. **Screenshot** machen (Druck-Taste)
3. **IT kontaktieren**:
   - Intern: 555
   - E-Mail: it@shirtful.de
   - Slack: #wms-support

**Wichtige Infos für IT:**
- Welche Station?
- Welcher Fehler?
- Paket-ID?
- Screenshot?

---

**Version 1.0** - Mai 2024 - Shirtful IT Team