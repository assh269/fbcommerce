import asyncio
import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, init_db
from app.models import Seller, Category, Product, ProductImage


CATEGORIES = [
    {"name": "Men's Casual Wear", "description": "T-shirts, shirts, jeans, shorts, and everyday essentials for men"},
    {"name": "Men's Traditional Wear", "description": "Longyi, Taipon, traditional jackets for men"},
    {"name": "Men's Streetwear & Sportswear", "description": "Oversized tees, hoodies, joggers, sportswear"},
    {"name": "Men's Accessories", "description": "Watches, sunglasses, hats, belts, and wallets for men"},
    {"name": "Women's Casual Wear", "description": "Tops, blouses, jeans, skirts, and everyday fashion for women"},
    {"name": "Women's Dresses & Skirts", "description": "Dresses, jumpsuits, skirts for all occasions"},
    {"name": "Women's Traditional Wear", "description": "Htamein, Yinkhae, Sarong, and traditional accessories"},
    {"name": "Women's Streetwear & Sportswear", "description": "Oversized tees, hoodies, joggers, athleisure for women"},
    {"name": "Women's Beauty & Skincare", "description": "Skincare, makeup, beauty tools and products"},
    {"name": "Women's Accessories & Jewelry", "description": "Necklaces, earrings, bracelets, hair accessories, scarves"},
    {"name": "Footwear", "description": "Sneakers, sandals, flats, heels, and casual shoes"},
    {"name": "Bags & Backpacks", "description": "Tote bags, backpacks, crossbody bags, and handbags"},
    {"name": "Tech Accessories", "description": "Phone cases, earphones, chargers, smart gadgets"},
]

PRODUCTS = [
    # === FEMALE 16-22 (20 products) ===
    {
        "name": "K-Fashion Oversized Striped Tee",
        "description": "Trending Korean-style oversized striped t-shirt. Perfect for casual outings in Yangon. Pair with jeans or shorts for a chic look.",
        "price": 15000, "gender": "female", "target_age": "16-22", "stock": 45, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Crop Top with Puff Sleeves",
        "description": "Stylish puff sleeve crop top, very popular among Yangon youth. Lightweight fabric perfect for Myanmar weather.",
        "price": 12000, "gender": "female", "target_age": "16-22", "stock": 60, "category_name": "Women's Casual Wear",
    },
    {
        "name": "High-Waist Denim Shorts",
        "description": "Trendy high-waist denim shorts with distressed details. A summer essential for young women in Yangon.",
        "price": 18000, "gender": "female", "target_age": "16-22", "stock": 35, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Baby Pink Cargo Pants",
        "description": "Soft pink cargo pants with side pockets. Korean fashion inspired, great for casual street style.",
        "price": 25000, "gender": "female", "target_age": "16-22", "stock": 30, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Satin Slip Dress",
        "description": "Elegant satin slip dress in pastel colors. Perfect for parties and date nights in Yangon.",
        "price": 32000, "gender": "female", "target_age": "16-22", "stock": 25, "category_name": "Women's Dresses & Skirts",
    },
    {
        "name": "Floral Midi Sundress",
        "description": "Lightweight floral print midi dress. Bestseller for Yangon summer. Adjustable straps and flowy fit.",
        "price": 28000, "gender": "female", "target_age": "16-22", "stock": 40, "category_name": "Women's Dresses & Skirts",
    },
    {
        "name": "Pleated Mini Skirt",
        "description": "Korean-style pleated mini skirt in multiple colors. A must-have for young women following K-fashion.",
        "price": 20000, "gender": "female", "target_age": "16-22", "stock": 55, "category_name": "Women's Dresses & Skirts",
    },
    {
        "name": "Two-Piece Knit Set",
        "description": "Matching knit top and skirt set. Trendy and comfortable, perfect for Yangon cafe hopping.",
        "price": 35000, "gender": "female", "target_age": "16-22", "stock": 20, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Oversized Hoodie with Print",
        "description": "Cozy oversized hoodie with cute graphic prints. Popular among Yangon teens and university students.",
        "price": 22000, "gender": "female", "target_age": "16-22", "stock": 50, "category_name": "Women's Streetwear & Sportswear",
    },
    {
        "name": "Platform Sneakers White",
        "description": "Chunky white platform sneakers. The ultimate K-fashion footwear trend in Yangon right now.",
        "price": 45000, "gender": "female", "target_age": "16-22", "stock": 30, "category_name": "Footwear",
    },
    {
        "name": "Mini Crossbody Bag",
        "description": "Cute mini crossbody bag in pastel colors. Fits phone and essentials. Popular among Yangon youth.",
        "price": 18000, "gender": "female", "target_age": "16-22", "stock": 40, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Heart-Shaped Sunglasses",
        "description": "Trendy heart-shaped sunglasses with UV protection. Perfect Instagram accessory.",
        "price": 8000, "gender": "female", "target_age": "16-22", "stock": 65, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Layered Chain Necklace Set",
        "description": "Gold-tone layered chain necklace set. Minimalist Korean jewelry trend.",
        "price": 10000, "gender": "female", "target_age": "16-22", "stock": 70, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Scrunchie Hair Set (10pcs)",
        "description": "Assorted velvet and silk scrunchies. Essential hair accessory for young women.",
        "price": 5000, "gender": "female", "target_age": "16-22", "stock": 100, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Acne Patch Pack",
        "description": "Hydrocolloid acne patches in cute shapes. Popular skincare essential for teens.",
        "price": 6000, "gender": "female", "target_age": "16-22", "stock": 80, "category_name": "Women's Beauty & Skincare",
    },
    {
        "name": "Tinted Lip Balm Set",
        "description": "Set of 3 tinted lip balms in trendy shades. Natural look popular among Yangon youth.",
        "price": 12000, "gender": "female", "target_age": "16-22", "stock": 60, "category_name": "Women's Beauty & Skincare",
    },
    {
        "name": "Cute Phone Grip Holder",
        "description": "Kawaii-style phone grip holder with stand. Fun accessory for young women.",
        "price": 7000, "gender": "female", "target_age": "16-22", "stock": 90, "category_name": "Tech Accessories",
    },
    {
        "name": "Hoop Earrings Set (3 pairs)",
        "description": "Gold and silver hoop earrings set. Classic everyday jewelry for young women.",
        "price": 9000, "gender": "female", "target_age": "16-22", "stock": 75, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Tote Bag with Canvas Print",
        "description": "Large canvas tote bag with trendy print. Reusable and stylish, popular for uni students.",
        "price": 15000, "gender": "female", "target_age": "16-22", "stock": 45, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Eye Shadow Palette (9 colors)",
        "description": "Korean-brand inspired 9-color eyeshadow palette with warm tones. Bestseller.",
        "price": 25000, "gender": "female", "target_age": "16-22", "stock": 35, "category_name": "Women's Beauty & Skincare",
    },

    # === FEMALE 22-30 (17 products) ===
    {
        "name": "Office Blouse with Tie Neck",
        "description": "Elegant blouse with tie neck detail. Perfect for office wear in Yangon.",
        "price": 22000, "gender": "female", "target_age": "22-30", "stock": 30, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Tailored Trousers High-Waist",
        "description": "High-waist tailored trousers in neutral colors. Essential for the modern Yangon working woman.",
        "price": 30000, "gender": "female", "target_age": "22-30", "stock": 25, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Midi Wrap Dress",
        "description": "Flattering wrap dress in midi length. Suitable for office and evening events.",
        "price": 38000, "gender": "female", "target_age": "22-30", "stock": 20, "category_name": "Women's Dresses & Skirts",
    },
    {
        "name": "Knitted Cardigan Long",
        "description": "Long open-front knitted cardigan. Perfect for air-conditioned offices in Yangon.",
        "price": 28000, "gender": "female", "target_age": "22-30", "stock": 35, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Silk Scarf Square",
        "description": "Luxurious silk scarf with elegant pattern. Versatile accessory for the professional woman.",
        "price": 18000, "gender": "female", "target_age": "22-30", "stock": 40, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Leather Tote Bag Medium",
        "description": "Genuine leather tote bag in black and brown. Everyday bag for working women.",
        "price": 65000, "gender": "female", "target_age": "22-30", "stock": 15, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Pointed Flats Ballet",
        "description": "Comfortable pointed ballet flats with cushion sole. Office-friendly footwear.",
        "price": 25000, "gender": "female", "target_age": "22-30", "stock": 30, "category_name": "Footwear",
    },
    {
        "name": "BB Cream SPF 50",
        "description": "Lightweight BB cream with high SPF. Daily essential for Yangon's sunny weather.",
        "price": 20000, "gender": "female", "target_age": "22-30", "stock": 50, "category_name": "Women's Beauty & Skincare",
    },
    {
        "name": "Waterproof Eyeliner Pen",
        "description": "Long-lasting waterproof eyeliner pen. Myanmar heat-proof makeup essential.",
        "price": 12000, "gender": "female", "target_age": "22-30", "stock": 60, "category_name": "Women's Beauty & Skincare",
    },
    {
        "name": "Minimalist Watch Women",
        "description": "Elegant minimalist watch with mesh strap. Affordable luxury accessory.",
        "price": 35000, "gender": "female", "target_age": "22-30", "stock": 25, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Blazer Structured Fit",
        "description": "Well-tailored blazer for women. Essential for professional occasions.",
        "price": 55000, "gender": "female", "target_age": "22-30", "stock": 15, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Backpack Laptop 15.6",
        "description": "Stylish laptop backpack with padded compartment. Perfect for work and travel.",
        "price": 40000, "gender": "female", "target_age": "22-30", "stock": 20, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Face Serum Vitamin C",
        "description": "Brightening vitamin C serum. Popular skincare product among Yangon women.",
        "price": 22000, "gender": "female", "target_age": "22-30", "stock": 40, "category_name": "Women's Beauty & Skincare",
    },
    {
        "name": "Bamboo Sun Hat Wide Brim",
        "description": "Wide brim bamboo sun hat. Stylish sun protection for Yangon summer.",
        "price": 15000, "gender": "female", "target_age": "22-30", "stock": 35, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Denim Jacket Classic",
        "description": "Classic denim jacket, slightly oversized. Timeless layering piece.",
        "price": 35000, "gender": "female", "target_age": "22-30", "stock": 20, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Strappy Sandals Block Heel",
        "description": "Block heel strappy sandals. Perfect for evenings out in Yangon.",
        "price": 30000, "gender": "female", "target_age": "22-30", "stock": 25, "category_name": "Footwear",
    },
    {
        "name": "Wireless Bluetooth Earbuds",
        "description": "Quality wireless earbuds with noise isolation. For music lovers on the go.",
        "price": 35000, "gender": "female", "target_age": "22-30", "stock": 30, "category_name": "Tech Accessories",
    },

    # === FEMALE 31-40 (8 products) ===
    {
        "name": "Htamein Silk Premium",
        "description": "High-quality silk htamein with traditional Myanmar patterns. Perfect for special occasions and festivals.",
        "price": 80000, "gender": "female", "target_age": "31-40", "stock": 15, "category_name": "Women's Traditional Wear",
    },
    {
        "name": "Elastic Waist Palazzo Pants",
        "description": "Comfortable palazzo pants with elastic waist. Stylish and practical for everyday wear.",
        "price": 25000, "gender": "female", "target_age": "31-40", "stock": 30, "category_name": "Women's Casual Wear",
    },
    {
        "name": "Gold Plated Earrings Set",
        "description": "Elegant gold-plated earring set with jade accents. Traditional meets modern design.",
        "price": 45000, "gender": "female", "target_age": "31-40", "stock": 20, "category_name": "Women's Accessories & Jewelry",
    },
    {
        "name": "Anti-Aging Night Cream",
        "description": "Premium anti-aging night cream with collagen. Advanced skincare for mature skin.",
        "price": 35000, "gender": "female", "target_age": "31-40", "stock": 25, "category_name": "Women's Beauty & Skincare",
    },
    {
        "name": "A-Line Midi Dress",
        "description": "Flattering A-line midi dress with V-neck. Elegant and age-appropriate design.",
        "price": 42000, "gender": "female", "target_age": "31-40", "stock": 20, "category_name": "Women's Dresses & Skirts",
    },
    {
        "name": "Comfortable Wedge Sandals",
        "description": "Stylish wedge sandals with arch support. Comfortable for long days out.",
        "price": 32000, "gender": "female", "target_age": "31-40", "stock": 25, "category_name": "Footwear",
    },
    {
        "name": "Crossbody Bag Leather",
        "description": "Genuine leather crossbody bag with multiple compartments. Everyday luxury.",
        "price": 70000, "gender": "female", "target_age": "31-40", "stock": 12, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Yinkhae Traditional Top",
        "description": "Beautiful Yinkhae traditional top with embroidery. For cultural events and ceremonies.",
        "price": 55000, "gender": "female", "target_age": "31-40", "stock": 18, "category_name": "Women's Traditional Wear",
    },

    # === MALE 16-22 (17 products) ===
    {
        "name": "Oversized Graphic T-Shirt",
        "description": "Trendy oversized t-shirt with bold graphic prints. Inspired by K-pop and street culture.",
        "price": 15000, "gender": "male", "target_age": "16-22", "stock": 50, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Cargo Pants Multi-Pocket",
        "description": "Street-style cargo pants with multiple pockets. Loose fit, very popular in Yangon.",
        "price": 25000, "gender": "male", "target_age": "16-22", "stock": 35, "category_name": "Men's Streetwear & Sportswear",
    },
    {
        "name": "Hoodie Pullover Solid Color",
        "description": "Essential pullover hoodie in solid colors. Wardrobe staple for young men.",
        "price": 22000, "gender": "male", "target_age": "16-22", "stock": 40, "category_name": "Men's Streetwear & Sportswear",
    },
    {
        "name": "Sports Jersey Basketball",
        "description": "Breathable basketball jersey with modern design. For sports and casual wear.",
        "price": 20000, "gender": "male", "target_age": "16-22", "stock": 30, "category_name": "Men's Streetwear & Sportswear",
    },
    {
        "name": "Joggers Cuffed Sweatpants",
        "description": "Comfortable cuffed joggers with drawstring waist. Perfect for lounging and sports.",
        "price": 18000, "gender": "male", "target_age": "16-22", "stock": 45, "category_name": "Men's Streetwear & Sportswear",
    },
    {
        "name": "Sneakers High Top White",
        "description": "Classic white high-top sneakers. Versatile footwear for any casual outfit.",
        "price": 40000, "gender": "male", "target_age": "16-22", "stock": 30, "category_name": "Footwear",
    },
    {
        "name": "Baseball Cap Embroidered",
        "description": "Trendy embroidered baseball cap with adjustable strap. Sun protection and style.",
        "price": 10000, "gender": "male", "target_age": "16-22", "stock": 60, "category_name": "Men's Accessories",
    },
    {
        "name": "Backpack Urban Style",
        "description": "Sleek urban backpack with laptop compartment. Perfect for school and daily use.",
        "price": 30000, "gender": "male", "target_age": "16-22", "stock": 25, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Digital Watch Sport",
        "description": "Sporty digital watch with LED display and stopwatch. Affordable and functional.",
        "price": 15000, "gender": "male", "target_age": "16-22", "stock": 40, "category_name": "Men's Accessories",
    },
    {
        "name": "Phone Case Shockproof",
        "description": "Durable shockproof phone case with ring holder. Available for all models.",
        "price": 8000, "gender": "male", "target_age": "16-22", "stock": 80, "category_name": "Tech Accessories",
    },
    {
        "name": "Denim Jacket Oversized",
        "description": "Oversized denim jacket with vintage wash. Cool streetwear layer.",
        "price": 32000, "gender": "male", "target_age": "16-22", "stock": 20, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Chain Necklace Silver Tone",
        "description": "Silver-tone chain necklace. Hip-hop inspired accessory for young men.",
        "price": 12000, "gender": "male", "target_age": "16-22", "stock": 50, "category_name": "Men's Accessories",
    },
    {
        "name": "Slides Sandals Comfort",
        "description": "Comfortable slide sandals with cushioned sole. Easy summer footwear.",
        "price": 12000, "gender": "male", "target_age": "16-22", "stock": 55, "category_name": "Footwear",
    },
    {
        "name": "Bucket Hat Reversible",
        "description": "Reversible bucket hat in two colors. K-fashion trend accessory.",
        "price": 10000, "gender": "male", "target_age": "16-22", "stock": 40, "category_name": "Men's Accessories",
    },
    {
        "name": "Short Sleeve Button Up",
        "description": "Casual short sleeve button-up shirt with fun patterns. Summer vacation essential.",
        "price": 20000, "gender": "male", "target_age": "16-22", "stock": 30, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Wireless Earbuds Budget",
        "description": "Affordable wireless earbuds with charging case. Great sound quality for the price.",
        "price": 20000, "gender": "male", "target_age": "16-22", "stock": 50, "category_name": "Tech Accessories",
    },
    {
        "name": "Tracksuit Set Two-Piece",
        "description": "Matching tracksuit set with jacket and pants. Athleisure trend at its best.",
        "price": 45000, "gender": "male", "target_age": "16-22", "stock": 20, "category_name": "Men's Streetwear & Sportswear",
    },

    # === MALE 22-30 (13 products) ===
    {
        "name": "Formal Shirt Slim Fit",
        "description": "Crisp slim-fit formal shirt in white and light blue. Office essential for men.",
        "price": 25000, "gender": "male", "target_age": "22-30", "stock": 35, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Chinos Pants Slim",
        "description": "Smart slim-fit chinos in neutral colors. Versatile for office and casual.",
        "price": 28000, "gender": "male", "target_age": "22-30", "stock": 30, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Longyi Casual Premium Cotton",
        "description": "High-quality cotton longyi in classic patterns. Comfortable traditional wear.",
        "price": 20000, "gender": "male", "target_age": "22-30", "stock": 40, "category_name": "Men's Traditional Wear",
    },
    {
        "name": "Leather Belt Dress",
        "description": "Genuine leather dress belt with brushed buckle. Essential accessory for office.",
        "price": 18000, "gender": "male", "target_age": "22-30", "stock": 45, "category_name": "Men's Accessories",
    },
    {
        "name": "Loafers Leather Brown",
        "description": "Brown leather loafers with rubber sole. Smart casual footwear.",
        "price": 45000, "gender": "male", "target_age": "22-30", "stock": 20, "category_name": "Footwear",
    },
    {
        "name": "Messenger Bag Canvas",
        "description": "Canvas messenger bag with multiple pockets. Perfect for work commute.",
        "price": 28000, "gender": "male", "target_age": "22-30", "stock": 25, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Classic Watch Analog",
        "description": "Minimalist analog watch with leather strap. Timeless professional accessory.",
        "price": 55000, "gender": "male", "target_age": "22-30", "stock": 18, "category_name": "Men's Accessories",
    },
    {
        "name": "Polo T-Shirt Premium",
        "description": "Premium pique cotton polo shirt. Smart casual essential for young professionals.",
        "price": 25000, "gender": "male", "target_age": "22-30", "stock": 35, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Sunglasses Aviator",
        "description": "Classic aviator sunglasses with UV400 protection. Timeless style.",
        "price": 20000, "gender": "male", "target_age": "22-30", "stock": 30, "category_name": "Men's Accessories",
    },
    {
        "name": "Laptop Backpack Anti-Theft",
        "description": "Anti-theft laptop backpack with USB charging. Safe and convenient for travel.",
        "price": 40000, "gender": "male", "target_age": "22-30", "stock": 20, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Oxford Shoes Formal",
        "description": "Classic oxford formal shoes in black. Essential for special occasions and office.",
        "price": 60000, "gender": "male", "target_age": "22-30", "stock": 15, "category_name": "Footwear",
    },
    {
        "name": "Grooming Kit Travel",
        "description": "Travel grooming kit with razor, comb, nail clipper, and case.",
        "price": 15000, "gender": "male", "target_age": "22-30", "stock": 40, "category_name": "Men's Accessories",
    },
    {
        "name": "Smart Watch Fitness Tracker",
        "description": "Fitness tracker smart watch with heart rate monitor and step counter.",
        "price": 50000, "gender": "male", "target_age": "22-30", "stock": 25, "category_name": "Tech Accessories",
    },

    # === MALE 31-40 (7 products) ===
    {
        "name": "Longyi Silk Traditional Pattern",
        "description": "Premium silk longyi with traditional Myanmar patterns. For formal occasions and festivals.",
        "price": 60000, "gender": "male", "target_age": "31-40", "stock": 15, "category_name": "Men's Traditional Wear",
    },
    {
        "name": "Business Shirt Premium Cotton",
        "description": "High-quality 100% cotton business shirt. Non-iron fabric for easy care.",
        "price": 35000, "gender": "male", "target_age": "31-40", "stock": 25, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Formal Trousers Wool Blend",
        "description": "Wool blend formal trousers with classic cut. For professional occasions.",
        "price": 50000, "gender": "male", "target_age": "31-40", "stock": 15, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Leather Wallet Bifold",
        "description": "Genuine leather bifold wallet with RFID protection. Premium everyday essential.",
        "price": 35000, "gender": "male", "target_age": "31-40", "stock": 25, "category_name": "Men's Accessories",
    },
    {
        "name": "Dress Shoes Lace-Up",
        "description": "Premium lace-up dress shoes in genuine leather. For formal events and office.",
        "price": 75000, "gender": "male", "target_age": "31-40", "stock": 12, "category_name": "Footwear",
    },
    {
        "name": "Taipon Traditional Jacket",
        "description": "Elegant Taipon traditional jacket with mandarin collar. For weddings and ceremonies.",
        "price": 70000, "gender": "male", "target_age": "31-40", "stock": 10, "category_name": "Men's Traditional Wear",
    },
    {
        "name": "Briefcase Leather Executive",
        "description": "Professional leather briefcase with combination lock. For the modern executive.",
        "price": 90000, "gender": "male", "target_age": "31-40", "stock": 8, "category_name": "Bags & Backpacks",
    },

    # === UNISEX / ALL AGES (18 products) ===
    {
        "name": "Plain White T-Shirt Essential",
        "description": "High-quality plain white t-shirt. Wardrobe essential for everyone. Multiple sizes available.",
        "price": 10000, "gender": "unisex", "target_age": "16-22", "stock": 100, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Plain White T-Shirt Premium",
        "description": "Premium quality plain white tee. Heavy weight cotton. Perfect for all ages and genders.",
        "price": 15000, "gender": "unisex", "target_age": "22-30", "stock": 80, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Plain White T-Shirt Classic",
        "description": "Classic crew neck white t-shirt. Comfortable fit. Suitable for men and women.",
        "price": 18000, "gender": "unisex", "target_age": "31-40", "stock": 60, "category_name": "Men's Casual Wear",
    },
    {
        "name": "Black Backpack Classic",
        "description": "Classic black backpack with padded straps. Fits laptop and books. For school, work, travel.",
        "price": 25000, "gender": "unisex", "target_age": "16-22", "stock": 50, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Canvas Sneakers Low Top",
        "description": "Classic low-top canvas sneakers. Available in black and white. Timeless casual footwear.",
        "price": 20000, "gender": "unisex", "target_age": "16-22", "stock": 60, "category_name": "Footwear",
    },
    {
        "name": "Cotton Face Mask Reusable",
        "description": "Reusable cotton face mask with filter pocket. Various colors. Essential daily item.",
        "price": 3000, "gender": "unisex", "target_age": "16-22", "stock": 150, "category_name": "Women's Beauty & Skincare",
    },
    {
        "name": "Cap Adjustable Plain",
        "description": "Simple adjustable plain cap in multiple colors. Unisex design for sun protection.",
        "price": 8000, "gender": "unisex", "target_age": "22-30", "stock": 70, "category_name": "Men's Accessories",
    },
    {
        "name": "Sunglasses Classic Wayfarer",
        "description": "Classic wayfarer sunglasses with UV protection. Timeless unisex accessory.",
        "price": 15000, "gender": "unisex", "target_age": "22-30", "stock": 45, "category_name": "Men's Accessories",
    },
    {
        "name": "Phone Stand Foldable",
        "description": "Foldable phone stand for desk use. Compatible with all phones and tablets.",
        "price": 5000, "gender": "unisex", "target_age": "22-30", "stock": 100, "category_name": "Tech Accessories",
    },
    {
        "name": "Socks Ankle Set 5 Pairs",
        "description": "Comfortable ankle socks set. Unisex design. Essential for daily wear.",
        "price": 6000, "gender": "unisex", "target_age": "16-22", "stock": 120, "category_name": "Footwear",
    },
    {
        "name": "Water Bottle Stainless Steel",
        "description": "Insulated stainless steel water bottle. Keeps drinks cold for 24 hours.",
        "price": 18000, "gender": "unisex", "target_age": "31-40", "stock": 40, "category_name": "Tech Accessories",
    },
    {
        "name": "Power Bank 10000mAh",
        "description": "Compact 10000mAh power bank with fast charging. Essential for mobile life.",
        "price": 25000, "gender": "unisex", "target_age": "22-30", "stock": 35, "category_name": "Tech Accessories",
    },
    {
        "name": "Towel Microfiber Travel",
        "description": "Quick-dry microfiber travel towel. Compact and lightweight. Perfect for travel and gym.",
        "price": 12000, "gender": "unisex", "target_age": "31-40", "stock": 50, "category_name": "Men's Streetwear & Sportswear",
    },
    {
        "name": "Notebook Journal Leather",
        "description": "Premium leather journal with lined paper. A5 size. For notes and journaling.",
        "price": 15000, "gender": "unisex", "target_age": "22-30", "stock": 45, "category_name": "Men's Accessories",
    },
    {
        "name": "Umbrella Compact Automatic",
        "description": "Automatic compact umbrella with windproof frame. Essential for Yangon rainy season.",
        "price": 10000, "gender": "unisex", "target_age": "31-40", "stock": 60, "category_name": "Men's Accessories",
    },
    {
        "name": "Tote Bag Reusable Shopping",
        "description": "Foldable reusable shopping tote bag. Eco-friendly and practical.",
        "price": 4000, "gender": "unisex", "target_age": "16-22", "stock": 100, "category_name": "Bags & Backpacks",
    },
    {
        "name": "Cushion Insole Gel",
        "description": "Gel cushion insoles for all shoe types. Comfort for long days standing.",
        "price": 7000, "gender": "unisex", "target_age": "31-40", "stock": 80, "category_name": "Footwear",
    },
    {
        "name": "Multi-USB Charger Cable",
        "description": "3-in-1 charging cable with Micro USB, USB-C, and Lightning. Braided nylon.",
        "price": 8000, "gender": "unisex", "target_age": "16-22", "stock": 90, "category_name": "Tech Accessories",
    },
]


async def seed():
    await init_db()
    async with async_session() as session:
        existing = await session.execute(select(Category))
        if existing.scalars().first():
            print("Database already has data. Drop tables or remove db file first.")
            return

        cat_map = {}
        for c in CATEGORIES:
            cat = Category(id=uuid.uuid4(), name=c["name"], description=c["description"])
            session.add(cat)
            cat_map[c["name"]] = cat

        seller = Seller(
            id=uuid.uuid4(),
            telegram_id=123456789,
            username="yangon_trends",
            business_name="Yangon Trend Shop",
            phone="+95-9-123456789",
            description="Your #1 source for the latest fashion trends in Yangon. We bring you K-fashion, streetwear, traditional wear, and accessories for all ages and genders.",
        )
        session.add(seller)
        await session.flush()

        for i, p in enumerate(PRODUCTS):
            cat = cat_map[p["category_name"]]
            product = Product(
                seller_id=seller.id,
                category_id=cat.id,
                name=p["name"],
                description=p["description"],
                price=p["price"],
                stock=p["stock"],
                gender=p["gender"],
                target_age=p["target_age"],
            )
            session.add(product)

        await session.commit()
        print(f"Seeded {len(CATEGORIES)} categories, 1 seller, and {len(PRODUCTS)} products!")


if __name__ == "__main__":
    asyncio.run(seed())
