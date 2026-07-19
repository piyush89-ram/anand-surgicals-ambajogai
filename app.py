from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import pandas as pd
import os
from urllib.parse import quote

app = Flask(__name__)
# Secure encryption key for keeping cart states preserved
app.secret_key = "anand_surgicals_2026"

EXCEL_FOLDER = "excel"


# -------------------------
# READ PRODUCTS ENGINE (ORIGINAL)
# -------------------------
def get_products(company):
    file_path = os.path.join(EXCEL_FOLDER, f"{company}.xlsx")

    if not os.path.exists(file_path):
        return []

    try:
        df = pd.read_excel(file_path)
        products = (
            df.iloc[7:, 0]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )
        # remove last row if unwanted
        if len(products) > 0:
            products.pop()
        return products
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


# -------------------------
# HOME PAGE
# -------------------------
@app.route('/')
def home():
    companies = []
    # Agar folder nahi hai toh auto create karein taaki crash na ho
    if os.path.exists(EXCEL_FOLDER):
        for file in os.listdir(EXCEL_FOLDER):
            if file.endswith(".xlsx"):
                companies.append(os.path.splitext(file)[0])
    
    companies.sort()
    
    # Counter badge tracks line rows rather than total product pieces sums
    cart_count = len(session.get("cart", []))

    return render_template(
        "index.html",
        companies=companies,
        cart_count=cart_count
    )


# -------------------------
# BRAND PAGE
# -------------------------
@app.route('/brand/<company>')
def brand(company):
    products = get_products(company)
    cart_count = len(session.get("cart", []))
    
    return render_template(
        "brand.html",
        brand=company.upper(),
        company=company,
        products=products,
        cart_count=cart_count  # Sent to sync navbar dynamic states
    )


# -------------------------
# GLOBAL SEARCH
# -------------------------
@app.route('/search')
def search():
    keyword = request.args.get("q", "").strip().lower()
    results = []

    if os.path.exists(EXCEL_FOLDER):
        for file in os.listdir(EXCEL_FOLDER):
            if not file.endswith(".xlsx"):
                continue

            company = os.path.splitext(file)[0]
            products = get_products(company)

            for product in products:
                if keyword in product.lower():
                    results.append({
                        "company": company.upper(),
                        "company_url": company,
                        "product": product
                    })

    return render_template(
        "search.html",
        keyword=keyword,
        products=results
    )


# -------------------------
# LIVE SEARCH API
# -------------------------
@app.route('/live_search')
def live_search():
    keyword = request.args.get("q", "").strip().lower()
    results = []

    if len(keyword) < 2:
        return jsonify([])

    if os.path.exists(EXCEL_FOLDER):
        for file in os.listdir(EXCEL_FOLDER):
            if not file.endswith(".xlsx"):
                continue

            company = os.path.splitext(file)[0]
            products = get_products(company)

            for product in products:
                if keyword in product.lower():
                    results.append({
                        "company": company.upper(),
                        "company_url": company,
                        "product": product
                    })

                    if len(results) >= 15:
                        return jsonify(results)

    return jsonify(results)


# -------------------------
# ADD TO CART (AJAX OPTIMIZED - NO JUMP / NO REDIRECT)
# -------------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product = request.form.get("product")
    company = request.form.get("company")
    qty = request.form.get("qty", "1")
    unit = request.form.get("unit", "Pieces")

    if "cart" not in session:
        session["cart"] = []

    cart_list = list(session["cart"])

    cart_list.append({
        "company": company,
        "product": product,
        "qty": qty,
        "unit": unit
    })

    session["cart"] = cart_list
    session.modified = True

    # Return HTTP 200 OK text response instead of forceful page reload redirect
    return "SUCCESS", 200


# -------------------------
# CART PAGE
# -------------------------
@app.route('/cart')
def cart():
    cart_items = session.get("cart", [])
    return render_template(
        "cart.html",
        cart_items=cart_items
    )


# -------------------------
# REMOVE ITEM (FIXED 404 AND BACKWARD COMPATIBLE)
# -------------------------
@app.route('/remove/<int:index>', methods=['GET'])
@app.route('/remove_item/<int:index>', methods=['GET'])
def remove_item(index):
    cart_list = session.get("cart", [])

    if 0 <= index < len(cart_list):
        cart_list = list(cart_list)
        cart_list.pop(index)
        session["cart"] = cart_list
        session.modified = True

    return redirect(url_for('cart'))


# -------------------------
# CLEAR CART
# -------------------------
@app.route('/clear_cart')
def clear_cart():
    session["cart"] = []
    return redirect(url_for('cart'))


# -------------------------
# SEND WHATSAPP ORDER
# -------------------------
@app.route('/send_order', methods=['POST'])
def send_order():
    customer = request.form.get("customer_name")
    mobile = request.form.get("mobile")
    city = request.form.get("city")

    cart_items = session.get("cart", [])

    if len(cart_items) == 0:
        return redirect(url_for('cart'))

    message = f"*ANAND SURGICALS ORDER*\n\n"
    message += f"Customer : {customer}\n"
    message += f"Mobile : {mobile}\n"
    message += f"City : {city}\n\n"
    message += f"Products:\n\n"

    for item in cart_items:
        message += f"🏢 Company : {item['company'].upper()}\n"
        message += f"📦 Product : {item['product']}\n"
        message += f"🔢 Qty : {item['qty']}\n"
        message += f"📦 Unit : {item['unit']}\n\n"

    whatsapp_number = "919420192170"
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={quote(message)}"

    # Order finish hone par cart automatically empty active karein
    session["cart"] = []

    return redirect(whatsapp_url)


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)