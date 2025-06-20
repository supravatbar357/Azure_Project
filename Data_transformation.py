# Databricks notebook source
spark

# COMMAND ----------

# MAGIC %md
# MAGIC ## **Configure connection with ADLS gen 2**

# COMMAND ----------

storage_account = "olistdatastorageversion0"
application_id = "1bb1871d-eb5c-4a5a-821e-40b02f9d6d34"
directory_id = "560c3a90-e1a2-403e-9678-f00a3b6778c9"

spark.conf.set(f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net", "OAuth")
spark.conf.set(f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
spark.conf.set(f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net", application_id)
spark.conf.set(f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net", "qXX8Q~CGnfrbASbDaD2eiltEghKNNYEzaMt1rayl")
spark.conf.set(f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net", f"https://login.microsoftonline.com/{directory_id}/oauth2/token")

# COMMAND ----------

# MAGIC %md
# MAGIC # **Reading the Data**

# COMMAND ----------

base_path = "abfss://olistdata@olistdatastorageversion0.dfs.core.windows.net/bronze/"
orders_path = base_path + "olist_orders_dataset.csv"
payments_path = base_path + "olist_order_payments_dataset.csv"
reviews_path = base_path + "olist_order_reviews_dataset.csv"
items_path = base_path + "olist_order_items_dataset.csv"
customers_path = base_path + "olist_customers_dataset.csv"
sellers_path = base_path + "olist_sellers_dataset.csv"
geolocation_path = base_path + "olist_geolocation_dataset.csv"
products_path = base_path + "olist_products_dataset.csv"


orders_df = spark.read.format("csv").option("header", "true").load(orders_path)
payments_df = spark.read.format("csv").option("header", "true").load(payments_path)
reviews_df = spark.read.format("csv").option("header", "true").load(reviews_path)
items_df = spark.read.format("csv").option("header", "true").load(items_path)
customers_df = spark.read.format("csv").option("header", "true").load(customers_path)
sellers_df = spark.read.format("csv").option("header", "true").load(sellers_path)
geolocation_df = spark.read.format("csv").option("header", "true").load(geolocation_path)
products_df = spark.read.format("csv").option("header", "true").load(products_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ## **Reading data from Pymongo**

# COMMAND ----------

from pymongo import MongoClient


# COMMAND ----------

# importing module
from pymongo import MongoClient

hostname = "rgvyc.h.filess.io"
database = "olistdataNosql_differwent"
port = "27018"
username = "olistdataNosql_differwent"
password = "c1574cab2b1089fe32b0430582ac45e609e98067"

uri = "mongodb://" + username + ":" + password + "@" + hostname + ":" + port + "/" + database

# Connect with the portnumber and host
client = MongoClient(uri)

# Access database
mydatabase = client[database]


# COMMAND ----------

import pandas as pd
collection = mydatabase['product_categories']

mongo_data = pd.DataFrame(list(collection.find()))

# COMMAND ----------

mongo_data.head()

# COMMAND ----------

display(products_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## **Cleaning the data**

# COMMAND ----------

from pyspark.sql.functions import col,to_date,datediff,current_date,when

# COMMAND ----------

def clean_datafram(df,name):
    print("Cleaning "+name)
    return df.dropDuplicates().na.drop('all')

orders_df = clean_datafram(orders_df,"Orders")
display(orders_df)

# COMMAND ----------

# convert Date Colums

orders_df = orders_df.withColumn("order_purchase_timestamp", to_date(col("order_purchase_timestamp")))\
    .withColumn("order_delivered_customer_date", to_date(col("order_delivered_customer_date")))\
        .withColumn("order_estimated_delivery_date", to_date(col("order_estimated_delivery_date")))

# COMMAND ----------

# Calculate Delivery and Time Delays

orders_df = orders_df.withColumn("actual_delivery_time", datediff("order_delivered_customer_date", "order_purchase_timestamp"))
orders_df = orders_df.withColumn("estimated_delivery_time", datediff("order_estimated_delivery_date", "order_purchase_timestamp"))
orders_df =orders_df.withColumn("Delay Time", col("actual_delivery_time") - col("estimated_delivery_time"))

display(orders_df)

# COMMAND ----------

display(orders_df.tail(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## **Joining the datasets**

# COMMAND ----------

orders_cutomers_df = orders_df.join(customers_df, orders_df.customer_id == customers_df.customer_id,"left")

orders_payments_df = orders_cutomers_df.join(payments_df, orders_cutomers_df.order_id == payments_df.order_id,"left")

orders_items_df = orders_payments_df.join(items_df,"order_id","left")

orders_items_products_df = orders_items_df.join(products_df, orders_items_df.product_id == products_df.product_id,"left")

final_df = orders_items_products_df.join(sellers_df, orders_items_products_df.seller_id == sellers_df.seller_id,"left")


# COMMAND ----------

display(final_df)

# COMMAND ----------

mongo_data.drop('_id',axis=1,inplace=True)

mongo_sparf_df = spark.createDataFrame(mongo_data)
display(mongo_sparf_df)

# COMMAND ----------

final_df = final_df.join(mongo_sparf_df,"product_category_name","left")

# COMMAND ----------

display(final_df)

# COMMAND ----------

def remove_duplicate_columns(df):
    columns = df.columns

    seen_columns = set()
    columns_to_drop = []

    for column in columns:
        if column in seen_columns:
            columns_to_drop.append(column)
        else:
            seen_columns.add(column)
    
    df_cleaned = df.drop(*columns_to_drop)
    return df_cleaned

final_df = remove_duplicate_columns(final_df)

# COMMAND ----------

final_df.write.mode("overwrite").parquet("abfss://olistdata@olistdatastorageversion0.dfs.core.windows.net/silver")