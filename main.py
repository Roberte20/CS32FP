import pandas as pd
# help(pandas)

data = {'Company': ['Atmos', 'Bonafi', 'Cisco'],
        'Price': [45.89, 169.34, 22.94],
        'City': ['Dallas', 'Boston', 'Boston']}
df = pd.DataFrame(data)
print("\nDataFrame:")
print(df)

# Basic DataFrame 

print("\nDataframe statistics:")
print(df.describe())

# Selecting columns
print("\nSelecting 'Company' column:")
print(df['Company'])

# Selecting rows by index
print("\nSelecting row with index 1:")
print(df.loc[1])

# Filtering data
print("\nFiltering rows where 'Price' is > 23:")
print(df[df['Price'] > 23])

# New Column
df['Price_Change'] = [20, -15, 23.5]
print("\n Adding new column 'Price_Change':")
print(df)

# Grouping data
grouped_data = df.groupby('City').sum()
print(grouped_data)

# Sorting data
sorted_data = df.sort_values(by='Price', ascending=False)
print("\nData sorted by 'Price':")
print(sorted_data)
