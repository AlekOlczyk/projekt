from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import json
import os

app = Flask(__name__)

FILE_NAME = "dane.json"
URL = "https://api.coingecko.com/api/v3/simple/price"

def get_crypto_prices(crypto_list):
    """Pobiera ceny i dane o kryptowalutach."""
    ids = ",".join(crypto_list)
    params = {
        "ids": ids,
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_change": "true"
    }
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        return response.json()
    return {}

def load_portfolio():
    """Wczytuje portfolio z pliku JSON."""
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("portfolio", {})
    return {}

def save_portfolio(portfolio):
    """Zapisuje portfolio do pliku JSON."""
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump({"portfolio": portfolio}, file, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/portfolio")
def portfolio():
    portfolio = load_portfolio()
    crypto_list = list(portfolio.keys())
    prices = get_crypto_prices(crypto_list)

    total_value = 0
    portfolio_data = []

    for crypto, amount in portfolio.items():
        price = prices.get(crypto, {}).get("usd", 0)
        value = amount * price
        total_value += value

        portfolio_data.append({
            "name": crypto.capitalize(),
            "amount": amount,
            "price": f"${price:.2f}" if price else "Brak danych",
            "value": f"${value:.2f}"
        })

    return render_template("portfolio.html", portfolio=portfolio_data, total_value=f"${total_value:.2f}")

@app.route("/buy", methods=["POST"])
def buy_crypto():
    crypto = request.form.get("crypto").lower()
    quantity = float(request.form.get("quantity"))

    if quantity <= 0:
        return jsonify({"error": "Ilość musi być większa od zera!"}), 400

    data = get_crypto_prices([crypto])
    if crypto not in data:
        return jsonify({"error": "Nieprawidłowa kryptowaluta!"}), 400

    price = data[crypto]["usd"]
    portfolio = load_portfolio()
    portfolio[crypto] = portfolio.get(crypto, 0) + quantity
    save_portfolio(portfolio)

    return redirect(url_for("portfolio"))

@app.route("/price", methods=["GET"])
def check_crypto_price():
    crypto = request.args.get("crypto").lower()
    data = get_crypto_prices([crypto])

    if crypto in data:
        return jsonify(data[crypto])
    else:
        return jsonify({"error": "Nie znaleziono kryptowaluty!"}), 404

if __name__ == "__main__":
    app.run(debug=True)
