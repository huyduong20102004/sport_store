import sqlite3
import os
import random
from flask import Flask, render_template, g, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "shop.db")
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# ---------- Database helpers ----------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cur = db.cursor()
    # users - updated to include email and fullname
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        fullname TEXT,
        oauth_provider TEXT,
        oauth_id TEXT
    )
    """)
    # products
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        image_url TEXT,
        description TEXT
    )
    """)
    db.commit()

def seed_products_if_empty():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    if count >= 100:
        return
    # clear and seed fresh
    cur.execute("DELETE FROM products")
    
    # Expanded sport products catalog with 100+ items
    products_data = [
        # === GIÀY THỂ THAO (30 sản phẩm) ===
        ("Giày Nike Air Max 2024", "Shoes", 2890000, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80", "Giày chạy bộ Nike Air Max với đệm khí tối ưu, thiết kế năng động, phù hợp mọi địa hình"),
        ("Giày Adidas Ultraboost 23", "Shoes", 3290000, "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80", "Giày chạy bộ Adidas Ultraboost công nghệ đệm Boost đỉnh cao, thoải mái cả ngày dài"),
        ("Giày Puma RS-X", "Shoes", 2190000, "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500&q=80", "Giày sneaker thể thao Puma RS-X phong cách retro, thiết kế đa sắc màu trendy"),
        ("Giày Nike React Infinity", "Shoes", 3490000, "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=500&q=80", "Giày chạy bộ Nike React Infinity với công nghệ React foam êm ái, chống chấn thương"),
        ("Giày Adidas NMD R1", "Shoes", 2690000, "https://images.unsplash.com/photo-1539185441755-769473a23570?w=500&q=80", "Giày thể thao Adidas NMD R1 phong cách urban, đế Boost êm ái và năng động"),
        ("Giày Under Armour HOVR", "Shoes", 2990000, "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500&q=80", "Giày chạy bộ Under Armour với công nghệ HOVR đệm êm, phản hồi năng lượng tối ưu"),
        ("Giày Reebok Nano X2", "Shoes", 2490000, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&q=80", "Giày tập gym Reebok Nano X2 bền bỉ, ổn định, phù hợp CrossFit và tập luyện"),
        ("Giày Nike Pegasus 40", "Shoes", 3190000, "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=500&q=80", "Giày chạy bộ Nike Pegasus 40 nhẹ nhàng, đệm êm, phù hợp chạy đường dài"),
        ("Giày Adidas Solar Glide", "Shoes", 2790000, "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=500&q=80", "Giày chạy bộ Adidas Solar Glide năng lượng boost, độ bám tốt, bền bỉ"),
        ("Giày Nike Metcon 8", "Shoes", 3390000, "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=500&q=80", "Giày tập gym Nike Metcon 8 ổn định tuyệt vời, hỗ trợ nâng tạ và HIIT"),
        ("Giày Puma Velocity Nitro", "Shoes", 2590000, "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80", "Giày chạy bộ Puma Velocity Nitro đệm êm, nhẹ, thoáng khí tối ưu"),
        ("Giày Asics Gel-Kayano 29", "Shoes", 3690000, "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=500&q=80", "Giày chạy bộ Asics Gel-Kayano hỗ trợ vòm chân, ổn định cho chân bẹt"),
        ("Giày New Balance 1080v12", "Shoes", 3490000, "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=500&q=80", "Giày chạy bộ New Balance Fresh Foam êm ái, thoải mái, phù hợp đường dài"),
        ("Giày Nike ZoomX Vaporfly", "Shoes", 5990000, "https://images.unsplash.com/photo-1539185441755-769473a23570?w=500&q=80", "Giày chạy marathon Nike ZoomX Vaporfly tấm carbon, tốc độ đỉnh cao"),
        ("Giày Adidas Supernova", "Shoes", 2390000, "https://images.unsplash.com/photo-1562183241-b937e95585b6?w=500&q=80", "Giày chạy bộ Adidas Supernova đệm êm, thoải mái, giá hợp lý"),
        ("Giày Hoka One One Clifton", "Shoes", 3790000, "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500&q=80", "Giày chạy bộ Hoka Clifton đệm cực êm, nhẹ, phù hợp mọi cự ly"),
        ("Giày Nike Air Zoom Tempo", "Shoes", 3990000, "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=500&q=80", "Giày training Nike Air Zoom Tempo năng động, phản hồi tốt"),
        ("Giày Saucony Ride 15", "Shoes", 2890000, "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500&q=80", "Giày chạy bộ Saucony Ride linh hoạt, đệm vừa phải, bền bỉ"),
        ("Giày Mizuno Wave Rider", "Shoes", 3190000, "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&q=80", "Giày chạy bộ Mizuno Wave công nghệ sóng, ổn định tốt"),
        ("Giày Brooks Ghost 15", "Shoes", 3390000, "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=500&q=80", "Giày chạy bộ Brooks Ghost êm ái, linh hoạt, phù hợp hàng ngày"),
        ("Giày Nike Joyride", "Shoes", 2990000, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80", "Giày Nike Joyride công nghệ hạt đệm độc đáo, thoải mái tối đa"),
        ("Giày Adidas Terrex Swift", "Shoes", 3190000, "https://images.unsplash.com/photo-1539185441755-769473a23570?w=500&q=80", "Giày trail running Adidas Terrex bám địa hình tốt, chống nước"),
        ("Giày Salomon Speedcross", "Shoes", 3490000, "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=500&q=80", "Giày chạy trail Salomon Speedcross độ bám cực tốt, địa hình khó"),
        ("Giày On Cloudstratus", "Shoes", 4290000, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&q=80", "Giày chạy bộ On Cloud công nghệ đệm đám mây, nhẹ nhàng"),
        ("Giày Nike Free RN", "Shoes", 2390000, "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500&q=80", "Giày Nike Free RN linh hoạt tự nhiên, phù hợp chạy nhẹ"),
        ("Giày Adidas 4D Run", "Shoes", 5490000, "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=500&q=80", "Giày Adidas 4D đế in 3D công nghệ cao, thiết kế tương lai"),
        ("Giày Nike Air Jordan XXXVII", "Shoes", 4990000, "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=500&q=80", "Giày bóng rổ Air Jordan công nghệ đỉnh cao, phong cách iconic"),
        ("Giày Converse Chuck Taylor", "Shoes", 1290000, "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=500&q=80", "Giày Converse Chuck Taylor classic, phong cách vintage bất hủ"),
        ("Giày Vans Old Skool", "Shoes", 1590000, "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500&q=80", "Giày Vans Old Skool phong cách skate, thiết kế đơn giản trendy"),
        ("Giày Fila Disruptor II", "Shoes", 1890000, "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500&q=80", "Giày Fila Disruptor phong cách chunky, xu hướng thời trang"),
        
        # === QUẦN ÁO THỂ THAO (30 sản phẩm) ===
        ("Áo thun Nike Dri-FIT", "Clothing", 690000, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500", "Áo thun thể thao Nike Dri-FIT công nghệ thấm hút mồ hôi, thoáng khí tối ưu"),
        ("Quần short Adidas 3-Stripes", "Clothing", 590000, "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500", "Quần short thể thao Adidas 3-Stripes thoải mái, co giãn 4 chiều"),
        ("Áo khoác Puma Windbreaker", "Clothing", 1290000, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500", "Áo khoác gió Puma Windbreaker chống nước, nhẹ nhàng"),
        ("Quần legging Nike Pro", "Clothing", 890000, "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500", "Quần legging Nike Pro co giãn tốt, ôm dáng, hỗ trợ cơ bắp"),
        ("Áo tank top Under Armour", "Clothing", 490000, "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=500", "Áo ba lỗ Under Armour HeatGear thoáng mát, thấm hút tốt"),
        ("Quần jogger Adidas Essential", "Clothing", 1090000, "https://images.unsplash.com/photo-1517438476312-10d79c077509?w=500", "Quần jogger Adidas Essential thoải mái, phong cách sporty"),
        ("Áo hoodie Nike Sportswear", "Clothing", 1590000, "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500", "Áo hoodie Nike Sportswear ấm áp, phong cách, cotton cao cấp"),
        ("Quần dài Puma Training", "Clothing", 990000, "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500", "Quần dài tập luyện Puma dryCELL, thấm hút mồ hôi tốt"),
        ("Áo polo Lacoste Sport", "Clothing", 1790000, "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=500", "Áo polo thể thao Lacoste cao cấp, vải pique thoáng mát"),
        ("Bộ đồ tập yoga", "Clothing", 1490000, "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=500", "Bộ đồ tập yoga nữ co giãn 4 chiều, ôm dáng, thời trang"),
        ("Áo khoác Nike Therma-FIT", "Clothing", 1890000, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500", "Áo khoác Nike Therma-FIT giữ ấm tốt, chống gió hiệu quả"),
        ("Quần short Reebok CrossFit", "Clothing", 690000, "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500", "Quần short Reebok CrossFit linh hoạt, bền bỉ, thoáng mát"),
        ("Áo thun Adidas FreeLift", "Clothing", 790000, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500", "Áo thun Adidas FreeLift thiết kế nâng cao, không bị cuộn"),
        ("Quần legging Lululemon", "Clothing", 1690000, "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500", "Quần legging Lululemon Align siêu mềm, ôm dáng hoàn hảo"),
        ("Áo bra thể thao Nike", "Clothing", 790000, "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=500", "Áo bra thể thao Nike hỗ trợ tốt, thoải mái, thiết kế đẹp"),
        ("Quần chạy bộ Asics", "Clothing", 890000, "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500", "Quần short chạy bộ Asics nhẹ, thoáng, có túi đựng điện thoại"),
        ("Áo khoác bomber Puma", "Clothing", 1990000, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500", "Áo khoác bomber Puma phong cách, chất liệu cao cấp"),
        ("Quần tập gym Gymshark", "Clothing", 1290000, "https://images.unsplash.com/photo-1517438476312-10d79c077509?w=500", "Quần tập gym Gymshark ôm dáng, tôn cơ bắp, form đẹp"),
        ("Áo compression Under Armour", "Clothing", 990000, "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=500", "Áo compression Under Armour ép cơ, tăng hiệu suất"),
        ("Quần short bơi Speedo", "Clothing", 590000, "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500", "Quần bơi Speedo chuyên nghiệp, chống clo, bền màu"),
        ("Áo gió Adidas Marathon", "Clothing", 1490000, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500", "Áo khoác gió Adidas siêu nhẹ, gấp gọn, chống nước tốt"),
        ("Quần 7/8 Nike Capri", "Clothing", 890000, "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500", "Quần 7/8 Nike Capri phù hợp tập yoga, gym, chạy bộ"),
        ("Áo thun Reebok Activchill", "Clothing", 690000, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500", "Áo thun Reebok Activchill mát lạnh tức thì, công nghệ làm mát"),
        ("Quần dài New Balance", "Clothing", 1090000, "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500", "Quần dài New Balance thoải mái, phù hợp mặc hàng ngày"),
        ("Áo vest Nike Training", "Clothing", 1290000, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500", "Áo vest Nike Training giữ ấm cốt lõi, thoáng mát tay áo"),
        ("Quần short 2-in-1 Salomon", "Clothing", 990000, "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500", "Quần short Salomon 2 lớp, có quần bó bên trong, chống sượt"),
        ("Áo thun Mizuno DryLite", "Clothing", 690000, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500", "Áo thun Mizuno DryLite khô nhanh, siêu nhẹ, thoáng khí"),
        ("Quần legging Reebok Lux", "Clothing", 1190000, "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500", "Quần legging Reebok Lux bóng nhẹ, ôm dáng, thời trang"),
        ("Áo khoác The North Face", "Clothing", 2990000, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500", "Áo khoác The North Face chống nước tốt, giữ ấm, bền bỉ"),
        ("Bộ đồ nỉ Adidas Tracksuit", "Clothing", 2490000, "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500", "Bộ đồ nỉ Adidas Tracksuit ấm áp, phong cách retro classic"),
        
        # === PHỤ KIỆN (25 sản phẩm) ===
        ("Găng tay tập gym Nike", "Accessories", 390000, "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?w=500", "Găng tay tập gym Nike bảo vệ tay, chống trơn trượt"),
        ("Túi thể thao Adidas Duffel", "Accessories", 890000, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500", "Túi xách thể thao Adidas Duffel rộng rãi, nhiều ngăn"),
        ("Bình nước Hydro Flask 1L", "Accessories", 590000, "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500", "Bình giữ nhiệt Hydro Flask giữ lạnh 24h, không BPA"),
        ("Khăn thể thao microfiber", "Accessories", 190000, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500", "Khăn lau mồ hôi microfiber thấm hút nhanh, nhẹ nhàng"),
        ("Dây đeo Apple Watch Sport", "Accessories", 290000, "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=500", "Dây đeo thể thao cho Apple Watch thoáng khí, bền bỉ"),
        ("Băng đô thể thao Nike", "Accessories", 150000, "https://images.unsplash.com/photo-1611312449408-fcece27cdbb7?w=500", "Băng đeo trán Nike Swoosh thấm hút mồ hôi tốt"),
        ("Tất thể thao Adidas 3 đôi", "Accessories", 290000, "https://assets.adidas.com/images/w_600,f_auto,q_auto/ee26f45e45d947a998f29246198a0d44_9366/Bo_3_DJoi_Tat_Logo_DJen_JI6315.jpg", "Combo 3 đôi tất thể thao Adidas cushion, êm ái"),
        ("Ba lô thể thao Nike Brasilia", "Accessories", 790000, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500", "Ba lô thể thao Nike Brasilia đa năng, nhiều ngăn"),
        ("Băng quấn cổ tay Harbinger", "Accessories", 290000, "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?w=500", "Băng quấn cổ tay Harbinger hỗ trợ nâng tạ, chống chấn thương"),
        ("Túi đựng giày Nike", "Accessories", 390000, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500", "Túi đựng giày Nike chống bụi, thoáng khí, tiện lợi"),
        ("Kính bơi Speedo Vanquisher", "Accessories", 490000, "https://images.unsplash.com/photo-1519315901367-f34ff9154487?w=500&q=80", "Kính bơi Speedo chống UV, chống sương mù, view rộng"),
        ("Mũ lưỡi trai Nike", "Accessories", 490000, "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=500", "Mũ thể thao Nike Dri-FIT chống nắng, thoáng khí"),
        ("Đai lưng tập gym", "Accessories", 690000, "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?w=500", "Đai lưng tập gym hỗ trợ cột sống, nâng tạ an toàn"),
        ("Túi đựng nước Nike", "Accessories", 290000, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500", "Túi đựng bình nước Nike gọn nhẹ, dễ mang theo"),
        ("Kính mát thể thao Oakley", "Accessories", 1490000, "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500", "Kính thể thao Oakley chống UV, ôm sát, không rơi"),
        ("Băng đeo điện thoại chạy bộ", "Accessories", 190000, "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500&q=80", "Băng đeo điện thoại chạy bộ chống nước, không rơi"),
        ("Túi đeo hông running", "Accessories", 390000, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500", "Túi đeo hông chạy bộ siêu nhẹ, chống nước, đựng điện thoại"),
        ("Bình lắc protein Blender", "Accessories", 290000, "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500", "Bình lắc protein Blender Bottle có bi trộn, không rò rỉ"),
        ("Khăn trải thảm yoga", "Accessories", 390000, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500", "Khăn trải thảm yoga chống trơn, thấm mồ hôi, gọn nhẹ"),
        ("Đồng hồ đeo tay Casio G-Shock", "Accessories", 2490000, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500", "Đồng hồ thể thao Casio G-Shock chống nước 200m, bền bỉ"),
        ("Tai nghe không dây Sony", "Accessories", 1990000, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80", "Tai nghe Sony không dây chống nước, bass mạnh, pin 8h"),
        ("Túi giặt đồ thể thao", "Accessories", 150000, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500", "Túi giặt chuyên dụng cho quần áo thể thao, bảo vệ vải"),
        ("Miếng lót giày thể thao", "Accessories", 190000, "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=500&q=80", "Miếng lót giày thể thao chống hôi, êm ái, thoáng khí"),
        ("Nón bảo hiểm xe đạp", "Accessories", 890000, "https://images.unsplash.com/photo-1614354540168-e0a8f3c1ed9f?w=500&q=80", "Nón bảo hiểm xe đạp nhẹ, thoáng khí, an toàn cao"),
        ("Đai nịt chạy bộ FlipBelt", "Accessories", 490000, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500", "Đai nịt chạy bộ FlipBelt co giãn, không chùng, đựng nhiều đồ"),
        
        # === DỤNG CỤ TẬP LUYỆN (15 sản phẩm) ===
        ("Tạ tay 5kg (cặp)", "Gear", 490000, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500", "Tạ tay 5kg cao su bọc ngoài, chống trơn trượt"),
        ("Thảm yoga cao cấp 6mm", "Gear", 690000, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=500&q=80", "Thảm tập yoga cao cấp dày 6mm, chống trơn, êm ái"),
        ("Dây kháng lực 5 mức độ", "Gear", 390000, "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=500&q=80", "Bộ dây kháng lực 5 mức độ, tập toàn thân"),
        ("Bóng tập yoga 65cm", "Gear", 490000, "https://images.unsplash.com/photo-1587557387938-c1560d6576fb?w=500&q=80", "Bóng tập Yoga Ball 65cm chống nổ, tập core hiệu quả"),
        ("Dây nhảy thể thao tốc độ", "Gear", 190000, "https://images.unsplash.com/photo-1611672585731-fa10603fb9e0?w=500&q=80", "Dây nhảy thể thao có đếm số vòng, phù hợp cardio"),
        ("Bóng Medicine Ball 8kg", "Gear", 890000, "https://images.unsplash.com/photo-1584735175315-9d5df23860e6?w=500&q=80", "Bóng tập Medicine Ball 8kg cao su bền bỉ"),
        ("Xà đơn treo tường", "Gear", 790000, "https://images.unsplash.com/photo-1590487988256-9ed24133863e?w=500&q=80", "Xà đơn treo tường đa năng, chịu lực 150kg"),
        ("Con lăn massage foam", "Gear", 590000, "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=500", "Con lăn massage foam roller, giải phỏng cơ"),
        ("Tạ điều chỉnh Bowflex 24kg", "Gear", 4990000, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500", "Tạ tay điều chỉnh Bowflex 2.5-24kg, tiết kiệm không gian"),
        ("Ghế tập gym đa năng", "Gear", 2990000, "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=500", "Ghế tập gym điều chỉnh đa góc, chắc chắn, gấp gọn"),
        ("Bóng Slam Ball 10kg", "Gear", 690000, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500", "Bóng Slam Ball 10kg chống nứt, tập sức mạnh bùng nổ"),
        ("Kettlebell 12kg", "Gear", 890000, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500", "Kettlebell 12kg gang đúc, tay cầm thoải mái, bền bỉ"),
        ("Xà kép tập chống đẩy", "Gear", 490000, "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=500", "Xà kép tập chống đẩy chắc chắn, chống trơn, tháo lắp dễ"),
        ("Bóng Bosu Balance", "Gear", 1490000, "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500", "Bóng cân bằng Bosu tập thăng bằng, core, phục hồi"),
        ("Bộ tạ đĩa 30kg", "Gear", 1990000, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500", "Bộ tạ đĩa 30kg gang đúc, có thanh đòn, chắc chắn"),
    ]
    
    for name, cat, price, image_url, description in products_data:
        cur.execute("INSERT INTO products (name, category, price, image_url, description) VALUES (?, ?, ?, ?, ?)",
                    (name, cat, price, image_url, description))
    db.commit()

# Initialize DB & seed
with app.app_context():
    init_db()
    seed_products_if_empty()

# ---------- Auth helpers ----------
def create_user(username, password):
    db = get_db()
    cur = db.cursor()
    pw_hash = generate_password_hash(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)

def get_user_id(username):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    r = cur.fetchone()
    return r["id"] if r else None

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/products")
def products_page():
    # optional q param for search
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 24
    offset = (page-1)*per_page
    db = get_db()
    cur = db.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("SELECT COUNT(*) FROM products WHERE name LIKE ? OR description LIKE ?", (like, like))
        total = cur.fetchone()[0]
        cur.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ? LIMIT ? OFFSET ?", (like, like, per_page, offset))
    else:
        cur.execute("SELECT COUNT(*) FROM products")
        total = cur.fetchone()[0]
        cur.execute("SELECT * FROM products LIMIT ? OFFSET ?", (per_page, offset))
    items = cur.fetchall()
    total_pages = (total + per_page - 1) // per_page
    return render_template("products.html", products=items, q=q, page=page, total_pages=total_pages)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# login/register pages
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if verify_user(username, password):
            session["username"] = username
            session.setdefault("cart", {})  # ensure cart exists
            return redirect(url_for("index"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng", "danger")
            # Store flag to auto-open login modal
            session["_open_login_modal"] = True
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        email = request.form.get("email", "").strip()
        fullname = request.form.get("fullname", "").strip()
        confirm_password = request.form.get("confirm_password", "")
        
        # Validation
        if not username or not password:
            flash("Vui lòng nhập đầy đủ thông tin", "warning")
            session["_open_register_modal"] = True
            return redirect(url_for("index"))
        
        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp", "warning")
            session["_open_register_modal"] = True
            return redirect(url_for("index"))
        
        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự", "warning")
            session["_open_register_modal"] = True
            return redirect(url_for("index"))
        
        # Create user with additional fields
        db = get_db()
        cur = db.cursor()
        try:
            password_hash = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password_hash, email, fullname) VALUES (?, ?, ?, ?)", 
                       (username, password_hash, email, fullname))
            db.commit()
            flash("Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.", "success")
            session["_open_register_modal"] = True
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            flash("Tên người dùng đã tồn tại", "danger")
            session["_open_register_modal"] = True
            return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    # keep cart or clear? we keep per-session cart but if user logs out, we clear to enforce login-to-buy rule
    session.pop("cart", None)
    return redirect(url_for("index"))

# API: list products JSON (for ajax or search)
@app.route("/api/products")
def api_products():
    q = request.args.get("q","").strip()
    db = get_db()
    cur = db.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ? LIMIT 200", (like, like))
    else:
        cur.execute("SELECT * FROM products LIMIT 200")
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)

# Add to cart (requires login)
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "username" not in session:
        return jsonify({"success": False, "error": "Bạn phải đăng nhập mới được thêm sản phẩm vào giỏ hàng.", "require_login": True}), 403
    data = request.json
    product_id = int(data.get("product_id"))
    qty = int(data.get("qty",1))
    # verify product exists
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if not cur.fetchone():
        return jsonify({"success": False, "error": "Sản phẩm không tồn tại"}), 400
    cart = session.setdefault("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    session["cart"] = cart
    return jsonify({"success": True, "cart": cart})

# Message page route
@app.route("/message")
def message():
    message_type = request.args.get('type', 'info')
    message_text = request.args.get('msg', 'Thông báo')
    return render_template("message.html", message_type=message_type, message=message_text)

@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    db = get_db()
    cur = db.cursor()
    items = []
    total = 0.0
    for pid_str, qty in cart.items():
        cur.execute("SELECT * FROM products WHERE id = ?", (int(pid_str),))
        p = cur.fetchone()
        if p:
            subtotal = p["price"] * qty
            total += subtotal
            items.append({"id": p["id"], "name": p["name"], "price": p["price"], "qty": qty, "image_url": p["image_url"], "subtotal": subtotal})
    return render_template("cart.html", items=items, total=total)

# Remove item from cart
@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    if "username" not in session:
        return jsonify({"success": False, "error": "Bạn phải đăng nhập"}), 403
    
    data = request.json
    product_id = str(data.get("product_id"))
    
    cart = session.get("cart", {})
    if product_id in cart:
        del cart[product_id]
        session["cart"] = cart
        return jsonify({"success": True, "message": "Đã xóa sản phẩm khỏi giỏ hàng"})
    else:
        return jsonify({"success": False, "error": "Sản phẩm không có trong giỏ hàng"}), 400

# simple checkout (mock)
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "username" not in session:
        flash("Bạn phải đăng nhập để thanh toán", "warning")
        return redirect(url_for("index"))
    
    if request.method == "GET":
        # Show checkout page with payment options
        cart = session.get("cart", {})
        if not cart:
            flash("Giỏ hàng trống", "info")
            return redirect(url_for("view_cart"))
        
        db = get_db()
        cur = db.cursor()
        items = []
        total = 0.0
        for pid_str, qty in cart.items():
            cur.execute("SELECT * FROM products WHERE id = ?", (int(pid_str),))
            p = cur.fetchone()
            if p:
                subtotal = p["price"] * qty
                total += subtotal
                items.append({"id": p["id"], "name": p["name"], "price": p["price"], "qty": qty, "image_url": p["image_url"], "subtotal": subtotal})
        return render_template("checkout.html", items=items, total=total)
    
    # POST: Process payment
    payment_method = request.form.get("payment_method")
    
    # Validate payment information
    if payment_method == "card":
        card_number = request.form.get("card_number")
        card_name = request.form.get("card_name")
        card_expiry = request.form.get("card_expiry")
        card_cvv = request.form.get("card_cvv")
        
        if not all([card_number, card_name, card_expiry, card_cvv]):
            flash("Vui lòng nhập đầy đủ thông tin thẻ", "warning")
            return redirect(url_for("checkout"))
    
    elif payment_method == "bank":
        bank_name = request.form.get("bank_name")
        account_number = request.form.get("account_number")
        account_holder = request.form.get("account_holder")
        
        if not all([bank_name, account_number, account_holder]):
            flash("Vui lòng nhập đầy đủ thông tin tài khoản ngân hàng", "warning")
            return redirect(url_for("checkout"))
    
    # For demo: clear cart and show success
    session.pop("cart", None)
    flash("Thanh toán thành công! Đơn hàng của bạn đang được xử lý.", "success")
    return redirect(url_for("index"))

# Run
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


