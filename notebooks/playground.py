import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    # Review of Session 5
    # Q1

    orders = [
        {"OrderID": 10248, "ShipCountry": "France"},
        {"OrderID": 10249, "ShipCountry": "Germany"},
        {"OrderID": 10248, "ShipCountry": "France"},
        {"OrderID": 10249, "ShipCountry": "Germany"},
        {"OrderID": 10248, "ShipCountry": "USA"},
        {"OrderID": 10249, "ShipCountry": "Germany"},
        {"OrderID": 10248, "ShipCountry": "France"},
        {"OrderID": 10249, "ShipCountry": "China"},
        {"OrderID": 10248, "ShipCountry": "China"},
    ]
    type(orders)
    return (orders,)


@app.cell
def _(orders):
    orders[0]["ShipCountry"]
    return


@app.cell
def _(orders):
    countries = []
    for order in orders:
        # print(type(order))
        print(order['OrderID'], order['ShipCountry'])
        countries.append(order['ShipCountry'])

    len(set(countries))
    return


@app.cell
def _():
    # Q3
    bmi = 27
    if bmi >= 30:
        category = "Obese"
    elif bmi >= 25:
        category = "Overweight"
    elif bmi >= 18.5:
        category = "Normal"
    else:
        category = "Underweight"
    print(category)
    return


@app.cell
def _():
    data = [
        {
            "name": "OpenAI",
            "vendor": "openai",
            "apiKey": "${input:chat.lm.secret.7a201382}"
        },
        {
            "name": "Babson AI",
            "vendor": "customendpoint",
            "apiKey": "${input:chat.lm.secret.-23df36c}",
            "apiType": "messages",
            "models": [
                {
                    "id": "claude-sonnet-5",
                    "name": "Sonnet 5 (Babson)",
                    "toolCalling": True,
                    "vision": True,
                    "maxInputTokens": 200000,
                    "maxOutputTokens": 32000
                }
            ]
        }
    ]
    return (data,)


@app.cell
def _(data):
    data[1]['models'][0]['name']
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    total = 0
    for charge in [10, 20, 30]:    
        total = total + charge
    print(total)
    return (charge,)


@app.cell
def _():
    max(["16.75", "9.50", "22.25"])
    return


@app.cell
def _():
    order_lines = ["notebook", "pen"]
    order_lines.extend(["stapler", "tape"])
    order_lines
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    charge = 10
    return (charge,)


@app.cell
def _():
    return


@app.cell
def _(charge):
    print(charge)
    return


@app.cell
def _():
    return


@app.cell
def _():
    import csv

    products = [
        [1, "Notebook", 2.50],
        [2, "Pen", 1.20],
        [3, "Backpack", 25.00],
        [4, "Water Bottle", 8.75],
        [5, "Desk Lamp", 15.30],
        [6, "Headphones", 45.00],
        [7, "Mouse", 12.99],
        [8, "Keyboard", 22.50],
        [9, "Monitor Stand", 18.00],
        [10, "Phone Case", 9.99],
    ]

    with open("products.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["product_id", "name", "price"])
        for product in products:
            writer.writerow(product)

    products
    return (csv,)


@app.cell
def _(csv):
    loaded_products = []
    with open("products.csv") as csv_file2:
        reader = csv.reader(csv_file2)
        next(reader)
        for csv_row in reader:
            loaded_products.append(csv_row)

    loaded_products
    return (loaded_products,)


@app.cell
def _(loaded_products):
    total_price = 0
    for row in loaded_products:
        total_price = total_price + float(row[2])

    round(total_price, 2)
    return


if __name__ == "__main__":
    app.run()
