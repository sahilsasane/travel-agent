from data_products.lens_utils import LensUtils


class Product360:
    def __init__(self):
        self.lens = LensUtils()

    def get_product_details(self, product_ids: list) -> dict:
        lens_name = "public:product360"
        query = {
            "measures": [],
            "dimensions": ["product.sub_category", "product.product_id", "product.product_name"],
            "segments": [],
            "filters": [
                {
                    "and": [
                        {
                            "member": "product.sub_category",
                            "operator": "equals",
                            "values": ["Stout & Porter"],
                        }
                    ]
                }
            ],
            "timeDimensions": [],
            "limit": 1,
            "offset": 0,
            "order": [],
        }
        return self.lens.get_results(query, lens_name)
