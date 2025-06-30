import unittest
from unittest.mock import Mock, patch

from data_products.customer_360 import Customer360


class TestCustomer360(unittest.TestCase):
    def setUp(self):
        self.customer360 = Customer360()

    def test_get_customer_status(self):
        # Mock response data
        mock_response = {
            "data": [
                {
                    "customer.customer_id": "011a94f0-35ce-4dcc-ab54-5f693123e74f",
                    "customer.status": "active",
                    "customer.state": "CA",
                    "customer.license": "ABC123",
                    "customer.primary_warehouse_id": "WH001",
                    "customer.premise": "commercial",
                    "customer.delivery_day": "Monday",
                    "customer.delivery_frequency": "weekly",
                    "customer.country": "USA",
                }
            ]
        }

        # Mock the LensUtils run_query method
        self.customer360.lens.run_query = Mock(return_value=mock_response)

        # Test the function
        result = self.customer360.get_customer_status("011a94f0-35ce-4dcc-ab54-5f693123e74f")

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["customer_id"], "011a94f0-35ce-4dcc-ab54-5f693123e74f")
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["state"], "CA")
        self.assertEqual(result["license"], "ABC123")
        self.assertEqual(result["primary_warehouse_id"], "WH001")
        self.assertEqual(result["premise"], "commercial")
        self.assertEqual(result["delivery_day"], "Monday")
        self.assertEqual(result["delivery_frequency"], "weekly")
        self.assertEqual(result["country"], "USA")

    def test_get_customer_status_no_data(self):
        # Mock empty response
        self.customer360.lens.run_query = Mock(return_value={"data": []})

        # Test the function
        result = self.customer360.get_customer_status("non-existent-id")

        # Assert that None is returned when no data is found
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
