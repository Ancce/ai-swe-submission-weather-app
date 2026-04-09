# Weather App Web
Presentazione progetto: https://docs.google.com/document/d/1UuMSRvAnq-7VUQywBhSNrNBUvwCkG4oxj4WV_OcUsAU/edit?usp=sharing 

## Panoramica del progetto

Questa app web fornisce dati meteo attuali e previsioni a 7 giorni per qualsiasi città nel mondo. Utilizza un'interfaccia semplice e intuitiva con autocompletamento per facilitare la ricerca. È stata sviluppata con Flask (Python) per il backend e HTML/CSS/JavaScript per il frontend, convertendo una precedente versione desktop basata su CustomTkinter.

L'app è ideale per utenti che vogliono controllare rapidamente il tempo senza app native, offrendo un'esperienza web responsiva e accessibile da qualsiasi dispositivo.

## Istruzioni di installazione

### Prerequisiti
- Python 3.8 o superiore installato.
- Connessione internet per accedere alle API esterne.

### Passaggi
1. **Clona o scarica il progetto** nella tua directory locale.
2. **Installa le dipendenze**:
   ```
   pip install -r requirements.txt
   ```
   Questo installerà Flask, requests e altre librerie necessarie.
3. **Avvia l'app**:
   ```
   cd src
   python app.py
   ```
   Oppure, per usare Flask CLI:
   ```
   flask --app app run
   ```
4. **Apri il browser** e naviga a `http://127.0.0.1:5000`.

L'app si avvierà in modalità debug, utile per lo sviluppo.

## Guida all'utilizzo

1. **Avvia l'app** seguendo le istruzioni di installazione.
2. **Digita il nome della città** nel campo di input. Dopo 2 caratteri, appariranno suggerimenti automatici (autocompletamento).
3. **Seleziona una città** dal datalist per visualizzare immediatamente il meteo attuale e le previsioni.
   - Alternativa: Premi "Cerca" per vedere una lista di città con stato/regione e seleziona manualmente.
4. **Visualizza i risultati**: Temperatura, vento, umidità, condizioni (con emoji), e previsioni giornaliere.
5. **Interagisci nuovamente**: Digita una nuova città per aggiornare i dati.

L'interfaccia è responsiva e funziona su desktop e mobile.

## Output di esempio

### Schermata principale (senza selezione)
```
🌤️ Meteo
Inserisci una città per vedere il meteo aggiornato

[Campo input con autocompletamento]
[ Bottone Cerca ]
```

### Dopo selezione (es. Roma)
```
🌤️ Meteo
Meteo per: Roma, Roma Capitale, Lazio, Italia

☀️ Cielo sereno
Temperatura: 22.5°C
Vento: 5.2 km/h
Umidità: 60%
