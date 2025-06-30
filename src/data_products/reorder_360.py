from data_products.lens_utils import LensUtils


class Reorder360:
    def __init__(self):
        self.lens = LensUtils()

    def get_reorder_patterns(self, customer_id: str) -> dict:
        lens_name = "public:reorder360"
        query = {
            "measures": [],
            "dimensions": [
                "customer.customer_id",
                "reorder_analysis.product_id",
                "reorder_analysis.recom_rank",
                "reorder_analysis.reorder_status",
                "reorder_analysis.invoice_days",
                "reorder_analysis.inv_total_count",
                "reorder_analysis.inv_week_count",
                "reorder_analysis.item_month_count",
                "reorder_analysis.item_week_count",
                "reorder_analysis.days_since_last_invoice",
                "reorder_analysis.avg_days_between_order",
                "customer.primary_warehouse_id",
                "product.sub_category",
            ],
            "segments": [],
            "filters": [
                {
                    "and": [
                        {
                            "member": "reorder_analysis.recom_rank",
                            "operator": "lte",
                            "values": ["3"],
                        },
                        {
                            "member": "customer.customer_id",
                            "operator": "equals",
                            "values": ["011a94f0-35ce-4dcc-ab54-5f693123e74f"],
                        },
                        {
                            "member": "reorder_analysis.reorder_status",
                            "operator": "equals",
                            "values": ["Upcoming"],
                        },
                        {
                            "member": "customer.primary_warehouse_id",
                            "operator": "equals",
                            "values": ["WH-023"],
                        },
                    ]
                }
            ],
            "timeDimensions": [
                {"dimension": "reorder_analysis.last_invoice_date", "granularity": "day"}
            ],
            "limit": 3,
            "offset": 0,
            "order": [],
        }
        return self.lens.get_results(query, lens_name)
