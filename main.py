# help(pandas)

import requests
import pandas as pd 
import pprint as pp


ROOT_URL = "https://api.beta.ons.gov.uk/v1/"

def list_of_datasets():
    # There are 41 available datasets 
    # Gets list of all datasets available from API
        num_to_get = 100
        datasets = []
        offset = 0 

        all_data = pd.DataFrame()

        while len(datasets) < num_to_get:
                r = requests.get(ROOT_URL + "datasets", params = {"offset": offset})
                results = r.json()


                df = pd.DataFrame(results.get("items"))
                all_data = pd.concat([all_data, df], ignore_index = True)
                # Save DataFrame to Excel file
                

                datasets.extend(results.get("items"))
                num_retrieved = results.get("count")
                offset += num_retrieved
                if num_retrieved == 0: 
                        break 

        all_data.to_excel("datasets_output.xlsx", index=False)

        return datasets

def get_dataset_by_name(datasets, target_name):

        for ds in datasets:
                if target_name.lower() in ds.get("title").lower():
                        return ds
        return None

def get_edition(dataset, preferred_edition="time-series"):
        # navigates through nested dictionaries to extract the value of the "href" key inside the "editions" dictionary, which is itself inside the "links" dictionary. 
        editions_url = dataset.get("links").get("editions").get("href")
        response = requests.get(editions_url)
        results = response.json()

        latest_version = dataset.get("links").get("latest_version").get("href")
        edition = latest_version

        for item in results.get("items"):
                if item.get("edition") == preferred_edition:
                        edition = item.get("links").get("latest_version").get("href")
                        break

        return edition

def get_dimensions(edition_url):

        valid_dimensions = {}
    
        r = requests.get(edition_url + "/dimensions")
        results = r.json()
        for dimension in results.get("items"):

                dim_id = dimension.get("links").get("options").get("id")
                options_url = f"{edition_url}/dimensions/{dim_id}/options"

                sr = requests.get(options_url, params={"limit": 50})
                sresults = sr.json()
                
        
                # valid_options = [item.get("option") for item in sresults.get("items")]
                option_descriptions = {
                item.get("option"): item.get("label") for item in sresults.get("items")
                }

                valid_dimensions[dimension.get("name")] = option_descriptions

        return valid_dimensions


def choose_dimensions(valid_dims, overrides={}):
        # By default, choose first valid item for all dimensions; then override where needed:'
        chosen_dimensions = {}
        # loop goes through each dimension in the valid_dims dictionary, finds the first available option for that dimension, and creates a new dictionary (chosen_dimensions) where the keys are the dimensions and the values are the first available options for each dimension.
        for k, v in valid_dims.items():
                chosen_dimensions[k] = next(iter(v.keys()))
        # get whole time-series, not just a single point
        chosen_dimensions["time"] = "*"
        '''
        for key, value in overrides.items():
                if key in chosen_dimensions: 
                        chosen_dimensions[key] = value
        ''' 
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
        if dimension_values is None:
                return valid_dims
        chosen_dimensions = choose_dimensions(valid_dims, dimension_values)
        df = get_observations(edition_url, chosen_dimensions)
       # Return a tuple containing three elements: dataframe(df) with the observations, dataset observations (ds), and the edition URL
        return df, ds, edition_url

def demo():
        
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

