import os
import sqlite3
import uuid
import warnings
from datetime import date

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

load_dotenv()
warnings.filterwarnings("ignore")

db_dir = os.path.join(os.getcwd(), "agents", "db")
db = os.path.join(db_dir, "travel.sqlite")


class SearchHotel(BaseTool):
    name: str = "search_hotel"
    description: str = """
    Search for hotels based on location, name, price tier, check-in date, and check-out date.

    Args:
        location (Optional[str]): The location of the hotel. Defaults to None.
        name (Optional[str]): The name of the hotel. Defaults to None.
        price_tier (Optional[str]): The price tier of the hotel. Defaults to None. Examples: Midscale, Upper Midscale, Upscale, Luxury

    Returns:
        list[dict]: A list of hotel dictionaries matching the search criteria.
    """

    def _run(
        self,
        location: str = None,
        name: str | None = None,
        price_tier: str | None = None,
    ) -> list[dict]:
        print(f"Executing search_hotel with location={location}, price_tier={price_tier}")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = "SELECT * FROM hotels WHERE 1=1"
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

        return [dict(zip([column[0] for column in cursor.description], row)) for row in results]


class BookHotel(BaseTool):
    name: str = "book_hotel"
    description: str = """
    Book a hotel by its ID.

    Args:
        hotel_id (int): The ID of the hotel to book.

    Returns:
        str: A message indicating whether the hotel was successfully booked or not.
    """

    def _run(
        self,
        config: RunnableConfig,
        hotel_id: str,
        check_in_date: date,
        check_out_date: date,
        room_type: str | None = None,
        num_guests: int = 1,
    ) -> str:
        print(
            f"Executing book_hotel with hotel_id={hotel_id}, check_in_date={check_in_date}, check_out_date={check_out_date}, num_guests={num_guests}"
        )

        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Get hotel details
        query = "SELECT * FROM hotels WHERE id = ?"
        cursor.execute(query, (hotel_id,))
        hotel_details = cursor.fetchone()
        if not hotel_details:
            raise ValueError(f"Hotel with ID {hotel_id} not found.")

        # Book the hotel
        booking_id = uuid.uuid4().hex[:8].upper()
        query = (
            "INSERT INTO hotel_bookings (booking_id, hotel_id, passenger_id, check_in_date, check_out_date, room_type, num_guests) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        params = [
            booking_id,
            hotel_id,
            passenger_id,
            check_in_date,
            check_out_date,
            room_type,
            num_guests,
        ]

        cursor.execute(query, params)
        conn.commit()
        booking_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return f"Hotel booked successfully with booking ID: {booking_id}"


class UpdateHotelBooking(BaseTool):
    name: str = "update_hotel_booking"
    description: str = """
    Update a hotel's check-in and check-out dates by its ID.

    Args:
        hotel_id (int): The ID of the hotel to update.
        checkin_date (Optional[Union[datetime, date]]): The new check-in date of the hotel. Defaults to None.
        checkout_date (Optional[Union[datetime, date]]): The new check-out date of the hotel. Defaults to None.

    Returns:
        str: A message indicating whether the hotel was successfully updated or not.
    """

    def _run(
        self,
        config: RunnableConfig,
        new_check_in_date: date,
        new_check_out_date: date,
    ) -> str:
        print(
            f"Executing update_hotel_booking with new_check_in_date={new_check_in_date}, new_check_out_date={new_check_out_date}"
        )

        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No booking ID configured.")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Get Booking ID
        query = "SELECT * FROM hotel_bookings WHERE passenger_id = ?"
        cursor.execute(query, (passenger_id,))
        booking_details = cursor.fetchone()
        print(booking_details)

        if not booking_details:
            cursor.close()
            conn.close()
            return "No existing booking found for the given passenger ID."
        booking_id = booking_details[0]

        # Update the hotel booking
        query = (
            "UPDATE hotel_bookings SET check_in_date = ?, check_out_date = ? WHERE booking_id = ?"
        )
        params = [new_check_in_date, new_check_out_date, booking_id]

        cursor.execute(query, params)
        conn.commit()

        cursor.close()
        conn.close()

        return f"Hotel booking with ID {booking_id} successfully updated."


class CancelHotelBooking(BaseTool):
    name: str = "cancel_hotel_booking"
    description: str = """
    Cancel a hotel by its ID.

    Args:
        hotel_id (int): The ID of the hotel to cancel.

    Returns:
        str: A message indicating whether the hotel was successfully cancelled or not.
    """

    def _run(self, config: RunnableConfig, hotel_id: str) -> str:
        print(f"Executing cancel_hotel_booking with hotel_id={hotel_id}")

        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Check if the booking exists
        query = "SELECT * FROM hotel_bookings WHERE passenger_id = ?"
        cursor.execute(query, (passenger_id,))
        existing_booking = cursor.fetchone()
        if not existing_booking:
            cursor.close()
            conn.close()
            return "No existing booking found for the given booking ID."

        # Cancel the hotel booking
        booking_id = existing_booking[0]
        query = "DELETE FROM hotel_bookings WHERE booking_id = ?"
        cursor.execute(query, (booking_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return f"Hotel booking with ID {booking_id} has been successfully canceled."
