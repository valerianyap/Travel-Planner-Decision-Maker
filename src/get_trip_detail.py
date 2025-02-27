# get prices, distance, and time to go from point A to point B
import json
from get_directions import get_transit_directions
from public_transport_fare_calc import calculate_bus_fare, calculate_mrt_fare


def get_trip_details(route_data, rider_type="Adult", sort_priority="price"):
    trip_details = []
    for route in route_data["routes"]:
        # accumulate the fares for the total price of this trip
        accumulated_price = 0
        tripInfo = ""
        addTripInfo = ""
        for step in route["steps"]:
            if step["travel_mode"] == "TRANSIT":
                departure_stop = step["departure_stop"]
                arrival_stop = step["arrival_stop"]
                if step["line"]["vehicle_type"] == "BUS":
                    bus_number = step["line"]["name"]

                    bus_fare = calculate_bus_fare(departure_stop, arrival_stop, bus_number, rider_type, tripInfo, addTripInfo)

                    # update tripInfo and addTripInfo if the trip is continuous
                    tripInfo = bus_fare["tripInfo"]
                    addTripInfo = bus_fare["addTripInfo"]

                    accumulated_price += int(bus_fare["fare"]) / 100
                
                elif step["line"]["vehicle_type"] == "SUBWAY":
                    mrt_fare = calculate_mrt_fare(departure_stop, arrival_stop, rider_type, tripInfo, addTripInfo)
                
                    # update tripInfo and addTripInfo if the trip is continuous
                    tripInfo = mrt_fare["tripInfo"]
                    addTripInfo = mrt_fare["addTripInfo"]

                    accumulated_price += int(mrt_fare["fare"]) / 100
        
        trip_details.append({
            "price_sgd": accumulated_price,
            "distance_km": route["distance"]["value"] / 1000,
            "duration_minutes": route["duration"]["value"] / 60,
            "departure_time": route["departure_time"].replace("\u202f", " "),
            "arrival_time": route["arrival_time"].replace("\u202f", " "),
            "steps": route["steps"],
        })
    
    # sort priority:
    # - price: minimum price possible
    # - earliest: the earliest arrival
    return sorted(trip_details, key=lambda x: (x["price_sgd"], x["arrival_time"]) if sort_priority == "price" else x["arrival_time"])


if __name__ == "__main__":
    BASE_PATH = "data/googleMaps/trip_detail"
    RIDER_TYPE = "Adult"
    # sort priority:
    # - price: minimum price possible
    # - earliest: the earliest arrival
    SORT_PRIORITY = "price"

    origin = 'Singpost Centre, 10 Eunos Rd 8, Singapore 408600'
    destination = 'Singapore Management University, 81 Victoria St, Singapore 188065'

    route_data = get_transit_directions(origin, destination, output_dir=BASE_PATH)
    trip_details = get_trip_details(route_data, rider_type=RIDER_TYPE, sort_priority=SORT_PRIORITY)

    save_path = f"{BASE_PATH}/priced_trip_details.json"
    with open(save_path, 'w') as f:
        json.dump(trip_details, f, indent=4)

    print(f"Trip Details saved at {save_path}")
