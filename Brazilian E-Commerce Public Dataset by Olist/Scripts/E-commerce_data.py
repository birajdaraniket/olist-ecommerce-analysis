import pandas as pd

# loading customers data
customers = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_customers_dataset.csv")
print(customers.head())
customers.info()  # checking structure

# loading geolocation (not used much but kept for understanding)
geolocation = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_geolocation_dataset.csv")
print(geolocation.head())
geolocation.info()

# loading order items
order_item = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_order_items_dataset.csv")
print(order_item.head())
order_item.info()

# checking if any negative freight values exist
neg_values = order_item[order_item["freight_value"] < 0]
print(len(neg_values))

# converting shipping date to datetime
order_item["shipping_limit_date"] = pd.to_datetime(order_item["shipping_limit_date"], errors="coerce", format="mixed")

# creating revenue column (price + freight)
order_item["revenue"] = order_item["price"] + order_item["freight_value"]
order_item.info()
print(order_item.tail())

# loading payments data
order_payments = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_order_payments_dataset.csv")
print(order_payments.head())
order_payments.info()

# checking negative payment values
print(len(order_payments[order_payments["payment_value"] < 0]))

# loading reviews data
order_reviews = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_order_reviews_dataset.csv")
print(order_reviews.head())
order_reviews.info()

# checking review text
print(order_reviews[["review_comment_title", "review_comment_message"]].head(10))

# filling missing review text
order_reviews["review_comment_title"] = order_reviews["review_comment_title"].fillna("no title")
order_reviews["review_comment_message"] = order_reviews["review_comment_message"].fillna("no messages")

# converting review dates
order_reviews["review_creation_date"] = pd.to_datetime(order_reviews["review_creation_date"], errors="coerce", format="mixed")
order_reviews["review_answer_timestamp"] = pd.to_datetime(order_reviews["review_answer_timestamp"], errors="coerce", format="mixed")

print(order_reviews[["review_comment_title", "review_comment_message"]].tail(10))
order_reviews.info()

# loading orders data
orders = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_orders_dataset.csv")
print(orders.head(7))
orders.info()

# checking datetime columns
print(orders["order_purchase_timestamp"])
print(orders["order_approved_at"])

# converting all date columns
orders["order_approved_at"] = pd.to_datetime(orders["order_approved_at"], errors="coerce")
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
orders["order_delivered_carrier_date"] = pd.to_datetime(orders["order_delivered_carrier_date"], errors="coerce")
orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"], errors="coerce")
orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"], errors="coerce")

# calculating delivery time in days
orders["delivery_time"] = (
    orders["order_delivered_customer_date"] - 
    orders["order_purchase_timestamp"]
).dt.days

# flag for delivered orders
orders["is_delivered"] = orders["order_delivered_customer_date"].notnull()

print(orders.tail(10))
orders.info()

# loading product data
products = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_products_dataset.csv")
print(products.head(10))
products.info()

# checking missing values in products
for col in products.columns:
    if products[col].isnull().sum() > 0:
        print(f"{col}, = {products[col].isnull().sum()} ")

# filling missing category
products["product_category_name"] = products["product_category_name"].fillna("no info found")
print(products.head(12))
products.info()

# loading sellers data
sellers = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\olist_sellers_dataset.csv")
print(sellers.head(10))
sellers.info()

# loading category translation
product_category_name_translation = pd.read_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Raw Dataset\product_category_name_translation.csv")
print(product_category_name_translation.head(10))
product_category_name_translation.info()

# quick check before merging
customers.info()
geolocation.info()
order_item.info()
order_payments.info()
order_reviews.info()
orders.info()
sellers.info()
products.info()

# grouping payments because one order can have multiple entries
payments_grouped = order_payments.groupby("order_id").agg({
    "payment_value": "sum",
    "payment_type": "first"
}).reset_index()

# merging all datasets step by step
df = orders.copy()
df = orders.merge(customers, on="customer_id", how="left")
df = df.merge(order_item, on="order_id", how="left")
df = df.merge(payments_grouped, on="order_id", how="left")
df = df.merge(sellers, on="seller_id", how="left")
df = df.merge(products, on="product_id", how="left")
df = df.merge(order_reviews, on="order_id", how="left")
df = df.merge(product_category_name_translation, on="product_category_name", how="left")

# checking merged data
df.info()
print(df.shape)
print(df["order_id"].nunique())

# removing duplicate rows
df = df.drop_duplicates()

# checking missing values after merge
print(df.isnull().sum().sort_values(ascending=False).head(40))

# starting analysis
print(df.columns)

# total revenue
print("Total revenue = ", df["revenue"].sum())

# top city and state by revenue
print(df.groupby("customer_city")["revenue"].sum().sort_values(ascending=False).head(1))
print(df.groupby("customer_state")["revenue"].sum().sort_values(ascending=False).head(1))

# revenue by payment type
print(df.groupby("payment_type")["revenue"].sum())

# creating delivery categories
df["delivery_type"] = df["delivery_time"].apply(
    lambda x: "Delivered in 5 days" if pd.notnull(x) and x<=5
    else "delivered in 5-10 days" if pd.notnull(x) and (x>5) & (x<=10)
    else "Delivered after more than 10 days"
)

# classifying reviews
df["review_score_status"] = df["review_score"].apply(
     lambda x: "good" if pd.notnull(x) and x >= 4
    else "Average" if pd.notnull(x) and x == 3
    else "poor"
)

# rating percentage
counts = df.groupby(["delivery_type", "review_score"]).size()
overall_percentage = counts / counts.sum() * 100
print(overall_percentage)

# category revenue analysis
print(df.groupby('product_category_name_english')['revenue'].sum().sort_values(ascending=False))

# checking seller distribution
sellers_state_count = df['seller_state'].nunique()

health_beauty_seller_states_count = df.groupby('product_category_name_english')['seller_state'].nunique()['health_beauty']
fashion_childrens_clothes_seller_state_count = df.groupby('product_category_name_english')['seller_state'].nunique()['fashion_childrens_clothes']

health_beauty_order_count = df.groupby("product_category_name_english")["order_id"].count()["health_beauty"]
fashion_children_clothes_order_count = df.groupby("product_category_name_english")["order_id"].count()["fashion_childrens_clothes"]

print(f"Low revenue category fashion_childrens_clothes has {fashion_children_clothes_order_count} orders across {fashion_childrens_clothes_seller_state_count} seller states,\n"
      f"while high revenue category health_beauty has {health_beauty_order_count} orders across {health_beauty_seller_states_count} seller states.\n"
      f"Total seller states = {sellers_state_count}")

print(df.groupby("product_category_name_english")["revenue"].mean().sort_values(ascending=False))

# creating useful columns
df["order_value"] = df["revenue"]

df["delivery_delay"] = (
    df["order_delivered_customer_date"] - 
    df["order_estimated_delivery_date"]
).dt.days

df["is_delayed"] = df["delivery_delay"] > 0

# checking repeat customers
customer_orders = df.groupby("customer_id")["order_id"].nunique()
df["is_repeat_customer"] = df["customer_id"].map(customer_orders) > 1

# seller level analysis
df.groupby("seller_id")["revenue"].sum()
df.groupby("seller_id")["order_id"].count()

# category level analysis
df.groupby("product_category_name_english")["revenue"].mean()
df.groupby("product_category_name_english")["order_id"].count()

# monthly trend
df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M")
df.groupby("order_month")["revenue"].sum()

# final dataset export
df.info()
df.to_csv(r"D:\Data Analyst\Brazilian E-Commerce Public Dataset by Olist\Cleaned master dataset\master_dataset_cleaned.csv")