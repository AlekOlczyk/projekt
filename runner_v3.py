import requests
import json
from tabulate import tabulate
from datetime import datetime

# URL API CoinGecko
URL = "https://api.coingecko.com/api/v3/simple/price"
FILE_NAME = "dane.json"

#Pobiera ceny i dodatkowe dane o kryptowalutach.
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

#Wczytuje istniejące portfolio z pliku JSON lub zwraca pustą strukturę.
def load_portfolio():

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
            return existing_data.get("portfolio", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

#Zapisuje portfolio do pliku JSON.
def save_portfolio(portfolio):

    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump({"portfolio": portfolio}, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Błąd zapisu do pliku: {e}")

#Pozwala użytkownikowi sprawdzić cenę wybranej kryptowaluty i wyświetla szczegóły w tabeli.
def check_crypto_price():

    crypto = input("\nPodaj nazwę kryptowaluty, którą chcesz sprawdzić: ").strip().lower()
    data = get_crypto_prices([crypto])

    if data:
        table = []
        for name, values in data.items():
            price = values.get("usd", "Brak danych")
            market_cap = values.get("usd_market_cap", 0) / 1e9  # w miliardach
            change_24h = values.get("usd_24h_change", "Brak danych")

            table.append([
                name.capitalize(),
                f"${price:.2f}" if isinstance(price, (int, float)) else price,
                f"${market_cap:.2f}B" if market_cap else "Brak danych",
                f"{change_24h:.2f}%" if isinstance(change_24h, (int, float)) else change_24h
            ])

        headers = ["Kryptowaluta", "Cena (USD)", "Kapitalizacja (mld USD)", "Zmiana 24h"]
        print(tabulate(table, headers, tablefmt="grid"))
    else:
        print("⚠️ Nie udało się pobrać danych. Sprawdź poprawność nazwy kryptowaluty.")

#Pozwala użytkownikowi kupić kryptowalutę i zapisuje ją w portfelu.
def buy_crypto():

    crypto = input("\nPodaj nazwę kryptowaluty, którą chcesz kupić: ").strip().lower()
    quantity = input(f"Ile jednostek {crypto} chcesz kupić? ")

    try:
        quantity = float(quantity)
        if quantity <= 0:
            print("⚠️ Ilość musi być większa od zera!")
            return
    except ValueError:
        print("⚠️ Wpisz poprawną liczbę!")
        return

    # Pobranie aktualnej ceny kryptowaluty
    data = get_crypto_prices([crypto])
    if crypto not in data:
        print("⚠️ Nie udało się pobrać danych. Sprawdź poprawność nazwy kryptowaluty.")
        return

    price = data[crypto]["usd"]
    cost = quantity * price
    print(f"✅ Zakupiono {quantity} {crypto} za ${cost:.2f} (po kursie ${price:.2f}/szt.)")

    # Aktualizacja portfela
    portfolio = load_portfolio()
    portfolio[crypto] = portfolio.get(crypto, 0) + quantity
    save_portfolio(portfolio)

    print(f"💰 Portfel zaktualizowany! Posiadasz teraz {portfolio[crypto]} {crypto}.")

#Wyświetla aktualne portfolio wraz z wartościami kryptowalut.
def show_portfolio():

    portfolio = load_portfolio()

    if not portfolio:
        print("💼 Twój portfel jest pusty!")
        return

    # Pobranie aktualnych cen wszystkich kryptowalut w portfelu
    crypto_list = list(portfolio.keys())
    prices = get_crypto_prices(crypto_list)

    total_value = 0
    table = []

    for crypto, amount in portfolio.items():
        price = prices.get(crypto, {}).get("usd", 0)  # Pobierz cenę lub domyślnie 0
        value = amount * price  # Wartość kryptowaluty w USD
        total_value += value  # Sumujemy całkowitą wartość portfela

        table.append([
            crypto.capitalize(),
            amount,
            f"${price:.2f}" if price else "Brak danych",
            f"${value:.2f}"
        ])

    print("\n💰 Twój portfel:")
    print(tabulate(table, headers=["Kryptowaluta", "Ilość", "Cena (USD)", "Wartość (USD)"], tablefmt="grid"))
    print(f"\n💵 Łączna wartość portfela: ${total_value:.2f}")


if __name__ == "__main__":
    print("🔍 Aplikacja do monitorowania cen kryptowalut")
    while True:
        print("\n📌 MENU:")
        print("1️⃣ Sprawdź obecny kurs kryptowaluty")
        print("2️⃣ Kup kryptowalutę")
        print("3️⃣ Zobacz swoje portfolio")
        print("4️⃣ Wyjdź z programu")

        choice = input("Wybierz opcję (1/2/3/4): ").strip()

        if choice == "1":
            check_crypto_price()
        elif choice == "2":
            buy_crypto()
        elif choice == "3":
            show_portfolio()
        elif choice == "4":
            print("👋 Zamykanie aplikacji...")
            break
        else:
            print("⚠️ Wybierz poprawną opcję!")
