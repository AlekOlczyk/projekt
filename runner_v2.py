import requests
import json
from tabulate import tabulate
from datetime import datetime

# URL API CoinGecko
URL = "https://api.coingecko.com/api/v3/simple/price"
FILE_NAME = "dane.json"

#Pobiera dane o cenach kryptowalut.
def get_crypto_prices(crypto_list):

    ids = ",".join(crypto_list)
    params = {
        "ids": ids,
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_change": "true"
    }

    response = requests.get(URL, params=params)
    if response.status_code != 200:
        print("❌ Błąd pobierania danych!")
        return {}

    return response.json()

#Wczytuje istniejące dane z pliku JSON lub zwraca pustą strukturę.
def load_existing_data():

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
            if isinstance(existing_data, dict) and "history" in existing_data:
                return existing_data  # Jeśli już ma poprawną strukturę, zwraca ją
            else:
                return {"history": []}  # Jeśli format jest błędny, tworzy nową strukturę
    except (FileNotFoundError, json.JSONDecodeError):
        return {"history": []}  # Jeśli plik nie istnieje lub jest uszkodzony, zwraca pustą listę

#Dopisuje nowe dane do pliku JSON zamiast go nadpisywać.
def save_to_file(data):

    try:
        existing_data = load_existing_data()

        # Dodanie nowej daty
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "data": data
        }
        existing_data["history"].append(entry)  # Dopisuje do listy

        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)

        print(f"✅ Dane zapisane do {FILE_NAME} (czas: {timestamp})")
    except Exception as e:
        print(f"❌ Błąd zapisu do pliku: {e}")


#Formatuje i wyświetla dane w tabeli.
def display_crypto_data(data):

    if not data:
        print("❌ Brak danych do wyświetlenia!")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table = []

    for crypto, values in data.items():
        price = values.get('usd', 'Brak danych')
        market_cap = values.get('usd_market_cap', 0) / 1e9  # w miliardach
        change_24h = values.get('usd_24h_change', 'Brak danych')

        table.append([
            crypto.capitalize(),
            f"${price:.2f}" if isinstance(price, (int, float)) else price,
            f"${market_cap:.2f}B" if market_cap else "Brak danych",
            f"{change_24h:.2f}%" if isinstance(change_24h, (int, float)) else change_24h
        ])

    headers = ["Kryptowaluta", "Cena (USD)", "Kapitalizacja (mld USD)", "Zmiana 24h"]
    print(f"\n📅 Aktualizacja danych: {timestamp}")
    print(tabulate(table, headers, tablefmt="grid"))


if __name__ == "__main__":
    print("🔍 Aplikacja do monitorowania cen kryptowalut")
    while True:
        user_input = input("\nPodaj kryptowaluty (np. bitcoin,ethereum) lub 'exit' aby zakończyć: ").strip().lower()

        if user_input == "exit":
            print("👋 Zamykanie aplikacji...")
            break

        if not user_input:
            print("⚠️ Musisz podać przynajmniej jedną kryptowalutę!")
            continue

        cryptos = user_input.replace(" ", "").split(",")
        data = get_crypto_prices(cryptos)

        if data:
            display_crypto_data(data)
            save_to_file(data)
        else:
            print("⚠️ Nie udało się pobrać danych. Sprawdź poprawność nazw kryptowalut.")
