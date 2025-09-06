# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that searches for cheap Ryanair flights between airports near Liège, Belgium. The script finds round-trip flights with a minimum stay duration and displays the cheapest options.

## Dependencies

- `ryanair` - Python package for accessing Ryanair flight data
- `datetime` - Built-in Python module for date manipulation

## Running the Project

```bash
python main.py
```

The script will:
1. Search for flights between predefined airports (LGG, MST, CRL, BRU, EIN, CGN, DUS)
2. Look for round-trips starting from October 1, 2025 with minimum 4-day stays
3. Display the 5 cheapest flight combinations

## Code Architecture

The project consists of a single script (`main.py`) that:

- Defines airport codes for the Liège region
- Configures departure date and minimum stay duration
- Uses nested loops to check all airport combinations
- Calls `ryanair.getReturnFlights()` for each route
- Collects and sorts results by total price
- Handles API errors gracefully with try-except blocks

## Configuration

Key parameters are defined as constants at the top of `main.py`:
- `airports`: List of airport codes to search
- `departure_date`: Initial departure date ('2025-10-01')
- `min_stay_duration`: Minimum stay in days (4)

## Error Handling

The script includes basic error handling that prints error messages when flight searches fail between specific airport pairs, allowing the script to continue processing other routes.