import sqlite3
import warnings
from datetime import date, datetime
from typing import Optional

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

load_dotenv()
warnings.filterwarnings("ignore")
db = "./travel.sqlite"


class SearchCarRental(BaseTool):
    name: str = "search_car_rental"
    description: str = """
    Search for car rentals based on location, name, price tier, start date, and end date.

    Args:
        location (Optional[str]): The location of the car rental. Defaults to None.
        name (Optional[str]): The name of the car rental company. Defaults to None.
        price_tier (Optional[str]): The price tier of the car rental. Defaults to None.
        start_date (Optional[Union[datetime, date]]): The start date of the car rental. Defaults to None.
        end_date (Optional[Union[datetime, date]]): The end date of the car rental. Defaults to None.

    Returns:
        list[dict]: A list of car rental dictionaries matching the search criteria.
    """

    def _run(
        self,
        location: str = None,
        name: str | None = None,
        price_tier: str | None = None,
        start_date: Optional[date | datetime] = None,
        end_date: Optional[date | datetime] = None,
    ) -> list[dict]:
        print(
            f"Executing search_hotel with location={location}, price_tier={price_tier}"
        )

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # query = "SELECT  FROM car_rentals WHERE 1=1"
        query = (
            "SELECT id, name, location, price_tier, booked FROM car_rentals WHERE 1=1"
        )
        params = []

        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")

        cursor.execute(query, params)
        results = cursor.fetchall()

        conn.close()

        return [
            dict(zip([column[0] for column in cursor.description], row))
            for row in results
        ]


class BookCarRental(BaseTool):
    name: str = "book_car_rental"
    description: str = """
    Book a car rental by its ID.

    Args:
        rental_id (int): The ID of the car rental to book.

    Returns:
        str: A message indicating whether the car rental was successfully booked or not.
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

        cursor.execute("UPDATE car_rentals SET booked = 1 WHERE id = ?", (rental_id,))
        conn.commit()

        if cursor.rowcount > 0:
            conn.close()
            return f"Car rental {rental_id} successfully booked."
        else:
            conn.close()
            return f"No car rental found with ID {rental_id}."


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
