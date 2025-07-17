test_sol = [[[[0, []], [6, [6, 10, 3, 5]], [10, []], [3, []], [5, []], [7, [7, 4, 8]], [8, []], [4, []]], [[0, [9]], [9, []], [0, [1]], [2, [2]], [1, []]]], [[[2, [2]], [6, [6, 10, 3, 5]]], [[7, [7, 4, 8]]]]]

# Customer data: {customer_id: (release_time, X, Y)}
# Customer IDs are 1-10, corresponding to indices in the solution
data = {
    1: (65, 16.03, 1.13),
    2: (58, 9.08, 2.10), 
    3: (23, 13.68, 19.95),
    4: (57, 4.21, 12.80),
    5: (32, 13.71, 15.86),
    6: (39, 17.11, 10.61),
    7: (63, 9.96, 15.37),
    8: (40, 6.44, 14.94),
    9: (13, 7.64, 15.92),
    10: (24, 14.70, 14.36)  # Additional customer if needed
}

# Depot location (from the description: center at (10, 10))
depot = (10, 10)

# Parameters from the description
truck_speed = 30  # km/h
drone_speed = 60  # km/h
service_time = 3  # minutes per customer
drone_service_time = 5  # minutes (δm = δd = 5 min)
truck_service_time = 5  # minutes (δt = 5 min)

# Drone parameters
num_drones = 2  # Number of drones available
drone_capacity = 2  # Q = 2 orders per drone (as mentioned in the description for small instances)

import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch
import matplotlib.patches as mpatches

def manhattan_distance(point1, point2):
    """Calculate Manhattan distance between two points (used for trucks)"""
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

def euclidean_distance(point1, point2):
    """Calculate Euclidean distance between two points (used for drones)"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def calculate_travel_time(distance, speed):
    """Calculate travel time in minutes given distance (km) and speed (km/h)"""
    return (distance / speed) * 60  # Convert to minutes

def evaluate_truck_route(route, data, depot):
    """
    Evaluate a truck route and return total time
    Route format: list of [customer_id, drone_customers_list]
    """
    total_time = 0
    current_location = depot
    
    for stop in route:
        customer_id = stop[0]
        if customer_id == 0:  # Depot
            continue
            
        # Travel to customer
        if customer_id in data:
            customer_location = data[customer_id]
            distance = manhattan_distance(current_location, customer_location)
            travel_time = calculate_travel_time(distance, truck_speed)
            total_time += travel_time
            
            # Service time
            total_time += service_time
            current_location = customer_location
    
    # Return to depot
    distance = manhattan_distance(current_location, depot)
    travel_time = calculate_travel_time(distance, truck_speed)
    total_time += travel_time
    
    return total_time

def evaluate_drone_deliveries(drone_customers, truck_location, data, depot):
    """
    Evaluate drone deliveries from a truck location
    """
    if not drone_customers:
        return 0
    
    total_time = 0
    
    for customer_id in drone_customers:
        if customer_id in data:
            customer_location = data[customer_id]
            # Drone flies from truck to customer and back
            distance_to_customer = euclidean_distance(truck_location, customer_location)
            distance_back = euclidean_distance(customer_location, truck_location)
            
            travel_time = calculate_travel_time(distance_to_customer + distance_back, drone_speed)
            total_time += travel_time + drone_service_time
    
    return total_time

def calculate_fitness(solution, data, depot):
    """
    Calculate fitness for a solution with resupply logic
    - Trucks must receive packages from depot or drone resupply before delivering
    - Solution format: [truck_routes, drone_resupply_assignments]
    """
    if not solution or len(solution) == 0:
        return float('inf')
    
    print(f"DEBUG: Solution structure: {solution}")
    print(f"DEBUG: Solution length: {len(solution)}")
    print(f"DEBUG: Available customers in data: {list(data.keys())}")
    print(f"DEBUG: Number of drones: {num_drones}, Drone capacity: {drone_capacity}")
    
    # Parse solution components
    truck_routes = solution[0] if len(solution) > 0 else []
    drone_resupply = solution[1] if len(solution) > 1 else []
    
    print(f"DEBUG: Truck routes: {truck_routes}")
    print(f"DEBUG: Number of trucks: {len(truck_routes)}")
    print(f"DEBUG: Drone resupply assignments: {drone_resupply}")
    
    if not truck_routes:
        return float('inf')
    
    max_completion_time = 0
    
    # Initialize drone availability tracker
    drone_available_time = {i: 0 for i in range(num_drones)}
    
    # Track which customers need resupply and when packages are available
    resupply_times = {}  # customer_id -> time when package is available at truck
    
    # Process drone resupply assignments first
    print(f"\nDEBUG: Processing drone resupply assignments...")
    for resupply_idx, resupply_assignment in enumerate(drone_resupply):
        if not resupply_assignment or len(resupply_assignment) < 1:
            continue
            
        # Each resupply assignment: [[truck_stop], [customers_to_resupply]]
        truck_stop_info = resupply_assignment[0] if len(resupply_assignment) > 0 else []
        customers_to_resupply = resupply_assignment[1] if len(resupply_assignment) > 1 else []
        
        if not truck_stop_info:
            truck_stop_info = customers_to_resupply  # Sometimes format is just [customers]
            customers_to_resupply = truck_stop_info
        
        print(f"DEBUG: Resupply {resupply_idx}: truck_stop={truck_stop_info}, customers={customers_to_resupply}")
        
        # Mark these customers as needing resupply
        for customer_id in customers_to_resupply:
            if customer_id in data:
                resupply_times[customer_id] = float('inf')  # Will be updated when drone delivers
    
    # Evaluate each truck route
    for truck_idx, route in enumerate(truck_routes):
        if not route:
            continue
            
        print(f"\nDEBUG: Processing truck {truck_idx + 1}, route: {route}")
        
        current_time = 0
        current_pos = depot
        truck_inventory = set()  # Customers truck has packages for
        
        # At depot, truck can pick up packages for customers not requiring resupply
        for stop in route:
            if isinstance(stop, list) and len(stop) > 0:
                customer_id = stop[0]
                if customer_id != 0 and customer_id not in resupply_times:
                    truck_inventory.add(customer_id)
                    print(f"DEBUG: Truck {truck_idx + 1} picks up package for customer {customer_id} at depot")
        
        for stop_idx, stop in enumerate(route):
            if not isinstance(stop, list) or len(stop) < 1:
                continue
                
            customer_id = stop[0]
            drone_customers = stop[1] if len(stop) > 1 else []
            
            print(f"DEBUG: Stop {stop_idx + 1}: Customer {customer_id}, Drone resupply for: {drone_customers}")
            
            # Skip depot
            if customer_id == 0:
                print(f"DEBUG: At depot")
                continue
                
            # Get customer data
            if customer_id not in data:
                print(f"WARNING: Customer {customer_id} not found in data")
                continue
                
            customer_data = data[customer_id]
            release_time = customer_data[0]
            customer_location = (customer_data[1], customer_data[2])
            
            # Travel to customer location
            distance = manhattan_distance(current_pos, customer_location)
            travel_time = calculate_travel_time(distance, truck_speed)
            current_time += travel_time
            
            print(f"DEBUG: Truck arrives at location of customer {customer_id} at T+{current_time:.1f}")
            
            # Handle drone resupply operations at this location
            if drone_customers:
                print(f"DEBUG: Processing drone resupply for customers: {drone_customers}")
                
                # Process drone deliveries from depot to truck at this location
                for i in range(0, len(drone_customers), drone_capacity):
                    batch = drone_customers[i:i + drone_capacity]
                    
                    # Find available drone
                    earliest_drone_id = min(drone_available_time, key=drone_available_time.get)
                    earliest_available_time = drone_available_time[earliest_drone_id]
                    
                    # Drone starts from depot when available
                    drone_start_time = earliest_available_time
                    
                    # Check release times for packages
                    for dc in batch:
                        if dc in data:
                            drone_start_time = max(drone_start_time, data[dc][0])
                    
                    # Drone flies from depot to truck location
                    depot_to_truck_distance = euclidean_distance(depot, customer_location)
                    drone_flight_time = calculate_travel_time(depot_to_truck_distance, drone_speed)
                    
                    # Drone arrival time at truck
                    drone_arrival_time = drone_start_time + drone_flight_time + drone_service_time
                    
                    # Update resupply times
                    for dc in batch:
                        if dc in resupply_times:
                            resupply_times[dc] = drone_arrival_time
                            truck_inventory.add(dc)
                            print(f"DEBUG: Drone {earliest_drone_id} delivers package for customer {dc} to truck at T+{drone_arrival_time:.1f}")
                    
                    # Drone returns to depot
                    drone_return_time = drone_arrival_time + drone_flight_time
                    drone_available_time[earliest_drone_id] = drone_return_time
                    
                    print(f"DEBUG: Drone {earliest_drone_id} returns to depot at T+{drone_return_time:.1f}")
            
            # Check if truck has package for this customer
            if customer_id in truck_inventory:
                # Wait for package if it's being resupplied
                if customer_id in resupply_times:
                    wait_until = resupply_times[customer_id]
                    if current_time < wait_until:
                        print(f"DEBUG: Truck waits for resupply until T+{wait_until:.1f}")
                        current_time = wait_until
                
                # Also wait for customer release time
                current_time = max(current_time, release_time)
                
                # Deliver to customer
                current_time += service_time
                truck_inventory.remove(customer_id)
                print(f"DEBUG: Truck delivers to customer {customer_id} at T+{current_time:.1f}")
            else:
                print(f"WARNING: Truck doesn't have package for customer {customer_id}")
            
            current_pos = customer_location
        
        # Return to depot
        distance = manhattan_distance(current_pos, depot)
        travel_time = calculate_travel_time(distance, truck_speed)
        current_time += travel_time
        
        print(f"DEBUG: Truck {truck_idx + 1} returns to depot at T+{current_time:.1f}")
        max_completion_time = max(max_completion_time, current_time)
    
    # Check final drone completion times
    final_drone_times = max(drone_available_time.values()) if drone_available_time else 0
    max_completion_time = max(max_completion_time, final_drone_times)
    
    print(f"\nDEBUG: Drone availability times: {drone_available_time}")
    print(f"DEBUG: Final fitness (max completion time): {max_completion_time:.1f} minutes")
    return max_completion_time

def visualize_solution(solution, data, depot, title="VRP with Drones Solution"):
    """
    Visualize the solution with routes and timeline
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Route visualization
    plot_routes(solution, data, depot, ax1, title)
    
    # Plot 2: Timeline
    plot_timeline(solution, data, depot, ax2)
    
    plt.tight_layout()
    plt.show()

def plot_routes(solution, data, depot, ax, title):
    """
    Plot the routes on a map
    """
    ax.set_title(title)
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.grid(True, alpha=0.3)
    
    # Plot depot
    ax.plot(depot[0], depot[1], 's', color='red', markersize=12, label='Depot')
    ax.annotate('Depot\n(10,10)', (depot[0], depot[1]), xytext=(5, 5), 
                textcoords='offset points', fontsize=8, ha='left')
    
    # Plot customers
    for customer_id, customer_data in data.items():
        location = (customer_data[1], customer_data[2])  # (X, Y)
        release_time = customer_data[0]
        ax.plot(location[0], location[1], 'o', color='blue', markersize=8)
        ax.annotate(f'{customer_id}\n(r={release_time})', location, xytext=(3, 3), 
                   textcoords='offset points', fontsize=8)
    
    if not solution or len(solution) == 0:
        ax.legend()
        return
    
    # Colors for different trucks
    colors = ['green', 'orange', 'purple', 'brown', 'pink']
    
    # Parse truck routes - first element contains truck routes
    truck_routes = solution[0] if len(solution) > 0 else []
    
    # Plot truck routes
    for truck_idx, route in enumerate(truck_routes):
        if not route:
            continue
            
        color = colors[truck_idx % len(colors)]
        current_pos = depot
        route_x = [depot[0]]
        route_y = [depot[1]]
        
        # Calculate cumulative time
        cumulative_time = 0
        
        for stop in route:
            if not isinstance(stop, list) or len(stop) < 1:
                continue
                
            customer_id = stop[0]
            drone_customers = stop[1] if len(stop) > 1 else []
            
            # Skip depot entries
            if customer_id == 0:
                continue
                
            if customer_id not in data:
                continue
                
            customer_data = data[customer_id]
            release_time = customer_data[0]
            customer_location = (customer_data[1], customer_data[2])
            
            # Wait for release time if necessary
            cumulative_time = max(cumulative_time, release_time)
            
            # Calculate travel time to this customer
            distance = manhattan_distance(current_pos, customer_location)
            travel_time = calculate_travel_time(distance, truck_speed)
            cumulative_time += travel_time
            
            route_x.append(customer_location[0])
            route_y.append(customer_location[1])
            
            # Annotate time at customer
            ax.annotate(f'T+{cumulative_time:.1f}min', 
                       customer_location, xytext=(-10, -15), 
                       textcoords='offset points', fontsize=7, 
                       color=color, weight='bold')
            
            # Service time
            cumulative_time += service_time
            
            # Plot drone deliveries from this location
            if drone_customers:
                plot_drone_routes(ax, customer_location, drone_customers, data, color)
            
            current_pos = customer_location
        
        # Return to depot
        route_x.append(depot[0])
        route_y.append(depot[1])
        
        # Plot truck route
        ax.plot(route_x, route_y, '-', color=color, linewidth=2, 
                label=f'Truck {truck_idx + 1}', alpha=0.7)
        
        # Add arrows to show direction
        for i in range(len(route_x) - 1):
            arrow = FancyArrowPatch((route_x[i], route_y[i]), 
                                  (route_x[i+1], route_y[i+1]),
                                  arrowstyle='->', mutation_scale=15, 
                                  color=color, alpha=0.6)
            ax.add_patch(arrow)
    
    ax.legend()
    ax.set_aspect('equal', adjustable='box')

def plot_drone_routes(ax, truck_location, drone_customers, data, truck_color):
    """
    Plot drone routes from truck location
    """
    for customer_id in drone_customers:
        if customer_id not in data:
            continue
            
        customer_data = data[customer_id]
        drone_location = (customer_data[1], customer_data[2])
        
        # Plot drone route (dashed line)
        ax.plot([truck_location[0], drone_location[0]], 
               [truck_location[1], drone_location[1]], 
               '--', color=truck_color, alpha=0.5, linewidth=1)
        
        # Plot return route
        ax.plot([drone_location[0], truck_location[0]], 
               [drone_location[1], truck_location[1]], 
               '--', color=truck_color, alpha=0.3, linewidth=1)
        
        # Mark drone customer
        ax.plot(drone_location[0], drone_location[1], 
               '^', color=truck_color, markersize=6, alpha=0.7)

def plot_timeline(solution, data, depot, ax):
    """
    Plot timeline of operations
    """
    ax.set_title('Timeline của các hoạt động')
    ax.set_xlabel('Thời gian (phút)')
    ax.set_ylabel('Truck/Drone')
    
    if not solution or len(solution) == 0:
        ax.text(0.5, 0.5, 'No solution to plot', ha='center', va='center', 
                transform=ax.transAxes)
        return
    
    # Parse truck routes - first element contains truck routes
    truck_routes = solution[0] if len(solution) > 0 else []
    colors = ['green', 'orange', 'purple', 'brown', 'pink']
    
    y_positions = []
    labels = []
    
    for truck_idx, route in enumerate(truck_routes):
        if not route:
            continue
            
        color = colors[truck_idx % len(colors)]
        y_pos = truck_idx
        y_positions.append(y_pos)
        labels.append(f'Truck {truck_idx + 1}')
        
        current_time = 0
        current_pos = depot
        
        # Timeline events
        events = [(0, 'Start at Depot', depot)]
        
        for stop in route:
            if not isinstance(stop, list) or len(stop) < 1:
                continue
                
            customer_id = stop[0]
            drone_customers = stop[1] if len(stop) > 1 else []
            
            # Skip depot entries
            if customer_id == 0:
                continue
                
            if customer_id not in data:
                continue
                
            customer_data = data[customer_id]
            release_time = customer_data[0]
            customer_location = (customer_data[1], customer_data[2])
            
            # Wait for release time if necessary
            current_time = max(current_time, release_time)
            
            # Travel time
            distance = manhattan_distance(current_pos, customer_location)
            travel_time = calculate_travel_time(distance, truck_speed)
            current_time += travel_time
            
            events.append((current_time, f'Arrive at {customer_id}', customer_location))
            
            # Service time
            current_time += service_time
            events.append((current_time, f'Complete service {customer_id}', customer_location))
            
            # Drone operations
            if drone_customers:
                for drone_customer in drone_customers:
                    if drone_customer not in data:
                        continue
                        
                    drone_data = data[drone_customer]
                    drone_location = (drone_data[1], drone_data[2])
                    drone_release = drone_data[0]
                    
                    drone_start_time = max(current_time, drone_release)
                    drone_distance = euclidean_distance(customer_location, drone_location)
                    drone_time = calculate_travel_time(drone_distance * 2, drone_speed) + drone_service_time
                    drone_completion_time = drone_start_time + drone_time
                    
                    events.append((drone_completion_time, f'Drone delivery {drone_customer}', drone_location))
            
            current_pos = customer_location
        
        # Return to depot
        distance = manhattan_distance(current_pos, depot)
        travel_time = calculate_travel_time(distance, truck_speed)
        current_time += travel_time
        events.append((current_time, 'Return to Depot', depot))
        
        # Plot timeline
        times = [event[0] for event in events]
        ax.barh(y_pos, max(times), height=0.3, color=color, alpha=0.3)
        
        # Plot events
        for time, event, location in events:
            ax.plot(time, y_pos, 'o', color=color, markersize=4)
            if 'Arrive' in event or 'Start' in event or 'Return' in event:
                ax.annotate(event, (time, y_pos), xytext=(5, 0), 
                           textcoords='offset points', fontsize=7, 
                           rotation=0, ha='left', va='center')
    
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, None)

def analyze_solution_details(solution, data, depot):
    """
    Print detailed analysis of the solution with drone queue management
    """
    print("="*60)
    print("PHÂN TÍCH CHI TIẾT SOLUTION")
    print("="*60)
    
    if not solution:
        print("Không có solution để phân tích")
        return
    
    # Parse truck routes - first element contains truck routes
    truck_routes = solution[0] if len(solution) > 0 else []
    drone_resupply = solution[1] if len(solution) > 1 else []
    
    print(f"Số lượng drone: {num_drones}")
    print(f"Sức chứa drone: {drone_capacity} khách hàng/chuyến")
    print(f"Drone resupply assignments: {drone_resupply}")
    
    total_time = 0
    total_distance = 0
    
    # Initialize drone availability tracker
    drone_available_time = {i: 0 for i in range(num_drones)}
    drone_trips = {i: [] for i in range(num_drones)}  # Track trips for each drone
    
    for truck_idx, route in enumerate(truck_routes):
        print(f"\n--- TRUCK {truck_idx + 1} ---")
        
        if not route:
            print("Route trống")
            continue
            
        current_time = 0
        current_pos = depot
        truck_distance = 0
        
        print(f"T+{current_time:5.1f}: Bắt đầu tại Depot {depot}")
        
        for stop in route:
            if not isinstance(stop, list) or len(stop) < 1:
                continue
                
            customer_id = stop[0]
            drone_customers = stop[1] if len(stop) > 1 else []
            
            # Skip depot entries
            if customer_id == 0:
                continue
                
            if customer_id not in data:
                print(f"WARNING: Customer {customer_id} not found")
                continue
                
            customer_data = data[customer_id]
            release_time = customer_data[0]
            customer_location = (customer_data[1], customer_data[2])
            
            # Wait for release time if necessary
            if current_time < release_time:
                print(f"T+{current_time:5.1f}: Chờ release time của customer {customer_id}")
                current_time = release_time
                print(f"T+{current_time:5.1f}: Customer {customer_id} được release")
            
            # Travel
            distance = manhattan_distance(current_pos, customer_location)
            travel_time = calculate_travel_time(distance, truck_speed)
            current_time += travel_time
            truck_distance += distance
            
            print(f"T+{current_time:5.1f}: Đến customer {customer_id} tại {customer_location}")
            print(f"         Release time: {release_time}, Khoảng cách: {distance:.2f}km, Thời gian di chuyển: {travel_time:.1f}min")
            
            # Service
            current_time += service_time
            print(f"T+{current_time:5.1f}: Hoàn thành phục vụ customer {customer_id}")
            
            # Drone deliveries
            if drone_customers:
                print(f"         Drone giao hàng cho: {drone_customers}")
                
                # Check capacity
                if len(drone_customers) > drone_capacity:
                    print(f"         CẢNH BÁO: Số khách hàng drone ({len(drone_customers)}) vượt quá sức chứa ({drone_capacity})")
                
                # Process in batches
                for i in range(0, len(drone_customers), drone_capacity):
                    batch = drone_customers[i:i + drone_capacity]
                    
                    # Find available drone
                    earliest_drone_id = min(drone_available_time, key=drone_available_time.get)
                    earliest_available_time = drone_available_time[earliest_drone_id]
                    
                    print(f"         Batch {i//drone_capacity + 1}: {batch}")
                    print(f"         Drone {earliest_drone_id} sẵn sàng tại T+{earliest_available_time:.1f}")
                    
                    drone_start_time = max(current_time, earliest_available_time)
                    batch_time = 0
                    drone_pos = customer_location
                    
                    for drone_customer in batch:
                        if drone_customer not in data:
                            continue
                            
                        drone_data = data[drone_customer]
                        drone_customer_location = (drone_data[1], drone_data[2])
                        drone_release = drone_data[0]
                        
                        # Wait for release
                        drone_start_time = max(drone_start_time, drone_release)
                        
                        # Travel to customer
                        distance_to_customer = euclidean_distance(drone_pos, drone_customer_location)
                        travel = calculate_travel_time(distance_to_customer, drone_speed)
                        batch_time += travel + drone_service_time
                        
                        print(f"         -> Drone {earliest_drone_id} đến {drone_customer} tại {drone_customer_location}")
                        print(f"            Release: {drone_release}, Khoảng cách: {distance_to_customer:.2f}km, Thời gian: {travel:.1f}min")
                        
                        drone_pos = drone_customer_location
                    
                    # Return to truck
                    return_distance = euclidean_distance(drone_pos, customer_location)
                    return_time = calculate_travel_time(return_distance, drone_speed)
                    batch_time += return_time
                    
                    drone_completion_time = drone_start_time + batch_time
                    drone_available_time[earliest_drone_id] = drone_completion_time
                    
                    # Track trip
                    drone_trips[earliest_drone_id].append({
                        'start': drone_start_time,
                        'end': drone_completion_time,
                        'customers': batch,
                        'from_truck_location': customer_location
                    })
                    
                    print(f"         Drone {earliest_drone_id}: Start T+{drone_start_time:.1f}, Duration {batch_time:.1f}min, Complete T+{drone_completion_time:.1f}")
            
            current_pos = customer_location
        
        # Return to depot
        distance = manhattan_distance(current_pos, depot)
        travel_time = calculate_travel_time(distance, truck_speed)
        current_time += travel_time
        truck_distance += distance
        
        print(f"T+{current_time:5.1f}: Về đến Depot")
        print(f"Tổng thời gian truck {truck_idx + 1}: {current_time:.1f} phút")
        print(f"Tổng khoảng cách truck {truck_idx + 1}: {truck_distance:.2f} km")
        
        total_time = max(total_time, current_time)
        total_distance += truck_distance
    
    # Print drone utilization summary
    print(f"\n--- THỐNG KÊ SỬ DỤNG DRONE ---")
    for drone_id in range(num_drones):
        print(f"\nDrone {drone_id}:")
        print(f"  Số chuyến bay: {len(drone_trips[drone_id])}")
        print(f"  Thời gian hoàn thành cuối: T+{drone_available_time[drone_id]:.1f}")
        
        for trip_idx, trip in enumerate(drone_trips[drone_id]):
            print(f"  Chuyến {trip_idx + 1}: T+{trip['start']:.1f} -> T+{trip['end']:.1f}")
            print(f"    Khách hàng: {trip['customers']}")
            print(f"    Xuất phát từ: {trip['from_truck_location']}")
    
    # Check final completion time including drones
    final_drone_time = max(drone_available_time.values()) if drone_available_time else 0
    total_time = max(total_time, final_drone_time)
    
    print(f"\n{'='*60}")
    print(f"TỔNG KẾT:")
    print(f"Tổng thời gian hoàn thành (bao gồm drone): {total_time:.1f} phút")
    print(f"Tổng khoảng cách tất cả trucks: {total_distance:.2f} km")
    print(f"Fitness value: {total_time:.2f}")
    print(f"{'='*60}")

# Test the visualization
if __name__ == "__main__":
    # Detailed structure analysis first
    print("PHÂN TÍCH CẤU TRÚC SOLUTION:")
    print("="*60)
    print(f"test_sol = {test_sol}")
    print(f"Độ dài solution: {len(test_sol)}")
    print(f"Phần tử 0: {test_sol[0]}")
    print(f"Phần tử 1: {test_sol[1] if len(test_sol) > 1 else 'Không có'}")
    
    print(f"\nPhần tử 0 có {len(test_sol[0])} truck routes:")
    for i, route in enumerate(test_sol[0]):
        print(f"  Truck {i+1}: {route}")
        print(f"    Số stops: {len(route)}")
        for j, stop in enumerate(route):
            print(f"      Stop {j+1}: Customer {stop[0]}, Drone deliveries: {stop[1] if len(stop) > 1 else []}")
    
    if len(test_sol) > 1:
        print(f"\nPhần tử 1 có {len(test_sol[1])} phần tử:")
        for i, item in enumerate(test_sol[1]):
            print(f"  Item {i+1}: {item}")
    
    # Print customer data for reference
    print(f"\nCustomer data (ID: (release_time, X, Y)):")
    for customer_id, customer_data in data.items():
        print(f"Customer {customer_id}: Release={customer_data[0]}, Location=({customer_data[1]}, {customer_data[2]})")
    print(f"Depot: {depot}")
    
    print("="*60)
    
    # Calculate fitness
    fitness_value = calculate_fitness(test_sol, data, depot)
    print(f"Fitness value for test solution: {fitness_value:.2f} minutes")
    
    # Detailed analysis
    analyze_solution_details(test_sol, data, depot)
    
    # Visualize the solution
    visualize_solution(test_sol, data, depot, "VRP with Drones - Test Solution")

#fitness description
'''To evaluate the performance of the MILP model and the matheuris-
tic, we developed instances from 10 to 100 customers based on Da-
yarian et al. (2020), Ulmer et al. (2019), and Archetti et al. (2018). We

consider a distribution area of 20 × 20 km2

, where customers are dis-
tributed uniformly at random. This area size is similar to Montgomery,

AL (413 km2
) and Valparaíso, Chile (402 km2

). Similar to Dayarian
et al. (2020), we locate the depot outside (−10, 10) the area, reflecting
the common situation of last-mile distribution facilities located on

European Journal of Operational Research 316 (2024) 168–182

178

J.C. Pina-Pardo et al.
the outskirts of cities. Nevertheless, to fully assess the matheuristic
compared to the MILP model on small instances, we also consider the
depot at the center (10, 10) and at the border (0, 10) of the area.
To generate the order release dates, we follow the procedure of
Archetti et al. (2018). These authors first compute the optimal TSP
value (zTSP) of visiting all customers in a single tour (without release
dates), and then generate uniformly random integer release dates in
the time interval [0, β ⋅ zTSP], where β is a factor that defines the width
of the interval. In our case, we obtain zTSP when the depot located at
the center of the area, with a constant truck travel speed of 30 km/h
and Manhattan distances. Similar to Archetti et al. (2020), we create
instances with β ∈ {0.5, 1.0, 1.5}.
Regarding the drone parameters, we consider the Avidrone 210TL,
manufactured by Avidrone Aerospace (Avidrone Aerospace, 2021), as
an example of the type of drone that could be used for resupply. This
drone has a payload capacity of 25 kilograms, a flight endurance of
90 min, and a maximum flight speed of 100 km/h. Considering that
most parcels weigh less than 2.3 kilograms (Poikonen & Golden, 2020),
this leads to a maximum drone load capacity (Q) of about 10 orders.
However, given that we evaluate the MILP model performance over
small instances of up to 20 customers, we experiment with Q = 2
orders for such instances. We then experiment with Q = 10 orders
when solving larger instances using the matheuristic. We assume that
all orders are interchangeable according to weight and physical size
(i.e., qi = 1, ∀i ∈ N). Furthermore, as commonly used in drone routing
research (Macrina et al., 2020), we employ a constant drone speed of
60 km/h, using the Euclidean metric to calculate the drone distances.
This should be an achievable average speed for the Avidrone 210TL.
The time needed to receive a drone en route or at the depot is fixed at
δm = δd = 5 min.
Based on Moshref-Javadi et al. (2020), we consider a fixed customer
service time of three minutes (i.e., si = 3, ∀i ∈ N). To enable a
fair comparison with the truck-only scenario, the time to receive a
truck at the depot is fixed at δt = 5 min, meaning that the time for
receiving a drone en route (δm) or at the depot (δd

) is equal to the time

for receiving a truck at the depot (δt

). Finally, we set a big-M value

as M = max
i∈N
{ri
} + zTSP in all MILP models. Here, M represents the
completion time if all orders to be released are waited for at the depot
and a single truck then conducts an optimal TSP tour.'''
