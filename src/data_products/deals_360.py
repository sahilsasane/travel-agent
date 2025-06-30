from data_products.lens_utils import LensUtils


class Deals360:
    def __init__(self):
        self.lens = LensUtils()

    def get_active_deals(self, customer_id: str = "", product_ids: list = []) -> dict:
        lens_name = "public:deals360"
        query = {
            "measures": [],
            "dimensions": ["deals.discount_percentage", "deals.product_id", "deals.deal_status"],
            "segments": [],
            "filters": [
                {
                    "and": [
                        {
                            "member": "deals.product_id",
                            "operator": "equals",
                            "values": [
                                "16ea9a48-3e19-4c13-b2f3-9bc5a2c71d73",
                                "2436193d-e75c-4abe-9575-dabebd4d390d",
                                "8a736ae0-8839-433b-892f-bc0bc95d9c76",
                            ],
                        }
                    ]
                }
            ],
            "timeDimensions": [],
            "limit": 10,
            "offset": 0,
            "order": [],
        }
        if product_ids:
            query["filters"][0]["and"].append(
                {"member": "product.product_id", "operator": "in", "values": product_ids}
            )
        return self.lens.get_results(query, lens_name)
