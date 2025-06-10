from typing import Annotated, TypedDict

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from agents.tools import BookFlightTool, SearchFlightsTool

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


class FlightSearchState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    remaining_steps: RemainingSteps
    session_id: str  # Links to shared session store
    raw_input: str  # Original user query text
    origin: str  # Validated city name
    destination: str  # Validated city name
    depart_date: str  # YYYY-MM-DD
    return_date: str  # YYYY-MM-DD, if round-trip
    is_one_way: bool  # True if one-way search
    flight_options: list[dict]  # Each dict: {flight_number, depart_time, price, …}
    no_results: bool  # True if SearchFlightsTool returned none


@tool
def update_search_flights_agent(
    origin: str | None,
    destination: str | None,
    depart_date: str | None,
    return_date: str | None,
    is_one_way: bool | None,
    flight_options: list[dict] | None,
    no_results: bool | None,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> str:
    """
    This tool updates the state of the flight search agent.
    It is called when the user selects a flight option or when the search results are updated.
    It takes the following parameters:
    - origin: The origin city for the flight search.
    - destination: The destination city for the flight search.
    - depart_date: The departure date for the flight search.
    - return_date: The return date for the flight search (if applicable).
    - is_one_way: A boolean indicating if the flight search is one-way or round-trip.
    - flight_options: A list of flight options returned by the SearchFlightsTool.
    - no_results: A boolean indicating if no results were found by the SearchFlightsTool.
    - tool_call_id: The ID of the tool call for tracking purposes.
    """
    payload = {
        "origin": origin,
        "destination": destination,
        "depart_date": depart_date,
        "return_date": return_date,
        "is_one_way": is_one_way,
        "flight_options": flight_options,
        "no_results": no_results,
    }

    return Command(
        update={
            **payload,
            "messages": [ToolMessage(content="Updated State", tool_call_id=tool_call_id)],
        }
    )


search_flights_agent = create_react_agent(
    model=model,
    state_schema=FlightSearchState,
    tools=[SearchFlightsTool(), update_search_flights_agent],
    prompt=(
        """
        You are a flight search agent. Your task is to assist users in finding flights based on their travel preferences.
        You will receive user queries and you need to extract the relevant information such as origin, destination, and travel dates.
        You will also need to handle the case where the user provides incomplete or incorrect information.
        You will use the SearchFlightsTool to find flights based on the provided information. In the origin and destination, dont put the IATA code, but the city name.
        Also transfer control back to supervisor only when the user is satisfied with the flight options.
        
        After user select a flight, you will call the update_search_flights_agent tool to update the state with the selected flight options.

        Your task is not to book the flight, but to assist the user in finding the best options.
        """
    ),
    name="search_flights_agent",
    checkpointer=MemorySaver(),
)


class BookFlightState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    remaining_steps: RemainingSteps
    session_id: str
    flight_number: str
    flight_date: str
    full_name: str
    date_of_birth: str
    phone_number: str
    gender: str
    seat_preference: str
    meal_preference: str
    special_assistance: str
    payment_method: str
    missing_fields: list[str]


@tool
def update_book_flight_agent(
    flight_number: str | None,
    full_name: str | None,
    date_of_birth: str | None,
    phone_number: str | None,
    gender: str | None,
    seat_preference: str | None,
    meal_preference: str | None,
    special_assistance: str | None,
    payment_method: str | None,
    missing_fields: list[str] | None,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> str:
    """
    Update the state of the flight booking agent with the provided information.
    This function is used to update the state of the agent with the selected flight and passenger details.
    The function takes the parameters as follows:
    - flight_number: The flight selected by the user.
    - full_name: The full name of the passenger.
    - date_of_birth: The date of birth of the passenger.
    - phone_number: The phone number of the passenger.
    - gender: The gender of the passenger.
    - seat_preference: The seat preference of the passenger (e.g., aisle, window).
    - meal_preference: The meal preference of the passenger (e.g., vegetarian).
    - special_assistance: Any special assistance required by the passenger.
    - payment_method: The payment method selected by the passenger.
    """
    payload = {
        "flight_number": flight_number,
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "phone_number": phone_number,
        "gender": gender,
        "seat_preference": seat_preference,
        "meal_preference": meal_preference,
        "special_assistance": special_assistance,
        "payment_method": payment_method,
        "missing_fields": missing_fields,
    }

    return Command(
        update={
            **payload,
            "messages": [ToolMessage(content="Updated State", tool_call_id=tool_call_id)],
        }
    )


book_flights_agent = create_react_agent(
    model=model,
    tools=[BookFlightTool(), update_book_flight_agent],
    state_schema=BookFlightState,
    prompt=(
        """
        You are a flight booking agent. Your task is to assist users in booking flights based on their travel preferences.
        You will receive user queries and you need to extract the relevant information.
        You will also need to handle the case where the user provides incomplete or incorrect information.
        You will use the BookFlightTool to book flights based on the provided information.
        After the BookFlightTool is called, you will compulsorily call the update_book_flight_agent tool to update the state with the booking confirmation.
        If the user provides a valid query, you will return the booking confirmation.
        If the user provides an invalid query, you will ask clarifying questions to gather the necessary information.
        """
    ),
    name="book_flights_agent",
    checkpointer=MemorySaver(),
)
