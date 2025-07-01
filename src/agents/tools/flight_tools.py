import os
import sqlite3
import uuid
import warnings
from datetime import date, datetime

import pytz
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool

load_dotenv()
warnings.filterwarnings("ignore")

db_dir = os.path.join(os.getcwd(), "src", "agents", "db")
db = os.path.join(db_dir, "travel.sqlite")


@tool
def fetch_user_flight_information_og(config: RunnableConfig) -> list[dict]:
    """Fetch all tickets for the user along with corresponding flight information and seat assignments.

    Returns:
        A list of dictionaries where each dictionary contains the ticket details,
        associated flight details, and the seat assignments for each ticket belonging to the user.
    """
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("No passenger ID configured.")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    query = """
    SELECT 
        t.ticket_no, t.book_ref,
        f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport, f.scheduled_departure, f.scheduled_arrival,
        bp.seat_no, tf.fare_conditions
    FROM 
        tickets t
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        JOIN flights f ON tf.flight_id = f.flight_id
        JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = f.flight_id
    WHERE 
        t.passenger_id = ?
    """
    cursor.execute(query, (passenger_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    results = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    conn.close()

    return results


@tool
def fetch_user_flight_information(config: RunnableConfig) -> dict:
    """Fetch all tickets for the user along with corresponding flight information, hotel bookings, and taxi bookings.

    Returns:
        A dictionary containing flight tickets, hotel bookings, and taxi bookings for the user.
    """
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Fetch flight tickets
    ticket_query = """SELECT * FROM tickets WHERE passenger_id = ?"""
    cursor.execute(ticket_query, (passenger_id,))
    ticket_rows = cursor.fetchall()

    flight_results = []
    if ticket_rows:
        ticket_column_names = [column[0] for column in cursor.description]

        for ticket_row in ticket_rows:
            ticket_dict = dict(zip(ticket_column_names, ticket_row))
            flight_id = ticket_dict.get("flight_id")

            if flight_id:
                flight_query = """SELECT * FROM flights WHERE flight_id = ?"""
                cursor.execute(flight_query, (flight_id,))
                flight_row = cursor.fetchone()

                if flight_row:
                    flight_column_names = [column[0] for column in cursor.description]
                    flight_dict = dict(zip(flight_column_names, flight_row))
                    combined_info = {"ticket_info": ticket_dict, "flight_info": flight_dict}
                    flight_results.append(combined_info)
                else:
                    combined_info = {"ticket_info": ticket_dict, "flight_info": None}
                    flight_results.append(combined_info)
            else:
                combined_info = {"ticket_info": ticket_dict, "flight_info": None}
                flight_results.append(combined_info)

    # Fetch hotel bookings
    hotel_query = """SELECT * FROM hotel_bookings WHERE passenger_id = ?"""
    cursor.execute(hotel_query, (passenger_id,))
    hotel_rows = cursor.fetchall()

    hotel_results = []
    hotel_info_rows = []
    if hotel_rows:
        hotel_column_names = [column[0] for column in cursor.description]
        hotel_results = [dict(zip(hotel_column_names, row)) for row in hotel_rows]
        hotel_ids = [hotel["hotel_id"] for hotel in hotel_results]

        hotel_info_query = """SELECT * FROM hotels WHERE id IN ({})""".format(
            ",".join("?" for _ in hotel_ids)
        )
        cursor.execute(hotel_info_query, hotel_ids)
        hotel_info_rows = cursor.fetchall()

    # Fetch taxi bookings
    taxi_query = """SELECT * FROM taxi_bookings WHERE passenger_id = ?"""
    cursor.execute(taxi_query, (passenger_id,))
    taxi_rows = cursor.fetchall()

    taxi_results = []
    if taxi_rows:
        taxi_column_names = [column[0] for column in cursor.description]
        taxi_results = [dict(zip(taxi_column_names, row)) for row in taxi_rows]

    # Fetch car rental bookings
    car_rental_query = """SELECT * FROM car_rental_bookings WHERE passenger_id = ?"""
    cursor.execute(car_rental_query, (passenger_id,))
    car_rental_rows = cursor.fetchall()

    car_rental_results = []
    car_rental_info_rows = []
    if car_rental_rows:
        car_rental_column_names = [column[0] for column in cursor.description]
        car_rental_results = [dict(zip(car_rental_column_names, row)) for row in car_rental_rows]
        car_rental_ids = [car["rental_id"] for car in car_rental_results]

        car_rental_info_query = """SELECT * FROM car_rentals WHERE id IN ({})""".format(
            ",".join("?" for _ in car_rental_ids)
        )
        cursor.execute(car_rental_info_query, car_rental_ids)
        car_rental_info_rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Format and return all data
    return {
        "flights": flight_results,
        "hotels_bookings": hotel_results,
        "hotel_info": list(hotel_info_rows) if hotel_info_rows else [],
        "taxis": taxi_results,
        "car_rental_bookings": car_rental_results,
        "car_rental_info": list(car_rental_info_rows) if car_rental_info_rows else [],
        "summary": {
            "total_flights": len(flight_results),
            "total_hotels": len(hotel_results),
            "total_taxis": len(taxi_results),
            "total_car_rentals": len(car_rental_results),
        },
    }


class FetchFlightDetails(BaseTool):
    name: str = "fetch_flight_details"
    description: str = """Fetch all tickets for the user along with corresponding flight information and seat assignments.

    Returns:
        A list of dictionaries where each dictionary contains the ticket details,
        associated flight details, and the seat assignments for each ticket belonging to the user.
    """

    def _run(
        self,
        config: RunnableConfig,
    ) -> list[dict]:
        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = """
        SELECT 
            t.ticket_no, t.book_ref,
            f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport, f.scheduled_departure, f.scheduled_arrival,
            bp.seat_no, tf.fare_conditions
        FROM 
            tickets t
            JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
            JOIN flights f ON tf.flight_id = f.flight_id
            JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = f.flight_id
        WHERE 
            t.passenger_id = ?
        """
        cursor.execute(query, (passenger_id,))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()

        return results


class SearchFlights(BaseTool):
    name: str = "search_flights"
    description: str = """Search for flights based on departure airport, arrival airport, and departure time range."""

    def _run(
        self,
        departure_airport: str = None,
        arrival_airport: str = None,
        start_time: date | datetime | None = None,
        end_time: date | datetime | None = None,
        limit: int = 10,
    ) -> str:
        print(
            f"Executing search_flights with departure_airport={departure_airport}, "
            f"arrival_airport={arrival_airport}, start_time={start_time}, end_time={end_time}"
        )
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = "SELECT * FROM flights WHERE 1 = 1"
        params = []
        if departure_airport:
            query += " AND departure_airport = ?"
            params.append(departure_airport)

        if arrival_airport:
            query += " AND arrival_airport = ?"
            params.append(arrival_airport)

        if start_time:
            query += " AND DATE(scheduled_departure) >= DATE(?)"
            params.append(start_time)

        if end_time:
            query += " AND DATE(scheduled_departure) <= DATE(?)"
            params.append(end_time)
        query += " LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()

        return results


class BookFlight(BaseTool):
    name: str = "book_flight"
    description: str = """
    Book a flight using the provided flight number, departure date, and booking reference.
    Use this tool when the user wants to book a flight.
    """

    def _run(
        self,
        config: RunnableConfig,
        flight_no: str,
        departure: date | datetime,
        fare_conditions: str | None = "None",
        meal_preference: str | None = "None",
        special_assistance: str | None = "None",
    ) -> str:
        print(
            f"Executing book_flight with flight_no={flight_no}, book_ref={1234}, fare_conditions={fare_conditions}, meal_preference={meal_preference}, special_assistance={special_assistance}"
        )

        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Get flight details
        query = "SELECT * FROM flights WHERE flight_no = ? AND DATE(scheduled_departure) = DATE(?)"
        cursor.execute(
            query,
            (
                flight_no,
                departure,
            ),
        )
        flight_details = cursor.fetchone()

        print(f"Flight details fetched: {flight_details}")
        if not flight_details:
            raise ValueError(f"Flight with number {flight_no} not found.")

        query = "INSERT INTO tickets (ticket_no, book_ref, passenger_id, flight_no, flight_id) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(
            query,
            (
                uuid.uuid4().hex[:8].upper(),
                "1234",
                passenger_id,
                flight_details[1],
                str(flight_details[0]),
            ),
        )
        conn.commit()
        ticket_no = cursor.lastrowid
        cursor.close()
        conn.close()

        # Get ticket
        # query = (
        #     "SELECT * FROM ticket_flights WHERE flight_id = ? AND fare_conditions = ?"
        # )
        # cursor.execute(query, (flight_details[0], fare_conditions))
        # ticket_details = cursor.fetchone()
        # if not ticket_details:
        #     raise ValueError(f"Ticket for flight {flight_no} not found.")

        # # Book the flight
        # query = (
        #     "INSERT INTO tickets (ticket_no, book_ref, passenger_id) VALUES (?, ?, ?)"
        # )
        # params = [ticket_details[0], "1234", passenger_id]

        # cursor.execute(query, params)
        # conn.commit()
        # ticket_no = cursor.lastrowid

        # # Generate boarding pass
        # boarding_no = uuid.uuid4().hex[:8].upper()
        # seat_no = f"{flight_details[1]}{uuid.uuid4().hex[:4].upper()}"

        # query = "INSERT INTO boarding_passes (ticket_no, flight_id, boarding_no, seat_no) VALUES (?, ?, ?, ?)"
        # params = [ticket_details[0], ticket_details[1], boarding_no, seat_no]
        # cursor.execute(query, params)
        # conn.commit()
        # boarding_pass_id = cursor.lastrowid

        # cursor.close()
        # conn.close()

        return f"Flight booked successfully with ticket no: {ticket_no}"


class CancelFlight(BaseTool):
    name: str = "cancel_flight"
    description: str = """Cancel the user's ticket and remove it from the database."""

    def _run(self, config: RunnableConfig, ticket_no: str) -> str:
        print(f"Executing cancel_flight with ticket_no={ticket_no}")

        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute("SELECT flight_id FROM ticket_flights WHERE ticket_no = ?", (ticket_no,))
        existing_ticket = cursor.fetchone()
        if not existing_ticket:
            cursor.close()
            conn.close()
            return "No existing ticket found for the given ticket number."

        # Check the signed-in user actually has this ticket
        cursor.execute(
            "SELECT ticket_no FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
            (ticket_no, passenger_id),
        )
        current_ticket = cursor.fetchone()
        if not current_ticket:
            cursor.close()
            conn.close()
            return f"Current signed-in passenger with ID {passenger_id} not the owner of ticket {ticket_no}"

        cursor.execute("DELETE FROM tickets WHERE ticket_no = ?", (ticket_no,))
        conn.commit()

        cursor.close()
        conn.close()

        return f"Flight with ticket ID {ticket_no} has been successfully canceled."


class UpdateFlight(BaseTool):
    name: str = "update_flight"
    description: str = """Update the user's ticket to a new valid flight."""

    def _run(
        self,
        config: RunnableConfig,
        ticket_no: str,
        new_flight_id: str,
    ) -> str:
        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT departure_airport, arrival_airport, scheduled_departure FROM flights WHERE flight_id = ?",
            (new_flight_id,),
        )
        new_flight = cursor.fetchone()
        if not new_flight:
            cursor.close()
            conn.close()
            return "Invalid new flight ID provided."
        column_names = [column[0] for column in cursor.description]
        new_flight_dict = dict(zip(column_names, new_flight))
        timezone = pytz.timezone("Etc/GMT-3")
        current_time = datetime.now(tz=timezone)
        departure_time = datetime.strptime(
            new_flight_dict["scheduled_departure"], "%Y-%m-%d %H:%M:%S.%f%z"
        )
        time_until = (departure_time - current_time).total_seconds()
        if time_until < (3 * 3600):
            return f"Not permitted to reschedule to a flight that is less than 3 hours from the current time. Selected flight is at {departure_time}."

        cursor.execute("SELECT flight_id FROM ticket_flights WHERE ticket_no = ?", (ticket_no,))
        current_flight = cursor.fetchone()
        if not current_flight:
            cursor.close()
            conn.close()
            return "No existing ticket found for the given ticket number."

        cursor.execute(
            "SELECT * FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
            (ticket_no, passenger_id),
        )
        current_ticket = cursor.fetchone()
        if not current_ticket:
            cursor.close()
            conn.close()
            return f"Current signed-in passenger with ID {passenger_id} not the owner of ticket {ticket_no}"

        cursor.execute(
            "UPDATE ticket_flights SET flight_id = ? WHERE ticket_no = ?",
            (new_flight_id, ticket_no),
        )
        conn.commit()

        cursor.close()
        conn.close()
        return "Ticket successfully updated to new flight."
