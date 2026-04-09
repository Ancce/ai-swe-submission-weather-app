import requests
from requests.exceptions import Timeout, ConnectionError, RequestException
import time
import urllib.parse

# Dizionario globale per la cache in-memory, chiave: dati e timestamp
_cache = {}
# Durata della cache in secondi (2 ore)
CACHE_DURATION = 2 * 60 * 60

def _get_cached(key):
    """
    Recupera i dati dalla cache se non sono scaduti.

    Controlla se la chiave esiste nella cache e se il timestamp è entro la durata massima.
    Se scaduto, rimuove la voce dalla cache.
    """
    if key in _cache:
        data, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
        else:
            del _cache[key]  # Rimuovi dati scaduti
    return None

def _set_cache(key, data):
    """
    Salva i dati nella cache con il timestamp corrente.

    Aggiunge o aggiorna la voce nella cache con i dati forniti e il tempo attuale.
    """
    _cache[key] = (data, time.time())

def get_coordinates(city, limit=5):
    """
    Ottieni una lista di coordinate (latitudine, longitudine) per una città usando l'API Nominatim di OpenStreetMap.

    Costruisce l'URL con la città codificata per evitare problemi con caratteri speciali,
    invia una richiesta GET, e analizza la risposta JSON per estrarre le informazioni rilevanti.
    Gestisce vari tipi di errori restituendo una lista vuota.
    """
    # Intestazione per identificare l'app (richiesto da Nominatim)
    headers = {'User-Agent': 'WeatherApp/1.0'}
    # Costruzione dell'URL con codifica della città per gestire spazi e caratteri speciali
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(city)}&format=json&limit={limit}"
    try:
        # Invio richiesta GET con timeout di 5 secondi
        response = requests.get(url, headers=headers, timeout=5)
        # Verifica se la risposta è positiva (status code 2xx)
        response.raise_for_status()
        # Parsing della risposta JSON
        data = response.json()
        results = []
        # Ciclo attraverso i risultati per estrarre dati utili
        for item in data:
            results.append({
                'lat': float(item['lat']),  # Conversione a float per latitudine
                'lon': float(item['lon']),  # Conversione a float per longitudine
                'display_name': item['display_name'],  # Nome completo della località
                'state': item.get('state', ''),  # Stato (se disponibile)
                'country': item.get('country', '')  # Paese (se disponibile)
            })
        return results
    except Timeout:
        # Errore se la richiesta supera il timeout
        return []
    except ConnectionError:
        # Errore di connessione (es. rete non disponibile)
        return []
    except requests.exceptions.HTTPError as e:
        # Errore HTTP (es. 404, 500)
        return []
    except (ValueError, KeyError, IndexError):
        # Errori di parsing JSON o accesso a chiavi/liste non esistenti
        return []
    except RequestException:
        # Altri errori di richiesta generici
        return []

def get_weather(lat: float, lon: float) -> dict:
    """
    Recupera i dati meteo attuali e le previsioni a 7 giorni per le coordinate geografiche fornite.

    Questa funzione interroga l'API Open-Meteo per ottenere informazioni meteorologiche dettagliate,
    inclusi temperatura, velocità del vento, codice meteo e previsioni giornaliere. Utilizza una cache
    in-memory per evitare richieste ripetute entro 30 minuti, migliorando le prestazioni e riducendo
    il carico sulle API esterne.

    Args:
        lat (float): La latitudine della località (valori compresi tra -90 e 90).
        lon (float): La longitudine della località (valori compresi tra -180 e 180).

    Returns:
        dict: Un dizionario contenente i dati meteo con le seguenti chiavi:
            - 'temperature' (float or None): Temperatura attuale in gradi Celsius.
            - 'windspeed' (float or None): Velocità del vento in km/h.
            - 'weathercode' (int or None): Codice numerico delle condizioni meteo (vedi WEATHER_CODES per descrizioni).
            - 'humidity' (int or str): Umidità relativa in percentuale (0-100) o "N/A" se non disponibile.
            - 'time' (str or None): Timestamp dell'ultimo aggiornamento (formato ISO).
            - 'daily' (dict): Previsioni giornaliere con chiavi:
                - 'dates' (list[str]): Lista di date (formato YYYY-MM-DD).
                - 'max_temps' (list[float]): Temperature massime giornaliere.
                - 'min_temps' (list[float]): Temperature minime giornaliere.
                - 'codes' (list[int]): Codici meteo giornalieri.
            In caso di errore, restituisce un dict con chiave 'error' e messaggio descrittivo (str).

    Raises:
        ValueError: Se lat o lon non sono numeri validi (sollevato internamente durante conversione).
        ConnectionError: Se non è possibile connettersi all'API (rete non disponibile).
        Timeout: Se la richiesta API supera il timeout di 5 secondi.
        requests.exceptions.HTTPError: Per errori HTTP (es. 404, 500) dall'API.
        KeyError: Se la risposta JSON ha una struttura inattesa.
        Exception: Per errori generici non previsti.

    Example:
        >>> from weather_api import get_weather
        >>> data = get_weather(41.9028, 12.4964)  # Coordinate di Roma
        >>> print(data['temperature'])
        22.5
        >>> print(data['daily']['max_temps'][0])  # Max domani
        24.0

        # Esempio con errore
        >>> error_data = get_weather(999, 999)  # Coordinate invalide
        >>> print(error_data)
        {'error': 'Errore nel parsing dei dati meteo'}
    """
    # Validazione coordinate
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return {"error": "Coordinate geografiche invalide"}

    # Crea chiave cache basata su latitudine e longitudine formattate
    cache_key = f"{lat:.4f},{lon:.4f}"
    # Verifica se i dati sono in cache
    cached_data = _get_cached(cache_key)
    if cached_data is not None:
        return cached_data  # Restituisci dati dalla cache

    try:
        # Costruzione URL per l'API Open-Meteo con parametri ottimizzati
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&daily=temperature_2m_max,temperature_2m_min,weathercode"
            f"&hourly=relative_humidity_2m"
            f"&forecast_days=7"
            f"&timezone=auto"
        )
        # Richiedi risposta compressa (gzip)
        headers = {'Accept-Encoding': 'gzip'}
        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()
        data = response.json()
        current = data.get('current_weather', {})
        daily = data.get('daily', {})
        hourly = data.get('hourly', {})

        humidity = "N/A"
        if hourly.get('relative_humidity_2m'):
            humidity = hourly['relative_humidity_2m'][0]

        weather_result = {
            "temperature": current.get('temperature'),
            "windspeed": current.get('windspeed'),
            "weathercode": current.get('weathercode'),
            "humidity": humidity,
            "time": current.get('time'),
            "daily": {
                "dates": daily.get('time', []),
                "max_temps": daily.get('temperature_2m_max', []),
                "min_temps": daily.get('temperature_2m_min', []),
                "codes": daily.get('weathercode', [])
            }
        }
        _set_cache(cache_key, weather_result)
        return weather_result
    except Timeout:
        return {"error": "Timeout: il server ha impiegato troppo tempo a rispondere"}
    except ConnectionError:
        return {"error": "Errore di connessione: verifica la tua connessione internet"}
    except requests.exceptions.HTTPError as e:
        # Errore HTTP dalla risposta
        return {"error": f"Errore HTTP: {e.response.status_code}"}
    except ValueError:
        # Errore di parsing JSON
        return {"error": "Errore nel parsing dei dati meteo"}
    except KeyError:
        # Chiave mancante nella risposta JSON
        return {"error": "Formato di risposta API inatteso"}
    except RequestException as e:
        # Altri errori di richiesta
        return {"error": f"Errore di richiesta: {str(e)}"}
    except Exception as e:
        # Eccezione generica
        return {"error": f"Errore inatteso: {str(e)}"}