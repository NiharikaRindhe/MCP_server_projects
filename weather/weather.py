# from typing import Any
# import httpx
# import argparse
# import asyncio
# import logging
# import sys
# from mcp.server.fastmcp import FastMCP

# # Setup logging
# def setup_logging():
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s [%(levelname)s] %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S"
#     )

# # Initialize FastMCP server
# mcp = FastMCP("weather")

# # Constants
# NWS_API_BASE = "https://api.weather.gov"
# USER_AGENT = "weather-app/1.0"

# async def make_nws_request(url: str) -> dict[str, Any] | None:
#     """Make a request to the NWS API with proper error handling."""
#     headers = {
#         "User-Agent": USER_AGENT,
#         "Accept": "application/geo+json"
#     }
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=30.0)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             logging.error(f"Failed NWS request to {url}: {e}")
#             return None

# def format_alert(feature: dict) -> str:
#     """Format an alert feature into a readable string."""
#     props = feature.get("properties", {})
#     return (
#         f"Event: {props.get('event', 'Unknown')}\n"
#         f"Area: {props.get('areaDesc', 'Unknown')}\n"
#         f"Severity: {props.get('severity', 'Unknown')}\n"
#         f"Description: {props.get('description', 'No description available')}\n"
#         f"Instructions: {props.get('instruction', 'No specific instructions provided')}"
#     )

# @mcp.tool()
# async def get_alerts(state: str) -> str:
#     """Get weather alerts for a US state."""
#     url = f"{NWS_API_BASE}/alerts/active/area/{state}"
#     data = await make_nws_request(url)

#     if not data or "features" not in data:
#         return "Unable to fetch alerts or no alerts found."

#     if not data["features"]:
#         return "No active alerts for this state."

#     alerts = [format_alert(feature) for feature in data["features"]]
#     return "\n---\n".join(alerts)

# @mcp.tool()
# async def get_forecast(latitude: float, longitude: float) -> str:
#     """Get weather forecast for a location."""
#     points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
#     points_data = await make_nws_request(points_url)

#     if not points_data:
#         return "Unable to fetch forecast data for this location."

#     forecast_url = points_data["properties"].get("forecast")
#     forecast_data = await make_nws_request(forecast_url)

#     if not forecast_data or "properties" not in forecast_data:
#         return "Unable to fetch detailed forecast."

#     periods = forecast_data["properties"].get("periods", [])
#     forecasts = []
#     for period in periods[:5]:  # Only show next 5 periods
#         forecasts.append(
#             f"{period['name']}:\n"
#             f"  Temperature: {period['temperature']}°{period['temperatureUnit']}\n"
#             f"  Wind: {period['windSpeed']} {period['windDirection']}\n"
#             f"  Forecast: {period['detailedForecast']}"
#         )
#     return "\n---\n".join(forecasts)

# # Command-line interface for testing manually
# def main_cli():
#     parser = argparse.ArgumentParser(description="Weather MCP Server CLI")
#     sub = parser.add_subparsers(dest="command")

#     # Alerts subcommand
#     parser_alerts = sub.add_parser("alerts", help="Get state alerts")
#     parser_alerts.add_argument("state", help="Two-letter state code (e.g. CA)")

#     # Forecast subcommand
#     parser_fc = sub.add_parser("forecast", help="Get forecast for lat/lon")
#     parser_fc.add_argument("latitude", type=float, help="Latitude")
#     parser_fc.add_argument("longitude", type=float, help="Longitude")

#     args = parser.parse_args()

#     if args.command == "alerts":
#         result = asyncio.run(get_alerts(args.state.upper()))
#     elif args.command == "forecast":
#         result = asyncio.run(get_forecast(args.latitude, args.longitude))
#     else:
#         parser.print_help()
#         return

#     print(result)

# if __name__ == "__main__":
#     setup_logging()
    
#     # Command-line test
#     if len(sys.argv) > 1 and sys.argv[1] in ("alerts", "forecast"):
#         main_cli()
#     else:
#         # If no CLI commands are passed, run the MCP server
#         logging.info("🚀 Weather MCP server running on stdio…")
#         mcp.run(transport="stdio")


# 2
import tkinter as tk
from tkinter import messagebox
import asyncio
import logging
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Setup logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
VALID_STATES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"}

# Function to make requests to the NWS API
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logging.error(f"Request failed: {e}")
        return {"error": "Failed to make request. Please check the API or your internet connection."}
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error: {e}")
        return {"error": "Received an invalid response from the weather service."}
    except Exception as e:
        logging.error(f"Unknown error: {e}")
        return {"error": "Something went wrong. Please try again later."}

# Validate state codes
def validate_state(state: str) -> bool:
    return state.upper() in VALID_STATES

# Format alerts into readable text
def format_alert(feature: dict) -> str:
    props = feature.get("properties", {})
    alert_text = (
        f"Event: {props.get('event', 'Unknown')}\n"
        f"Area: {props.get('areaDesc', 'Unknown')}\n"
        f"Severity: {props.get('severity', 'Unknown')}\n"
        f"Description: {props.get('description', 'No description available')}\n"
        f"Instructions: {props.get('instruction', 'No specific instructions provided')}"
    )
    return alert_text

# MCP tool for getting weather alerts
@mcp.tool()
async def get_alerts(state: str) -> str:
    if not validate_state(state):
        return "Invalid state code. Please enter a valid two-letter state code (e.g. CA, NY)."
    
    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)
    
    if "error" in data:
        return data["error"]

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

# MCP tool for getting weather forecast
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data or "error" in points_data:
        return "Unable to fetch forecast data for this location. Please check the coordinates."

    forecast_url = points_data["properties"].get("forecast")
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data or "properties" not in forecast_data:
        return "Unable to fetch detailed forecast."

    periods = forecast_data["properties"].get("periods", [])
    if not periods:
        return "No forecast periods available for this location."

    forecasts = []
    for period in periods[:5]:
        forecasts.append(
            f"{period['name']}:\n"
            f"  Temperature: {period['temperature']}°{period['temperatureUnit']}\n"
            f"  Wind: {period['windSpeed']} {period['windDirection']}\n"
            f"  Forecast: {period['detailedForecast']}"
        )
    return "\n---\n".join(forecasts)

# WeatherApp UI using Tkinter
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather MCP Server")
        
        # State input for alerts
        self.state_label = tk.Label(root, text="Enter State (e.g., CA):")
        self.state_label.grid(row=0, column=0)

        self.state_entry = tk.Entry(root)
        self.state_entry.grid(row=0, column=1)

        self.alert_button = tk.Button(root, text="Get Alerts", command=self.fetch_alerts)
        self.alert_button.grid(row=1, column=0, columnspan=2)

        # Latitude and longitude input for forecast
        self.latitude_label = tk.Label(root, text="Enter Latitude:")
        self.latitude_label.grid(row=2, column=0)

        self.latitude_entry = tk.Entry(root)
        self.latitude_entry.grid(row=2, column=1)

        self.longitude_label = tk.Label(root, text="Enter Longitude:")
        self.longitude_label.grid(row=3, column=0)

        self.longitude_entry = tk.Entry(root)
        self.longitude_entry.grid(row=3, column=1)

        self.forecast_button = tk.Button(root, text="Get Forecast", command=self.fetch_forecast)
        self.forecast_button.grid(row=4, column=0, columnspan=2)

        # Display the result in a text box
        self.result_text = tk.Text(root, height=10, width=50)
        self.result_text.grid(row=5, column=0, columnspan=2)

    def fetch_alerts(self):
        state = self.state_entry.get().upper()
        if state:
            result = asyncio.run(get_alerts(state))
            self.display_result(result)
        else:
            messagebox.showerror("Input Error", "Please enter a valid state code.")

    def fetch_forecast(self):
        try:
            lat = float(self.latitude_entry.get())
            lon = float(self.longitude_entry.get())
            result = asyncio.run(get_forecast(lat, lon))
            self.display_result(result)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid latitude and longitude.")

    def display_result(self, result):
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        self.result_text.insert(tk.END, result)  # Insert new result

# Main function to run the app
if __name__ == "__main__":
    setup_logging()  # Set up logging
    root = tk.Tk()  # Create Tkinter root window
    app = WeatherApp(root)  # Instantiate WeatherApp
    root.mainloop()  # Run the app
