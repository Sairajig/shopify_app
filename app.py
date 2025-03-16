import shopify
import pandas as pd
import json

# Shopify API Setup
def shopify_api_setup(api_key, password, shop_name):
    shopify.Session.setup(api_key=api_key, secret=password)
    session = shopify.Session(f"{shop_name}.myshopify.com", "2023-10", api_key)
    shopify.ShopifyResource.activate_session(session)

# Fetch Customer Data
def fetch_customers():
    customers = shopify.Customer.find()
    customer_data = []
    for customer in customers:
        customer_data.append({
            "name": customer.first_name + " " + customer.last_name,
            "email": customer.email,
            "orders_count": customer.orders_count
        })
    return customer_data

# Fetch Abandoned Cart Data
def fetch_abandoned_carts():
    carts = shopify.Checkout.find()
    cart_data = []
    for cart in carts:
        cart_data.append({
            "name": cart.customer.first_name + " " + cart.customer.last_name if cart.customer else "Unknown",
            "email": cart.email,
            "cart_value": sum(float(item.line_price) for item in cart.line_items)
        })
    return cart_data

# Data Processing
def process_data(customers, carts):
    processed_data = []
    email_to_cart = {cart["email"]: cart for cart in carts}

    for customer in customers:
        cart = email_to_cart.get(customer["email"], None)
        processed_entry = {
            "Customer Name": customer["name"],
            "Email": customer["email"],
            "Number of Orders": customer["orders_count"] if customer["orders_count"] > 0 else None,
            "Abandoned Cart Value": cart["cart_value"] if cart else None
        }
        processed_data.append(processed_entry)

    for cart in carts:
        if cart["email"] not in [customer["email"] for customer in customers]:
            processed_data.append({
                "Customer Name": cart["name"],
                "Email": cart["email"],
                "Number of Orders": None,
                "Abandoned Cart Value": cart["cart_value"]
            })

    return processed_data

# Export Processed Data to JSON and CSV
def export_data(processed_data):
    # Export to JSON
    with open("processed_data.json", "w") as json_file:
        json.dump(processed_data, json_file, indent=4)

    # Export to CSV
    df = pd.DataFrame(processed_data)
    df.to_csv("processed_data.csv", index=False)

# Process Uploaded CSV
def process_uploaded_csv(file_path):
    df = pd.read_csv(file_path)
    sorted_df = df.sort_values(by="Number of Orders", ascending=False)
    sorted_df.to_csv("sorted_uploaded_data.csv", index=False)
    print("Uploaded data sorted and saved to sorted_uploaded_data.csv")

if __name__ == "__main__":
    # Shopify API credentials
    API_KEY = "your_api_key"
    PASSWORD = "your_password"
    SHOP_NAME = "your_shop_name"

    # Setup Shopify API
    shopify_api_setup(API_KEY, PASSWORD, SHOP_NAME)

    # Fetch Data
    customers = fetch_customers()
    carts = fetch_abandoned_carts()

    # Process Data
    processed_data = process_data(customers, carts)

    # Export Data
    export_data(processed_data)

    # Process an uploaded CSV example
    # Uncomment the line below and specify the path to the uploaded CSV
    # process_uploaded_csv("uploaded_data.csv")
