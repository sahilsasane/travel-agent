from data_products.lens_utils import LensUtils


class Inventory360:
    def __init__(self):
        self.lens = LensUtils()

    def get_stock_levels(self, product_ids: list) -> dict:
        lens_name = "public:inventory360"
        query = {
            "measures": ["inventory.total_stock_quantity"],
            "dimensions": ["inventory.product_id"],
            "segments": [],
            "filters": [
                {
                    "and": [
                        {
                            "member": "inventory.product_id",
                            "operator": "equals",
                            "values": product_ids,
                        }
                    ]
                }
            ],
            "timeDimensions": [],
            "limit": 1000,
            "offset": 0,
            "order": [],
            "timezone": "UTC",
        }
        return self.lens.get_results(query, lens_name)
