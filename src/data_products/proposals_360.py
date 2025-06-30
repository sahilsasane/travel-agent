from data_products.lens_utils import LensUtils


class Proposals360:
    def __init__(self):
        self.lens = LensUtils()

    def get_recommendations(self, customer_id: str) -> dict:
        lens_name = "public:proposal360"
        query = {
            "measures": [],
            "dimensions": [
                "product.stock_quantity",
                "product.brand",
                "product.category",
                "product.sub_category",
                "proposal.product_id",
                "proposal.customer_id",
                "proposal.proposal_status",
                "proposal.proposed_price",
            ],
            "segments": [],
            "filters": [
                {
                    "and": [
                        {
                            "member": "proposal.proposal_status",
                            "operator": "equals",
                            "values": ["Accepted"],
                        },
                        {
                            "member": "proposal.customer_id",
                            "operator": "equals",
                            "values": ["011a94f0-35ce-4dcc-ab54-5f693123e74f"],
                        },
                    ]
                }
            ],
            "timeDimensions": [{"dimension": "proposal.proposal_date", "granularity": "day"}],
            "limit": 1,
            "offset": 0,
            "order": [],
        }
        return self.lens.get_results(query, lens_name)
