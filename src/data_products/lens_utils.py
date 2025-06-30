# this cclass helps query a given lens and returns the results various formats.
import json
import os
import time

import pandas as pd
import requests


class LensUtils:
    def __init__(self):
        self.lensurl = os.environ["LENS2_API_URL"]
        self._query_max_retries = 3
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": os.environ["LENS2_API_SECRET"],
            "apikey": os.environ["LENS2_API_SECRET"],
        }

    def get_results(self, query: dict, lens_name: str) -> dict:
        url = os.environ["LENS2_API_URL"] + lens_name + "/v2/load"
        data = {"query": {}}
        data["query"] = query

        print(data)
        response = None
        try:
            retries = 0
            while retries < self._query_max_retries:
                response = requests.post(url, json=data, headers=self.headers)
                if response.status_code == 200:
                    response_data = response.json()
                    print(response_data["data"])
                    if "error" in response_data and response_data["error"] == "Continue wait":
                        retries += 1
                        time.sleep(3)
                        continue
                    else:
                        return response_data["data"]
                else:
                    print("Lens Query Request Failed. Status Code: ", response.status_code)
                    break

        except Exception as ex:
            # traceback.print_exc()
            print(ex)

        return response

    def dry_run(self, query: str) -> dict:
        # this will return the query plan and the expected results
        response = None
        try:
            qry = {"query": json.loads(query)}
            lensurl = os.environ["LENS2_API_URL"]
            response = requests.get(f"{lensurl}/dry-run?query={query}", headers=self.headers)

            response_data = response.json()
            if "error" in response_data:
                # logger.error("dry-run: error in query")
                return False, response_data
            else:
                return True, response_data

            # logger.error("Lens Query Dryrun Request Failed. Status Code: ",response.status_code)

        except Exception as ex:
            # traceback.print_exc()
            return False, {"error": "Fatal"}

    def get_results_df(self, query: str) -> pd.DataFrame:
        res = self.get_results(query)
        res_data = res.json()["data"]
        df = pd.DataFrame(res_data)
        return df
