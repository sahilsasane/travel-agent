import os
import sqlite3
import warnings
from datetime import date, datetime

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

load_dotenv()
warnings.filterwarnings("ignore")


db_dir = os.path.join(os.getcwd(), "db")
db = os.path.join(db_dir, "travel.sqlite")


class SearchTaxi(BaseTool):
    name: str = "search_taxi"
    description: str = """
    Search for taxi based on passenger count, vehicle type, and price tier.

    Args:
        passenger_count (int, optional): The number of passengers. Defaults to None.
        vehicle_type (str, optional): The type of vehicle to search for. Defaults to None.
        price_tier (str, optional): The price tier of the taxi. Defaults to None.

    Returns:
        list[dict]: A list of taxi dictionaries matching the search criteria.
    """

    def _run(
        self,
        vehicle_type: str | None = None,
        price_tier: str | None = None,
    ) -> list[dict]:
        print(f"Executing search_taxis with vehicle_type={vehicle_type}, price_tier={price_tier}")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = "SELECT * FROM taxi WHERE 1=1"
        params = []

        cursor.execute(query, params)
        results = cursor.fetchall()

        conn.close()

        return [dict(zip([column[0] for column in cursor.description], row)) for row in results]


class BookTaxi(BaseTool):
    name: str = "book_taxi"
    description: str = """
    Book a taxi for a passenger

    Args:
        id (str): The ID of the passenger.
        vehicle_type (str): The type of vehicle to book.
        pickup_time (Union[datetime, date]): The time when the taxi should pick up the passenger.
        pickup_location (str): The location where the passenger will be picked up.
        dropoff_location (str): The location where the passenger will be dropped off.

    Returns:
        str: A message indicating whether the taxi was successfully booked or not.
    """

    def _run(
        self,
        config: RunnableConfig,
        id: str,
        vehicle_type: str,
        pickup_time: date | datetime,
        pickup_location: str,
        dropoff_location: str,
    ) -> str:
        print(f"Executing book_car_rental with id={id}, vehicle_type={vehicle_type}, ")

        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = "INSERT INTO taxi_bookings (id, passenger_id, vehicle_type, pickup_time, pickup_location, dropoff_location) VALUES (?, ?, ?, ?, ?, ?)"
        params = (id, passenger_id, vehicle_type, pickup_time, pickup_location, dropoff_location)

        cursor.execute(query, params)
        conn.commit()

        if cursor.rowcount > 0:
            conn.close()
            return f"Taxi successfully booked for passenger {id}."
        else:
            conn.close()
            return f"Failed to book taxi for passenger {id}."

        # cursor.execute("UPDATE car_rentals SET booked = 1 WHERE id = ?", (rental_id,))
        # conn.commit()

        # if cursor.rowcount > 0:
        #     conn.close()
        #     return f"Car rental {rental_id} successfully booked."
        # else:
        #     conn.close()
        #     return f"No car rental found with ID {rental_id}."


class UpdateCarRental(BaseTool):
    name: str = "update_car_rental"
    description: str = """
    Update a car rental's start and end dates by its ID.

    Args:
        rental_id (int): The ID of the car rental to update.
        start_date (Optional[Union[datetime, date]]): The new start date of the car rental. Defaults to None.
        end_date (Optional[Union[datetime, date]]): The new end date of the car rental. Defaults to None.

    Returns:
        str: A message indicating whether the car rental was successfully updated or not.
    """

    def _run(
        self,
        config: RunnableConfig,
        rental_id: str,
        start_date: date,
        end_date: date,
    ) -> str:
        print(
            f"Executing book_car_rental with rental_id={rental_id}, start_date={start_date}, end_date={end_date}"
        )

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        if start_date:
            cursor.execute(
                "UPDATE car_rentals SET start_date = ? WHERE id = ?",
                (start_date, rental_id),
            )
        if end_date:
            cursor.execute(
                "UPDATE car_rentals SET end_date = ? WHERE id = ?",
                (end_date, rental_id),
            )

        conn.commit()

        if cursor.rowcount > 0:
            conn.close()
            return f"Car rental {rental_id} successfully updated."
        else:
            conn.close()
            return f"No car rental found with ID {rental_id}."


class CancelCarRental(BaseTool):
    name: str = "cancel_car_rental"
    description: str = """
    Cancel a car rental by its ID.

    Args:
        rental_id (int): The ID of the car rental to cancel.

    Returns:
        str: A message indicating whether the car rental was successfully cancelled or not.
    """

    def _run(
        self,
        config: RunnableConfig,
        rental_id: str,
    ) -> str:
        print(f"Executing cancel_car_rental with rental_id={rental_id}")

        conn = sqlite3.connect(db)

        cursor = conn.cursor()

        cursor.execute("UPDATE car_rentals SET booked = 0 WHERE id = ?", (rental_id,))
        conn.commit()

        if cursor.rowcount > 0:
            conn.close()
            return f"Car rental {rental_id} successfully cancelled."
        else:
            conn.close()
            return f"No car rental found with ID {rental_id}."
