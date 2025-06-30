from data_products.lens_utils import LensUtils

#this class provides the access to query customer 360 for multiple scenarios.
#get customer status  based on the customer id
#get customer details based on the customer id
#get customer transactions based on the customer id
#get customer details based on the customer id

class Customer360:
    def __init__(self):
        self.lens = LensUtils()

    def get_customer_status(self, customer_id):
        lens_name = "public:customer360"
        customer_query = {
        "measures": [],
        "dimensions": [
            "customer.customer_id",
            "customer.license",
            "customer.state",
            "customer.status",
            "customer.primary_warehouse_id",
            "customer.premise",
            "customer.delivery_day",
            "customer.delivery_frequency",
            "customer.country"
        ],
        "segments": [],
        "filters": [
            {
            "and": [
                {
                "member": "customer.customer_id",
                "operator": "equals",
                "values": [
                    "011a94f0-35ce-4dcc-ab54-5f693123e74f"
                ]
                }
            ]
            }
        ],
        "timeDimensions": [
            {
            "dimension": "customer.license_deactivation",
            "granularity": "day"
            },
            {
            "dimension": "customer.activation_date",
            "granularity": "day"
            }
        ],
        "limit": 10,
        "offset": 0,
        "order": []
        }
        results = self.lens.get_results(customer_query, lens_name)
        return results

    def get_next_delivery_window(self, customer_id):
        lens_name = "public:customer360"
        customer_query = {
                        "measures": [],
                        "dimensions": [
                            "customer.customer_id",
                            "customer.status"
                        ],
                        "segments": [],
                        "filters": [
                            {
                            "and": [
                                {
                                "member": "customer.customer_id",
                                "operator": "equals",
                                "values": [
                                    "011a94f0-35ce-4dcc-ab54-5f693123e74f"
                                ]
                                }
                            ]
                            }
                        ],
                        "timeDimensions": [
                            {
                            "dimension": "customer.next_delivery_date",
                            "granularity": "day"
                            }
                        ],
                        "limit": 10,
                        "offset": 0,
                        "order": []
                        }
        results = self.lens.get_results(customer_query, lens_name)
        return results

if __name__ == '__main__':
    customer_360 = Customer360()
    results = customer_360.get_customer_status('011a94f0-35ce-4dcc-ab54-5f693123e74f')
    print(results)