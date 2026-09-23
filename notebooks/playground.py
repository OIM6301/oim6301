import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    charge = 10
    return (charge,)


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
