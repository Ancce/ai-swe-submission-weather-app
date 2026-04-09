# Import delle librerie necessarie
from flask import Flask, render_template, request
import sys
import os

# Aggiunta del percorso src per importare moduli locali
from .weather_api import get_weather, get_coordinates

# Creazione dell'istanza Flask
app = Flask(__name__)

# Dizionario che mappa i codici meteo WMO a descrizioni testuali e emoji
WEATHER_CODES = {
    0: ("Cielo sereno", "☀️"),
    1: ("Principalmente sereno", "🌤️"),
    2: ("Parzialmente nuvoloso", "⛅"),
    3: ("Nuvoloso", "☁️"),
    45: ("Nebbia", "🌫️"),
    48: ("Nebbia con brina", "🌫️"),
    51: ("Pioggerella leggera", "🌦️"),
    53: ("Pioggerella moderata", "🌦️"),
    55: ("Pioggerella intensa", "🌦️"),
    56: ("Pioggerella ghiacciata leggera", "🌨️"),
    57: ("Pioggerella ghiacciata intensa", "🌨️"),
    61: ("Pioggia leggera", "🌧️"),
    63: ("Pioggia moderata", "🌧️"),
    65: ("Pioggia intensa", "🌧️"),
    66: ("Pioggia ghiacciata leggera", "🌨️"),
    67: ("Pioggia ghiacciata intensa", "🌨️"),
    71: ("Nevicata leggera", "❄️"),
    73: ("Nevicata moderata", "❄️"),
    75: ("Nevicata intensa", "❄️"),
    77: ("Granelli di neve", "❄️"),
    80: ("Rovesci leggeri", "🌦️"),
    81: ("Rovesci moderati", "🌦️"),
    82: ("Rovesci violenti", "🌦️"),
    85: ("Nevicate leggere", "❄️"),
    86: ("Nevicate intense", "❄️"),
    95: ("Temporale", "⛈️"),
    96: ("Temporale con grandine leggera", "⛈️"),
    99: ("Temporale con grandine intensa", "⛈️")
}

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Route principale dell'app web per gestire richieste GET e POST.

    Gestisce la ricerca di città, la selezione e la visualizzazione dei dati meteo.
    Restituisce il template HTML con variabili per errori, liste e dati.
    """
    # Inizializzazione variabili per il template
    weather_data = None
    error = None
    city_list = None
    selected_city = None
    
    if request.method == 'POST':
        # Controllo se è una ricerca città
        if 'search' in request.form:
            # Estrazione e validazione del nome città dal form
            city = request.form.get('city', '').strip()
            if not city:
                error = "Inserisci una città valida!"
            else:
                # Chiamata alla funzione per ottenere lista di città
                city_list = get_coordinates(city)
                if not city_list:
                    error = "Nessuna città trovata"
        # Controllo se è una selezione città
        elif 'select' in request.form:
            # Estrazione latitudine e longitudine dai campi nascosti
            lat = request.form.get('lat')
            lon = request.form.get('lon')
            selected_city = request.form.get('selected_city')
            if lat and lon:
                # Chiamata alla funzione per ottenere dati meteo
                weather_data = get_weather(float(lat), float(lon))
                if "error" in weather_data:
                    error = weather_data["error"]
    # --- Funzionalità: Meteo per più città ---
    multi_weather = []
    selected_cities = []
    if request.method == 'POST' and 'multi_city' in request.form:
        cities = request.form.get('multi_city', '').split(';')
        for city in cities:
            city = city.strip().capitalize()
            if city:
                coords = get_coordinates(city)
                if coords:
                    lat, lon = coords[0]['lat'], coords[0]['lon']
                    weather = get_weather(lat, lon)
                    if 'error' not in weather:
                        multi_weather.append({'city': city, 'weather': weather})
                        selected_cities.append(city)
    # --- Fine funzionalità ---
    return render_template(
        'index.html',
        weather_data=weather_data,
        error=error,
        city_list=city_list,
        selected_city=selected_city,
        weather_codes=WEATHER_CODES,
        multi_weather=multi_weather,
        selected_cities=selected_cities
    )

if __name__ == "__main__":
    app.run(debug=True)
