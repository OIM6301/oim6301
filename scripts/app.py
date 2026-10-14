import bmi

# result = bmi.compute_bmi(70, 1.75)
# print(f"Computed BMI: {result:.2f}")

people = [
    {"name": "Alice", "height": 1.75, "weight": 70},
    {"name": "Bob", "height": 1.80, "weight": 85},
    {"name": "Charlie", "height": 1.68, "weight": 65},
    {"name": "Frank", "height": 1.72, "weight": 78},
    {"name": "Grace", "height": 1.65, "weight": 60},
    {"name": "Diana", "height": 1.60, "weight": 55},
    {"name": "Evan", "height": 1.90, "weight": 95},
]

for person in people:
    # print(person)
    weight = person["weight"]
    height = person["height"]
    bmi_value = bmi.compute_bmi(weight, height)
    category = bmi.classify_bmi(bmi_value)
    print(f"{person['name']} has a BMI of {bmi_value:.2f}, which is classified as {category}.")