import math
import re
from typing import Annotated

import numexpr
import requests
from langchain_chroma import Chroma
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool
from langchain_openai import OpenAIEmbeddings
from langgraph.types import Command

from schema.models import FlightBookingRequest


def calculator_func(expression: str) -> str:
    """Calculates a math expression using numexpr.

    Useful for when you need to answer questions about math using numexpr.
    This tool is only for math questions and nothing else. Only input
    math expressions.

    Args:
        expression (str): A valid numexpr formatted math expression.

    Returns:
        str: The result of the math expression.
    """

    try:
        local_dict = {"pi": math.pi, "e": math.e}
        output = str(
            numexpr.evaluate(
                expression.strip(),
                global_dict={},  # restrict access to globals
                local_dict=local_dict,  # add common mathematical functions
            )
        )
        return re.sub(r"^\[|\]$", "", output)
    except Exception as e:
        raise ValueError(
            f'calculator("{expression}") raised error: {e}.'
            " Please try again with a valid numerical expression"
        )


calculator: BaseTool = tool(calculator_func)
calculator.name = "Calculator"


# Format retrieved documents
def format_contexts(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def load_chroma_db():
    # Create the embedding function for our project description database
    try:
        embeddings = OpenAIEmbeddings()
    except Exception as e:
        raise RuntimeError(
            "Failed to initialize OpenAIEmbeddings. Ensure the OpenAI API key is set."
        ) from e

    # Load the stored vector database
    chroma_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
    return retriever


def database_search_func(query: str) -> str:
    """Searches chroma_db for information in the company's handbook."""
    # Get the chroma retriever
    retriever = load_chroma_db()

    # Search the database for relevant documents
    documents = retriever.invoke(query)

    # Format the documents into a string
    context_str = format_contexts(documents)

    return context_str


database_search: BaseTool = tool(database_search_func)
database_search.name = "Database_Search"  # Update name with the purpose of your database


CITY_TO_IATA = {
    "new york": "JFK",
    "los angeles": "LAX",
    "chicago": "ORD",
    "mumbai": "BOM",
    "delhi": "DEL",
    "bangalore": "BLR",
    "chennai": "MAA",
    "kolkata": "CCU",
    "hyderabad": "HYD",
}


FLIGHTS_URL = "http://localhost:8000/flights"


class SearchFlightsTool(BaseTool):
    name: str = "search_flights"
    description: str = """
    Searches for flight information using a third-party API.
    Use this tool when the user asks to find flights and you have all the necessary information:
    origin city, destination city, and departure date.
    Optionally takes number of adults, children, travel class, and if it's one-way.
    Do NOT call this tool if origin, destination, or departure date is missing.
    """

    def _run(
        self,
        origin: str,
        destination: str,
        departure: str,
        return_date: str | None = None,
        num_adults: int = 1,
        num_children: int = 0,
        travel_class: str = "economy",
        is_one_way: bool = True,
        **kwargs,
    ) -> str:
        print(
            f"Executing SearchFlightsTool with params: origin={origin}, destination={destination}, date={departure}, adults={num_adults}, children={num_children}, class={travel_class}, one_way={is_one_way}"
        )

        origin_iata = CITY_TO_IATA.get(origin.lower())
        destination_iata = CITY_TO_IATA.get(destination.lower())

        print(origin_iata, destination_iata)

        if not origin_iata:
            return (
                f"Could not find IATA code for origin city: {origin}. Please provide a known city."
            )
        if not destination_iata:
            return f"Could not find IATA code for destination city: {destination}. Please provide a known city."

        params = {
            "origin": origin_iata,
            "destination": destination_iata,
            "departure": departure,
            "return_date": return_date,
            "num_adults": num_adults,
            "num_children": num_children,
            "travel_class": travel_class,
            "is_one_way": is_one_way,
        }

        try:
            response = requests.get(FLIGHTS_URL, params=params)
            response.raise_for_status()
            data = response.json()

            return data

        except Exception as e:
            print(f"Error calling flight API: {e}")
            return f"An error occurred while searching for flights: {e}"


class BookFlightTool(BaseTool):
    name: str = "book_flight"
    description: str = """
    Book a flight using the provided flight details.
    Use this tool when the user has provided all necessary information for booking a flight.
    This includes the flight details, passenger information, and payment details.
    Do NOT call this tool if any required information is missing.
    The flight details should include the origin, destination, departure date, return date (if applicable), number of adults, number of children, and travel class.
    """

    def _run(
        self,
        flight_number: str,
        flight_date: str,
        full_name: str,
        date_of_birth: str,
        gender: str | None = "Not Specified",
        phone_number: str = "None",
        seat_preference: str | None = "None",
        meal_preference: str | None = "None",
        special_assistance: str | None = "None",
        payment_method: str = "None",
        tool_call_id: Annotated[str, InjectedToolCallId] = "None",
    ) -> dict:
        print(f"Executing BookFlightTool for flight_number={flight_number} on {flight_date}")

        params = {
            "flight_number": flight_number,
            "flight_date": flight_date,
            "full_name": full_name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "phone_number": phone_number,
            "seat_preference": seat_preference,
            "meal_preference": meal_preference,
            "special_assistance": special_assistance,
            "payment_method": payment_method,
        }
        try:
            schema = FlightBookingRequest(**params)
            print(f"Booking flight with params: {schema.model_dump()}")
            response = requests.post(FLIGHTS_URL, json=schema.model_dump())
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"Error calling flight API: {e}")
            return f"An error occurred while booking the flight: {e}"


@tool
def update_state(
    budget: str | None,
    flight_number: str | None,
    hotel_id: str | None,
    no_of_adults: int | None,
    no_of_children: int | None,
    travel_class: str | None,
    is_one_way: bool | None,
    check_in: str | None,
    check_out: str | None,
    origin: str | None,
    destination: str | None,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> str:
    """Request assistance from a human."""
    payload = {
        "budget": budget,
        "flight_number": flight_number,
        "hotel_id": hotel_id,
        "no_of_adults": no_of_adults,
        "no_of_children": no_of_children,
        "travel_class": travel_class,
        "is_one_way": is_one_way,
        "check_in": check_in,
        "check_out": check_out,
        "origin": origin,
        "destination": destination,
    }
    # human_response = interrupt({
    #     "question": "Please verify trip parameters",
    #     **payload
    # })

    # corrections: dict = {}
    # for key, value in payload.items():
    #     if key in human_response and human_response[key] != value:
    #         corrections[key] = human_response[key]

    # message_text = (
    #     "All details correct"
    #     if not corrections
    #     else f"Corrections: {corrections}"
    # )

    return Command(
        update={
            **payload,
            "messages": [ToolMessage(content="Updated State", tool_call_id=tool_call_id)],
        }
    )
