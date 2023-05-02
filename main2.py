#help(pandas)

import requests
import pandas as pd 
import pprint as pp


ROOT_URL = "https://api.beta.ons.gov.uk/v1/"

def list_of_datasets():
    # There are 41 available datasets 
    # Gets list of all datasets available from API
        count = 42
        datasets = []
        offset = 0 

        all_data = pd.DataFrame()

        while len(datasets) < count:
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

        # all_data.to_excel("datasets_output.xlsx", index=False)

        return datasets

def get_dataset_by_name(datasets, target_name):

        for ds in datasets:
                if target_name.lower() in ds.get("title").lower():
                        #pp.pprint(ds)
                        #print("#" * 70)
                        return ds
        return None

def get_edition(dataset, preferred_edition="time-series"):
        # navigates through nested dictionaries to extract the value of the "href" key inside the "editions" dictionary, which is itself inside the "links" dictionary. 
        editions_url = dataset.get("links").get("editions").get("href")
        response = requests.get(editions_url)
        results = response.json()

        #pp.pprint(results)
        #print("#" * 70)

        latest_version = dataset.get("links").get("latest_version").get("href")
        edition = latest_version

        for item in results.get("items"):
                if item.get("edition") == preferred_edition:
                        edition = item.get("links").get("latest_version").get("href")
                        break

        return edition

def get_dimensions(edition_url, target_dimension = None):

        valid_dimensions = {}
    
        r = requests.get(edition_url + "/dimensions")
        results = r.json()
        #pp.pprint(results)
        #print("#" * 70)
        for dimension in results.get("items"):

                dim_id = dimension.get("links").get("options").get("id")
                options_url = f"{edition_url}/dimensions/{dim_id}/options"

                sr = requests.get(options_url, params={"limit": 50})
                sresults = sr.json()
                
                # valid_options = [item.get("option") for item in sresults.get("items")]
                option_descriptions = {item.get("option"): item.get("label") for item in sresults.get("items")}
                valid_dimensions[dimension.get("name")] = option_descriptions
                '''
                if dimension.get("name") == target_dimension:
                        print(f"Options for {target_dimension}:")
                        for option, label in option_descriptions.items():
                                print(f"{option}: {label}")
                        print("#" * 70)
                '''
        return valid_dimensions


def choose_dimensions(valid_dims, overrides = {}):
        # By default, choose first valid item for all dimensions; then override where needed:'
        chosen_dimensions = {}
        # loop goes through each dimension in the valid_dims dictionary, finds the first available option for that dimension, and creates a new dictionary (chosen_dimensions) where the keys are the dimensions and the values are the first available options for each dimension.
        for k, v in valid_dims.items():
                chosen_dimensions[k] = next(iter(v.keys()))
        # get whole time-series, not just a single point
        chosen_dimensions["time"] = "*"

        #  Allows you to specificy the specific dimensions in the control function
        chosen_dimensions.update(overrides)
        
        pp.pprint(chosen_dimensions)
        print("*" * 70)

        return chosen_dimensions


def get_observations(edition_url, dimensions):

        r = requests.get(edition_url + "/observations", params=dimensions)
        results = r.json()

        #pp.pprint(results)
        #print("#" * 70)

        # Printing the dimensions dictionary 
        # print("Dimensions:", dimensions)
        # print("#" * 70)
        
        summary = []
        if results.get("observations") is not None:
            for observation in results.get("observations"):

                    '''
                    time_dict = observation.get("dimensions").get("Time")
                    print("Time dictionary:", time_dict)
                    print("#" * 70)

                    observ = observation.get("observation")
                    print(observ)
                    '''
                    

                    id = observation.get("dimensions").get("Time").get("id")
                    summary.append({"id": id, "observation": observation.get("observation")})
        df = pd.DataFrame(summary)
        # print(df)
        
        return df


def get_timeseries(dataset_name, dimension_values):
        # Fetches a list of all available datasets
        dss = list_of_datasets()
        ds = get_dataset_by_name(dss, dataset_name)
        # Retrives URL for time-series edition
        edition_url = get_edition(ds)
        # Fetches the valid dimensions and their options for the dataset edition 
        valid_dims = get_dimensions(edition_url)
        if dimension_values is None:
                return valid_dims
        chosen_dimensions = choose_dimensions(valid_dims, overrides = dimension_values)
        # Fetches the observations for the specified dimensions and stores them in a DataFrame
        df = get_observations(edition_url, chosen_dimensions)
       # Return a tuple containing three elements: dataframe(df) with the observations, dataset observations (ds), and the edition URL
        return df, ds, edition_url

def control():
        # Set value to 1, if you'd like to print list of available datasets, 2 if you'd like to see the valid dimension options for the chosen data, 0 otherwise
        controut = 0 


        if controut == 1:
                print("*" * 70)
                print("List of available datasets:")
                dss = list_of_datasets()
                # Extract the titles from the datasets list
                titles = [item.get("title") for item in dss]
                # Create a DataFrame from the list of titles
                df = pd.DataFrame(titles, columns=["title"])
                # Save the DataFrame as an Excel file
                df.to_excel("datasets_list.xlsx", index=False)
                [print(item.get("title")) for item in dss]
        else:
                dss = list_of_datasets()
       

        dataset_name = "Annual GDP for England, Wales and the English regions"

        print("\n")
        print(dataset_name)
        if controut == 2: 
                print("*" * 70)        
                print(f"Valid options for dimensions for the {dataset_name}")
                dimensions = get_timeseries(dataset_name, None)
                pp.pprint(dimensions)
                dfdim = pd.DataFrame(dimensions)
                dfdim.to_excel("Dimensions.xlsx", index = False)
                print("\n")

        # Input Desired Dimensions   
        GDP_dimensions = {
                "geography": "UKI",
                "growthrate" : "aix",
                #"unofficialstandardindustrialclassification": 'A-T',
        }
        print(f"Chosen dimensions for the {dataset_name}")
        #pp.pprint(GDP_dimensions, indent=4)
        # print("*" * 70)
        # print("\n")

        df_GDP = get_timeseries(dataset_name, GDP_dimensions)[0]
        # print(df_GDP)
        # Sorts the output by year 
        df_GDP = df_GDP.sort_values("id")
        # Converting to numerical format, 'coerce' sets NaN if cannot convert 
        df_GDP["id"] = pd.to_numeric(df_GDP["id"], errors="coerce") 
        df_GDP["observation"] = pd.to_numeric(df_GDP["observation"], errors="coerce") 
        df_GDP["% YOY_growth_rate"] = df_GDP["observation"].pct_change() * 100

        print("Annual GDP index for London 2012 - 2021")
        print(df_GDP)
        # Index = false prevents Pandas from including the index column in the output file
        df_GDP.to_excel("Annual_GDP_London_2012_2021.xlsx", index = False)

        # print(df_GDP.columns)


if __name__ == "__main__":
        control()
        '''
        dataset_name = "Annual GDP for England, Wales and the English regions"
        dss = list_of_datasets()
        ds = get_dataset_by_name(dss, dataset_name)
        edition_url = get_edition(ds)
        valid_dims = get_dimensions(edition_url, target_dimension="unofficialstandardindustrialclassification")
        '''

''' 
Annual GDP for England, Wales and English Regions:

{'editions': {'href': 'https://api.beta.ons.gov.uk/v1/datasets/regional-gdp-by-year/editions'}, 'latest_version': {'href': 'https://api.beta.ons.gov.uk/v1/datasets/regional-gdp-by-year/editions/time-series/versions/5', 'id': '5'}, 'self': {'href': 'https://api.beta.ons.gov.uk/v1/datasets/regional-gdp-by-year'}, 'taxonomy': {'href': 'https://api.beta.ons.gov.uk/v1/economy/grossdomesticproductgdp'}}

'''

