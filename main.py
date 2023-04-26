# help(pandas)

import requests
import pandas as pd 
import pprint as pp
import logging

logger = logging.getLogger(__name__)

ROOT_URL = "https://api.beta.ons.gov.uk/v1/"

def list_of_datasets():
    # There are 41 available datasets 
    # Gets list of all datasets available from API
        num_to_get = 100
        datasets = []
        offset = 0 
        while len(datasets) < num_to_get:
                r = requests.get(ROOT_URL + "datasets", params = {"offset": offset})
                results = r.json()
                [logger.info(item.get("title")) for item in results.get("items")]
                datasets.extend(results.get("items"))
                num_retrieved = results.get("count")
                offset += num_retrieved
                if num_retrieved == 0: 
                        break 
        logger.info(f"\nFound {len(datasets)} datasets")
        return datasets
def get_dataset_by_name(datasets, target_name):

        for ds in datasets:
                if target_name.lower() in ds.get("title").lower():
                        logger.info(f"Found dataset '{ds.get('title')}'")
                        return ds
        logger.info(f"No dataset found containing '{target_name}'")
        return None

def get_edition(dataset, prefered_edition="time-series"):
    
        editions_url = dataset.get("links").get("editions").get("href")
        r = requests.get(editions_url)
        results = r.json()
        for row in results.get("items"):
                if row.get("edition") == prefered_edition:
                        edition = row.get("links").get("latest_version").get("href")
                        return edition

        # Default to latest version, if requested version is not found.
        latest_version = dataset.get("links").get("latest_version").get("href")
        return latest_version

def get_dimensions(edition_url):

        valid_dimensions = {}
    
        r = requests.get(edition_url + "/dimensions")
        results = r.json()
        for dimension in results.get("items"):
                logger.info(f'{dimension.get("name")}: \t{dimension.get("label")}')
                dim_id = dimension.get("links").get("options").get("id")
                options_url = f"{edition_url}/dimensions/{dim_id}/options"

                sr = requests.get(options_url, params={"limit": 50})
                sresults = sr.json()
                # TODO! Could add in paging here, as there *could* be multiple pages of valid options.
                logger.info(f"\tHas {sresults.get('count')} options")
                # valid_options = [item.get("option") for item in sresults.get("items")]
                option_descriptions = {
                item.get("option"): item.get("label") for item in sresults.get("items")
                }
                logger.info(f'{dimension.get("name")}: {option_descriptions}')
                valid_dimensions[dimension.get("name")] = option_descriptions

        return valid_dimensions


def choose_dimensions(valid_dims, overrides={}):
        # By default, choose first valid item for all dimensions; then override where needed:
        chosen_dimensions = {k: next(iter(v.keys())) for k, v in valid_dims.items()}
        # get whole time-series, not just a single point in time:
        chosen_dimensions["time"] = "*"
        chosen_dimensions.update(overrides)
        return chosen_dimensions


def get_observations(edition_url, dimensions):

        r = requests.get(edition_url + "/observations", params=dimensions)
        results = r.json()
        summary = []
        for observation in results.get("observations"):
                id = observation.get("dimensions").get("Time").get("id")
                summary.append({"id": id, "observation": observation.get("observation")})
        df = pd.DataFrame(summary)
        return df


def get_timeseries(dataset_name, dimension_values):

        dss = list_of_datasets()
        ds = get_dataset_by_name(dss, dataset_name)
        edition_url = get_edition(ds)
        valid_dims = get_dimensions(edition_url)
        logger.info(valid_dims)
        if dimension_values is None:
                return valid_dims
        chosen_dimensions = choose_dimensions(valid_dims, dimension_values)
        df = get_observations(edition_url, chosen_dimensions)
        logger.info(df.shape)
        return df, ds, edition_url

def demo():
        '''
        print("=" * 70)
        print("List of available datasets:")
        dss = list_of_datasets()

        # Extract the titles from the datasets list
        titles = [item.get("title") for item in dss]

         # Create a DataFrame from the list of titles
        df = pd.DataFrame(titles, columns=["title"])
 
        # Save the DataFrame as an Excel file
        df.to_excel("datasets_list.xlsx", index=False)

        [print(item.get("title")) for item in dss]
        '''

        print("=" * 70)
        dataset_name = "UK Labour Market"
        print(f"Valid options for dimensions for the {dataset_name}, with descriptions")
        # Get the set of valid dimensions for the Labour Market set.
        # E.g. list of valid age groups, economic activity categories etc.

        dimensions = get_timeseries(dataset_name, None)
        pp.pprint(dimensions)
        df2 = pd.DataFrame(dimensions)
        df2.to_excel("UK Labour Market.xlsx", index = False)
        print("\n")

        dataset_name = "Annual GDP for England, Wales and the English regions"
        print(f"Valid options for dimensions for the {dataset_name}, with descriptions")
        # Get the set of valid dimensions for the Labour Market set.
        # E.g. list of valid age groups, economic activity categories etc.

        dimensions = get_timeseries(dataset_name, None)
        pp.pprint(dimensions)
        print("\n")

        GDP_ds_name = "Annual GDP"
        GDP_dimensions = {
                "geography": "UKI",
                "growthrate" : "gra",
        }
        print(f"Chosen dimensions for the {dataset_name}")
        pp.pprint(GDP_dimensions, indent=4)

        df_GDP = get_timeseries(GDP_ds_name, GDP_dimensions)[0]
        df_GDP = df_GDP.sort_values("id")
        print(GDP_ds_name)
        print(df_GDP)


if __name__ == "__main__":
    demo()

'''
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

'''

'''
api_key = '932528a61e46dbfce70dde3f56e455ef'
series_id = 'GDPC1'  # Real Gross Domestic Product (USA)
url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json'

response = requests.get(url)
data = response.json()

observations = data['observations']
df = pd.DataFrame(observations)

df['date'] = pd.to_datetime(df['date'])
df['value'] = pd.to_numeric(df['value'], errors='coerce')
df.dropna(inplace=True)

df.to_excel('gdp_data.xlsx', index=False)
'''

