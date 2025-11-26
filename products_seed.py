import json
import random

# Danh sách danh mục sản phẩm
CATEGORIES = [
    "Shoes", "T-Shirt", "Shorts", "Jacket", "Backpack",
    "Football", "Gloves", "Running Shoes", "Yoga Pants",
    "Sport Bottle", "Cap", "Gym Bag"
]

# Từ khoá để random ảnh thể thao từ Unsplash
UNSPLASH_KEYWORDS = [
    "sport", "fitness", "running", "football", "gym", "training",
    "basketball", "swimming", "cycling", "workout", "tennis",
    "badminton", "soccer", "athlete"
]

def random_image():
    keyword = random.choice(UNSPLASH_KEYWORDS)
    # random 1 ảnh unique → nhờ vào query random
    return f"https://source.unsplash.com/random/600x600/?{keyword}&sig={random.randint(1,999999)}"

def random_price():
    return random.randint(150_000, 2_000_000)

def random_product_name(category):
    adjectives = [
        "Pro", "Max", "Ultra", "Force", "Fusion", "X", "Prime",
        "Elite", "Power", "Flex", "Speed", "Storm"
    ]
    return f"{category} {random.choice(adjectives)} {random.randint(1, 500)}"

products = []

for i in range(150):
    category = random.choice(CATEGORIES)
    product = {
        "id": i + 1,
        "name": random_product_name(category),
        "category": category,
        "price": random_price(),
        "image": random_image(),
        "description": "High-quality sports product suitable for training and competition."
    }
    products.append(product)

# Xuất ra file JSON
with open("products.json", "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=4)

print("Đã tạo 150 sản phẩm thành công trong products.json!")
