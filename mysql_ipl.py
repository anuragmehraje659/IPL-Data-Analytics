
import pandas as pd
import mysql.connector


# 1. Read cleaned CSV
df = pd.read_csv(
    "archive/cleaned_IPL.csv",
    low_memory=False
)

# 2. Convert date
df["date"] = pd.to_datetime(df["date"])


# 3. MySQL connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Anuragmh@09",
    database="ipl_project"
)

cursor = connection.cursor()

print("MySQL connected successfully!")


# 4. Create table structure automatically
columns = []

for column, dtype in df.dtypes.items():

    if pd.api.types.is_integer_dtype(dtype):
        mysql_type = "BIGINT"

    elif pd.api.types.is_float_dtype(dtype):
        mysql_type = "DOUBLE"

    elif pd.api.types.is_bool_dtype(dtype):
        mysql_type = "BOOLEAN"

    elif pd.api.types.is_datetime64_any_dtype(dtype):
        mysql_type = "DATETIME"

    else:
        mysql_type = "TEXT"

    columns.append(f"`{column}` {mysql_type}")


create_table_query = f"""
CREATE TABLE IF NOT EXISTS ipl_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    {", ".join(columns)}
)
"""

cursor.execute(create_table_query)

print("Table created successfully!")


# 5. Insert data
column_names = list(df.columns)

columns_sql = ", ".join(f"`{col}`" for col in column_names)
placeholders = ", ".join(["%s"] * len(column_names))

insert_query = f"""
INSERT INTO ipl_data ({columns_sql})
VALUES ({placeholders})
"""


# 6. Insert in batches
batch_size = 2000

for start in range(0, len(df), batch_size):

    batch = df.iloc[start:start + batch_size]

    data = []

    for row in batch.itertuples(index=False, name=None):

        cleaned_row = []

        for value in row:

            if pd.isna(value):
                cleaned_row.append(None)
            elif isinstance(value, pd.Timestamp):
                cleaned_row.append(value.to_pydatetime())
            else:
                cleaned_row.append(value)

        data.append(tuple(cleaned_row))

    cursor.executemany(insert_query, data)
    connection.commit()

    print(
        f"Inserted {min(start + batch_size, len(df))} "
        f"/ {len(df)} rows"
    )


# 7. Close connection
cursor.close()
connection.close()

print("All data inserted successfully!")