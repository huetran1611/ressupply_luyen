import copy
import Data
import Function
import random
import Neighborhood

epsilon = (-1)*0.00001
DIFFERENTIAL_RATE_RELEASE_TIME = Data.DIFFERENTIAL_RATE_RELEASE_TIME
B_ratio = Data.B_ratio
C_ratio = Data.C_ratio

def Neighborghood_change_drone_route(solution):
    neighborhood = []
    
    package = copy.deepcopy(solution[1])
    for i in range(Data.number_of_trucks):
        pack = []
        for j in range(len(solution[0][i][0][1])):
            pack.append(solution[0][i][0][1][j])
        package.insert(0,[[0,pack]])
            
    # Sắp xếp lại theo thứ tự drone
    for i in range(len(package)):
        for l in range(len(package[i])):
            for j in range(len(package[i][l][1])):
                for k in range(j+1,len(package[i][l][1])):
                    if(Data.release_date[package[i][l][1][j]] < Data.release_date[package[i][l][1][k]]):
                        temp = package[i][l][1][j]
                        package[i][l][1][j] = package[i][l][1][k]
                        package[i][l][1][k] = temp
    for i in range(len(package)):
        for j in range(len(package[i])):
            for k in range(1, len(package[i][j][1])+1):
                NewSolution = copy.deepcopy(solution)
                ChangePackages = []
                ChangeInTruck = Function.city_in_which_truck(solution, package[i][j][1][0])
                IndexOfReceiveCityInTruck = -1
                for l in range(k):
                    ChangePackage = package[i][j][1][l]
                    ChangePackages.append(ChangePackage)             # Các gói hàng sẽ chuyển
                    
                    # Xoá ở New Solution
                    
                    if(package[i][j][0] != 0):
                        NewSolution[1][i-Data.number_of_trucks][j][1].remove(ChangePackage)
                        for ii in range(len(NewSolution[0][ChangeInTruck])):
                            if(ChangePackage in NewSolution[0][ChangeInTruck][ii][1]):
                                IndexOfReceiveCityInTruck = ii
                                NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
                                break
                    else:
                        for ii in range(len(NewSolution[0][ChangeInTruck])):
                            if(ChangePackage in NewSolution[0][ChangeInTruck][ii][1]):
                                IndexOfReceiveCityInTruck = ii
                                NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
                                break
                if (Function.sum_weight(ChangePackages) > Data.drone_capacity):
                    continue
                if (NewSolution[0][ChangeInTruck][IndexOfReceiveCityInTruck][0] in ChangePackages):
                    continue
                if (package[i][j][0] != 0):
                    if (NewSolution[1][i-Data.number_of_trucks][j][1] == []):
                        NewSolution[1][i-Data.number_of_trucks].pop(j)
                        if (NewSolution[1][i-Data.number_of_trucks] == []):
                            NewSolution[1].pop(i-Data.number_of_trucks)
                stop = False
                for l in range(IndexOfReceiveCityInTruck + 1, len(NewSolution[0][ChangeInTruck])):
                    '''print("---------------------------------")
                    print(i,", ",j,", ",k,", ",l)'''
                    New_solution1 = copy.deepcopy(NewSolution)
                    '''for iii in range(Data.number_of_trucks):
                        print(New_solution1[0][iii])
                    print(New_solution1[1])
                    print(Function.Check_if_feasible(New_solution1))
                    print("-------------------------------")'''
                    ReceiveCity = New_solution1[0][ChangeInTruck][l][0]
                    if (ReceiveCity in ChangePackages): 
                        stop = True
                        
                    if Data.euclid_flight_matrix[0][ReceiveCity] * 2 + Data.unloading_time > Data.drone_limit_time:
                        if stop:
                            break
                        else:
                            continue
                    
                    # Trường hợp 1: Điểm giao đến không phải điểm nhận hàng
                    if (New_solution1[0][ChangeInTruck][l][1] == []):
                        # Add điểm giao hàng tại truck route
                        New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + ChangePackages
                        #Add điểm giao hàng tại drone package
                        if (Data.euclid_flight_matrix[0][ReceiveCity]*2 <= Data.drone_limit_time):
                            Neighborhood.addNewTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)
                        else:
                            continue
                    # Trường hợp 2: Điểm giao đến cũng là một điểm nhận hàng
                    else:
                        # Add điểm giao hàng tại truck route
                        New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + ChangePackages
                        #Add điểm giao hàng tại drone package
                        Neighborhood.groupTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)
                    '''for iii in range(Data.number_of_trucks):
                        print(New_solution1[0][iii])
                    print(New_solution1[1])
                    print(Function.Check_if_feasible(New_solution1))
                    print("-------------------------------")'''
                    temp = []
                    if (Function.has_duplicate_synchonize_point(New_solution1)):
                        print ("this solution has duplicate synchonixe point see drone que: \n")
                        print (New_solution1[1])
                    else:
                        temp.append(New_solution1)
                        fit, dt, tt = Function.fitness(New_solution1)
                        temp.append([fit, dt, tt])
                        temp.append(-1)
                        temp.append(-1)
                        neighborhood.append(temp)
                    if stop == True:
                        break      
    return neighborhood

def Neighborghood_change_drone_route_plus(solution):
    neighborhood = []
    
    package = copy.deepcopy(solution[1])
    for i in range(Data.number_of_trucks):
        pack = []
        for j in range(len(solution[0][i][0][1])):
            pack.append(solution[0][i][0][1][j])
        package.insert(0,[[0,pack]])
        
    for i in range(len(package)):
        for j in range(len(package[i])):
            index_truck = Function.index_truck_of_cities[package[i][j][0]]
            remained_pack = len(package[i][j][1])
            for k in range(len(solution[0][index_truck])):
                city = solution[0][index_truck][k][0]
                if city in package[i][j][1]:
                    remained_pack -= 1
                    package[i][j][1].remove(city)
                    if Data.release_date[city] > 0:
                        package[i][j][1].append(city)
                if remained_pack == 0:
                    break
        
    for i in range(len(package)):
        for j in range(len(package[i])):
            for k in range(1, len(package[i][j][1])+1):
                Total_case = takeAmountBeginAndEndPackage(package[i][j][1], k)
                for ii in range(len(Total_case)):
                    NewSolution = copy.deepcopy(solution)
                    ChangePackages = copy.deepcopy(Total_case[ii])
                    ChangeInTruck = Function.city_in_which_truck(solution, package[i][j][1][0])
                    IndexOfReceiveCityInTruck = -1
                    #print("Total: ", Total_case[ii])
                    for l in range(len(ChangePackages)):
                        #print("-----------------------------", ChangePackages)
                        ChangePackage = ChangePackages[l]

                        # Xoá ở New Solution
                        if(package[i][j][0] != 0):
                            NewSolution[1][i-Data.number_of_trucks][j][1].remove(ChangePackage)
                            for ii in range(len(NewSolution[0][ChangeInTruck])):
                                if(ChangePackage in NewSolution[0][ChangeInTruck][ii][1]):
                                    IndexOfReceiveCityInTruck = ii
                                    NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
                                    break
                        else:
                            for ii in range(len(NewSolution[0][ChangeInTruck])):
                                if(ChangePackage in NewSolution[0][ChangeInTruck][ii][1]):
                                    IndexOfReceiveCityInTruck = ii
                                    NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
                                    break
                        #print(ChangePackages)
                    #print("Change-1: ",ChangePackages)
                    if (Function.sum_weight(ChangePackages) > Data.drone_capacity):
                        continue
                    if (NewSolution[0][ChangeInTruck][IndexOfReceiveCityInTruck][0] in ChangePackages):
                        continue
                    if (package[i][j][0] != 0):
                        if (NewSolution[1][i-Data.number_of_trucks][j][1] == []):
                            NewSolution[1][i-Data.number_of_trucks].pop(j)
                            if (NewSolution[1][i-Data.number_of_trucks] == []):
                                NewSolution[1].pop(i-Data.number_of_trucks)
                    stop = False
                    for l in range(len(NewSolution[0][ChangeInTruck])):

                        if l == IndexOfReceiveCityInTruck:
                            continue
                        
                        New_solution1 = copy.deepcopy(NewSolution)

                        # for iii in range(Data.number_of_trucks):
                        #     print(New_solution1[0][iii])
                        # print(New_solution1[1])
                        # print(Function.Check_if_feasible(New_solution1))
                        # print("------")
                        
                        ReceiveCity = New_solution1[0][ChangeInTruck][l][0]
                        if ReceiveCity in ChangePackages: 
                            stop = True
                            
                        if Data.euclid_flight_matrix[0][ReceiveCity] * 2 + Data.unloading_time > Data.drone_limit_time:
                            if stop:
                                break
                            else:
                                continue
                        
                        # Trường hợp 1: Điểm giao đến không phải điểm nhận hàng
                        if New_solution1[0][ChangeInTruck][l][1] == []:
                            # Add điểm giao hàng tại truck route
                            for ll in range(len(ChangePackages)):
                                New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + [ChangePackages[ll]]
                            #Add điểm giao hàng tại drone package
                            if Data.euclid_flight_matrix[0][ReceiveCity]*2 + Data.unloading_time <= Data.drone_limit_time:
                                if l != 0:
                                    New_solution1, index_drone_trip, index_in_trip = Neighborhood.addNewTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)
                                '''if(i == 1 and j == 0 and k == 1 and l == 2):
                                    print("------------2-------------------")
                                    for iii in range(Data.number_of_trucks):
                                        print(New_solution1[0][iii])
                                    print(New_solution1[1])
                                    print(Function.Check_if_feasible(New_solution1))
                                    print("-------------------------------")'''
                            else:
                                continue
                        # Trường hợp 2: Điểm giao đến cũng là một điểm nhận hàng
                        else:
                            '''print("----3----")
                            for iii in range(Data.number_of_trucks):
                                print(New_solution1[0][iii])
                            print(New_solution1[1])
                            print(Function.Check_if_feasible(New_solution1))'''
                            # Add điểm giao hàng tại truck route
                            for ll in range(len(ChangePackages)):
                                New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + [ChangePackages[ll]]
                            #Add điểm giao hàng tại drone package
                            if l != 0:
                                New_solution1, index_drone_trip, index_in_trip, if_group = Neighborhood.groupTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)
                            '''print("----4----")
                            for iii in range(Data.number_of_trucks):
                                print(New_solution1[0][iii])
                            print(New_solution1[1])
                            print(Function.Check_if_feasible(New_solution1))'''
                        # for iii in range(Data.number_of_trucks):
                        #     print(New_solution1[0][iii])
                        # print(New_solution1[1])
                        # print(Function.Check_if_feasible(New_solution1))
                        # print("-------------------------------")
                        temp = []
                        if (Function.has_duplicate_synchonize_point(New_solution1)):
                            print ("this solution has duplicate synchonixe point see drone que: \n")
                            print (New_solution1[1])
                        else:
                            temp.append(New_solution1)
                            fit, dt, tt = Function.fitness(New_solution1)
                            temp.append([fit, dt, tt])
                            temp.append(-1)
                            temp.append(-1)
                            neighborhood.append(temp)
                        if stop == True:
                            break  
                
    return neighborhood

def group_two_trip(solution, index_drone_trip1, index_in_trip1, index_drone_trip2, index_in_trip2):
    package = copy.deepcopy(solution[1][index_drone_trip2][index_in_trip2][1])
    city_remove_package = solution[1][index_drone_trip2][index_in_trip2][0]
    
    for i in range(len(package)):
        solution[1][index_drone_trip1][index_in_trip1][1] += [package[i]]
    
    chosen_city = solution[1][index_drone_trip1][index_in_trip1][0]
    index_truck = Function.index_truck_of_cities[chosen_city]
    
    solution[1][index_drone_trip2].pop(index_in_trip2)
    
    delete_trip = False
    if solution[1][index_drone_trip2] == []:
        solution[1].pop(index_drone_trip2)
        delete_trip = True
    
    for i in range(1, len(solution[0][index_truck])):
        city = solution[0][index_truck][i][0]
        # Xóa trước
        if city == city_remove_package:
            for j in reversed(range(len(solution[0][index_truck][i][1]))):
                pack = solution[0][index_truck][i][1][j]
                if pack in package:
                    solution[0][index_truck][i][1].pop(j)
        # Add sau
        if city == chosen_city:
           for j in range(len(package)):
                solution[0][index_truck][i][1] += [package[j]]
    
    if delete_trip:
        if index_drone_trip1 > index_drone_trip2:
            solution = Rearrange_index_trip(solution, index_drone_trip1 - 1, True)
        elif index_drone_trip1 < index_drone_trip2:
            solution = Rearrange_index_trip(solution, index_drone_trip1, False)
    else:
        if index_drone_trip1 > index_drone_trip2:
            solution = Rearrange_index_trip(solution, index_drone_trip1, True)
        elif index_drone_trip1 < index_drone_trip2:
            solution = Rearrange_index_trip(solution, index_drone_trip1, False)
    
    return solution

# def Neighborhood_group_trip(solution):
#     neighborhood = []
#     temp = []
#     temp.append(solution)
#     fit, dt, tt = Function.fitness(solution)
#     temp.append([fit, dt, tt])
#     neighborhood.append(temp)
#     for i in range(len(solution[1])):
#         if Data.number_of_drones < 2:
#             return neighborhood
#         max_range = -1
#         min_range = -1
#         if i <= len(solution[1]) - 4:
#             max_range = i + 4
#         else:
#             max_range = len(solution[1])
#         if i - 3 >= 0:
#             min_range = i - 3
#         else:
#             min_range = 0
#         for j in range(min_range, max_range):
#             if i == j: continue
#             for k in range(len(solution[1][j])):
#                 new_solution = copy.deepcopy(solution)
#                 package_need_group = []
#                 package_need_group_to_city = solution[1][j][k][0]
#                 for l in range(len(solution[1][j][k][1])):
#                     package_need_group.append(solution[1][j][k][1][l])
#                 change_drone_flight_come_truck_number = Function.city_in_which_truck(solution, package_need_group_to_city)
                
#                 if Function.total_demand(solution[1][i]) + Function.sum_weight(package_need_group) <= Data.drone_capacity:
#                     if Function.max_release_date_update(solution[1][i]) * DIFFERENTIAL_RATE_RELEASE_TIME + Data.standard_deviation > Function.max_release_date(package_need_group) and Function.min_release_date_update(solution[1][i]) * DIFFERENTIAL_RATE_RELEASE_TIME + B_ratio * Data.standard_deviation > Function.max_release_date(package_need_group):
#                         check = False
#                         check_break = False
#                         for l in range(len(solution[1][i])):
#                             new_city_of_package_need_group = solution[1][i][l][0]
#                             come_to_truck = Function.city_in_which_truck(solution, new_city_of_package_need_group)
#                             if change_drone_flight_come_truck_number == come_to_truck:
#                                 if j < i: 
#                                     check_break = True
#                                     break
                                    
#                                 new_solution[1][i][l][1] += package_need_group
                                
#                                 # Cập nhật thông tin trên lộ trình xe tải
#                                 for m in range(len(new_solution[0][come_to_truck])):
#                                     city_evaluate = new_solution[0][come_to_truck][m][0]
                                    
#                                     # Xác định các vị trí của kho (0) trong lộ trình
#                                     depot_indices = [idx for idx, point in enumerate(new_solution[0][come_to_truck]) if point[0] == 0]
                                    
#                                     # Tìm vị trí của các thành phố
#                                     city_need_group_idx = -1
#                                     new_city_idx = -1
                                    
#                                     for idx, point in enumerate(new_solution[0][come_to_truck]):
#                                         if point[0] == package_need_group_to_city:
#                                             city_need_group_idx = idx
#                                         if point[0] == new_city_of_package_need_group:
#                                             new_city_idx = idx
                                    
#                                     # Kiểm tra xem có kho giữa hai thành phố không
#                                     has_depot_between = False
#                                     min_idx = city_need_group_idx if city_need_group_idx < new_city_idx else new_city_idx
#                                     max_idx = city_need_group_idx if city_need_group_idx > new_city_idx else new_city_idx
                                    
#                                     for depot_idx in depot_indices:
#                                         if depot_idx > min_idx and depot_idx < max_idx and depot_idx != 0:
#                                             has_depot_between = True
#                                             break
                                    
#                                     # Thêm gói hàng vào thành phố đích mới nếu không có kho ở giữa
#                                     if city_evaluate == new_city_of_package_need_group and not has_depot_between:
#                                         new_solution[0][come_to_truck][m][1] += package_need_group
                                    
#                                     # Xóa gói hàng khỏi thành phố nguồn cũ
#                                     if city_evaluate == package_need_group_to_city:
#                                         for n in range(len(package_need_group)):
#                                             if package_need_group[n] in new_solution[0][come_to_truck][m][1]:
#                                                 new_solution[0][come_to_truck][m][1].remove(package_need_group[n])
                                
#                                 check = True
                                
#                         if check_break: continue
                        
#                         if not check:
#                             stop = False
#                             if i < j:
#                                 for m in range(i+1, j):
#                                     for n in range(len(new_solution[1][m])):
#                                         checkCoincideTruck = Function.city_in_which_truck(new_solution, new_solution[1][m][n][0])
#                                         if checkCoincideTruck == change_drone_flight_come_truck_number:
#                                             stop = True
#                                             break
#                                     if stop: break
#                             else:
#                                 for m in range(j+1, i):
#                                     for n in range(len(new_solution[1][m])):
#                                         checkCoincideTruck = Function.city_in_which_truck(new_solution, new_solution[1][m][n][0])
#                                         if checkCoincideTruck == change_drone_flight_come_truck_number:
#                                             stop = True
#                                             break
#                                     if stop: break
#                             if stop: continue
                            
#                             # Kiểm tra thêm cho xe tải đa chuyến
#                             # Tìm "phân đoạn" (segment) của xe tải mà thành phố đích thuộc về
#                             truck_route = new_solution[0][change_drone_flight_come_truck_number]
#                             depot_indices = [idx for idx, point in enumerate(truck_route) if point[0] == 0]
                            
#                             # Tìm vị trí của thành phố cần gộp
#                             for idx, point in enumerate(truck_route):
#                                 if point[0] == package_need_group_to_city:
#                                     city_idx = idx
#                                     break
                            
#                             # Xác định phân đoạn hiện tại
#                             current_segment = -1
#                             for seg_idx, depot_idx in enumerate(depot_indices):
#                                 if city_idx > depot_idx:
#                                     current_segment = seg_idx
                            
#                             # Kiểm tra xem các thành phố trong chuyến bay hiện tại có cùng phân đoạn không
#                             same_segment = True
#                             for trip_point in new_solution[1][i]:
#                                 city = trip_point[0]
#                                 if city == 0:
#                                     continue
                                
#                                 # Tìm vị trí của thành phố trong lộ trình xe tải
#                                 city_truck = Function.city_in_which_truck(new_solution, city)
#                                 if city_truck != change_drone_flight_come_truck_number:
#                                     continue
                                
#                                 # Tìm vị trí của thành phố trong lộ trình
#                                 for idx, point in enumerate(truck_route):
#                                     if point[0] == city:
#                                         point_idx = idx
#                                         break
                                
#                                 # Xác định phân đoạn của thành phố
#                                 point_segment = -1
#                                 for seg_idx, depot_idx in enumerate(depot_indices):
#                                     if point_idx > depot_idx:
#                                         point_segment = seg_idx
                                
#                                 # Nếu không cùng phân đoạn, không thể gộp
#                                 if point_segment != current_segment:
#                                     same_segment = False
#                                     break
                            
#                             if not same_segment:
#                                 continue
                                
#                             new_solution[1][i].append([package_need_group_to_city, package_need_group])
#                             shortest_route_by_point, shortest_route_by_truck = Function.find_drone_flight_shortest(solution, new_solution[1][i])
#                             drone_fly_time = Data.euclid_flight_matrix[0][shortest_route_by_point[0]] + Data.euclid_flight_matrix[shortest_route_by_point[len(shortest_route_by_point)-1]][0]
#                             for m in range(len(shortest_route_by_point)-1):
#                                 drone_fly_time += Data.euclid_flight_matrix[shortest_route_by_point[m]][shortest_route_by_point[m+1]]
#                             if drone_fly_time + len(shortest_route_by_point) * Data.unloading_time > Data.drone_limit_time:
#                                 continue
                                
#                         # Xóa chuyến giao hàng đã được gộp từ chuyến bay drone cũ
#                         new_solution[1][j].pop(k)
#                         if new_solution[1][j] == []:
#                             new_solution[1].pop(j)
                            
#                         # Kiểm tra tính khả thi của lời giải mới
#                         if Function.check_if_drone_time_out_of_limit(new_solution):
#                             temp = []
#                             temp.append(new_solution)
#                             print(new_solution)
#                             fit, dt, tt = Function.fitness(new_solution)
#                             temp.append([fit, dt, tt])
#                             temp.append([i,j,k])
#                             neighborhood.append(temp)
#     return neighborhood
# Neighborhood_group_trip gộp 1 lần giao hàng tới 1 thành phố cảu drone vào một trip khác
def Neighborhood_group_trip(solution):
    neighborhood = []
    temp = []
    temp.append(solution)
    fit, dt, tt = Function.fitness(solution)
    temp.append([fit, dt, tt])
    neighborhood.append(temp)
    
    for i in range(len(solution[1])):
        if Data.number_of_drones < 2:
            return neighborhood
        max_range = -1
        min_range = -1
        if i <= len(solution[1]) - 4:
            max_range = i + 4
        else:
            max_range = len(solution[1])
        if i - 3 >= 0:
            min_range = i - 3
        else:
            min_range = 0
            
        for j in range(min_range, max_range):
            if i == j: 
                continue
                
            for k in range(len(solution[1][j])):
                try:
                    new_solution = copy.deepcopy(solution)
                    package_need_group = []
                    package_need_group_to_city = solution[1][j][k][0]
                    
                    # Collect packages to be grouped
                    for l in range(len(solution[1][j][k][1])):
                        package_need_group.append(solution[1][j][k][1][l])
                    
                    change_drone_flight_come_truck_number = Function.city_in_which_truck(solution, package_need_group_to_city)
                    
                    # Capacity check
                    if Function.total_demand(solution[1][i]) + Function.sum_weight(package_need_group) <= Data.drone_capacity:
                        # Release date constraints
                        if (Function.max_release_date_update(solution[1][i]) * DIFFERENTIAL_RATE_RELEASE_TIME + Data.standard_deviation > Function.max_release_date(package_need_group) and 
                            Function.min_release_date_update(solution[1][i]) * DIFFERENTIAL_RATE_RELEASE_TIME + B_ratio * Data.standard_deviation > Function.max_release_date(package_need_group)):
                            
                            check = False
                            check_break = False
                            
                            # Try to group with existing pickup points in trip i
                            for l in range(len(solution[1][i])):
                                new_city_of_package_need_group = solution[1][i][l][0]
                                come_to_truck = Function.city_in_which_truck(solution, new_city_of_package_need_group)
                                
                                if change_drone_flight_come_truck_number == come_to_truck:
                                    if j < i: 
                                        check_break = True
                                        break
                                    
                                    # Add packages to existing pickup point
                                    new_solution[1][i][l][1] += package_need_group
                                    
                                    # Update truck route - add packages to destination city
                                    for m in range(len(new_solution[0][come_to_truck])):
                                        city_evaluate = new_solution[0][come_to_truck][m][0]
                                        
                                        if city_evaluate == new_city_of_package_need_group:
                                            new_solution[0][come_to_truck][m][1] += package_need_group
                                        
                                        # Remove packages from source city with validation
                                        if city_evaluate == package_need_group_to_city:
                                            packages_to_remove = []
                                            
                                            for n in range(len(package_need_group)):
                                                pkg = package_need_group[n]
                                                if pkg in new_solution[0][come_to_truck][m][1]:
                                                    packages_to_remove.append(pkg)
                                            
                                            # Remove only packages that exist
                                            for pkg in packages_to_remove:
                                                new_solution[0][come_to_truck][m][1].remove(pkg)
                                    
                                    check = True
                                    break
                            
                            if check_break: 
                                continue
                            
                            # If no existing pickup point can be used, create new one
                            if not check:
                                stop = False
                                
                                # Check for truck conflicts between trips
                                if i < j:
                                    for m in range(i+1, j):
                                        for n in range(len(new_solution[1][m])):
                                            checkCoincideTruck = Function.city_in_which_truck(new_solution, new_solution[1][m][n][0])
                                            if checkCoincideTruck == change_drone_flight_come_truck_number:
                                                stop = True
                                                break
                                        if stop: 
                                            break
                                else:
                                    for m in range(j+1, i):
                                        for n in range(len(new_solution[1][m])):
                                            checkCoincideTruck = Function.city_in_which_truck(new_solution, new_solution[1][m][n][0])
                                            if checkCoincideTruck == change_drone_flight_come_truck_number:
                                                stop = True
                                                break
                                        if stop: 
                                            break
                                
                                if stop: 
                                    continue
                                
                                # Add new pickup point to trip i
                                new_solution[1][i].append([package_need_group_to_city, package_need_group])
                                
                                # Check drone time constraints
                                shortest_route_by_point, shortest_route_by_truck = Function.find_drone_flight_shortest(solution, new_solution[1][i])
                                drone_fly_time = Data.euclid_flight_matrix[0][shortest_route_by_point[0]] + Data.euclid_flight_matrix[shortest_route_by_point[len(shortest_route_by_point)-1]][0]
                                for m in range(len(shortest_route_by_point)-1):
                                    drone_fly_time += Data.euclid_flight_matrix[shortest_route_by_point[m]][shortest_route_by_point[m+1]]
                                
                                if drone_fly_time + len(shortest_route_by_point) * Data.unloading_time > Data.drone_limit_time:
                                    continue
                            
                            # Remove the original pickup point from trip j
                            if k < len(new_solution[1][j]):
                                new_solution[1][j].pop(k)
                            else:
                                continue
                            
                            # Remove empty trip if necessary
                            if new_solution[1][j] == []:
                                new_solution[1].pop(j)
                            
                            # Validate and add to neighborhood
                            if Function.check_if_drone_time_out_of_limit(new_solution):
                                temp = []
                                temp.append(new_solution)
                                fit, dt, tt = Function.fitness(new_solution)
                                temp.append([fit, dt, tt])
                                temp.append([i, j, k])
                                neighborhood.append(temp)
                
                except Exception as e:
                    continue
    
    return neighborhood

def choose_what_to_group(solution, index_drone_trip, index_in_trip, find_in_forward):
    # #Debug
    # print("solution: ", solution)
    # print("index_drone_trip: ", index_drone_trip)
    # print("index_in_trip: ", index_in_trip)
    # print("find_in_forward: ", find_in_forward)
    chosen_city = solution[1][index_drone_trip][index_in_trip][0]
    index_truck = Function.index_truck_of_cities[chosen_city] 
    start1, end1 = Function.determine_start_end(solution, index_truck, chosen_city)
    index_chosen_city_in_truck = -1
    for i in range(len(solution[0][index_truck])):
        city = solution[0][index_truck][i][0]
        if city == chosen_city:
            index_chosen_city_in_truck = i
    demand_package = 0
    stone_package = solution[1][index_drone_trip][index_in_trip][1]
    for i in range(len(stone_package)):
        demand_package += Data.city_demand[stone_package[i]]
    
    if find_in_forward == False:
        index_drone_trip_choose_to_group = -1
        index_in_trip_choose_to_group = -1
        stop1368 = False
        for i in reversed(range(index_drone_trip)):
            for j in range(len(solution[1][i])):
                city1 = solution[1][i][j][0]
                index_truck1 = Function.index_truck_of_cities[city1]
                if Function.index_truck_of_cities[solution[1][i][j][0]] == index_truck:
                    start2, end2 = Function.determine_start_end(solution, index_truck1, city1)
                    if start2 == start1:
                        index_drone_trip_choose_to_group = i
                        index_in_trip_choose_to_group = j
                        stop1368 = True
                        break
            if stop1368:
                break
            
        if not stop1368:
            pre_potential_package = copy.deepcopy(solution[0][index_truck][start1][1])
            potential_package = []
            # for i in range(len(solution[0][index_truck])):
            for i in range(start1+1, end1):
                city = solution[0][index_truck][i][0]
                if city in pre_potential_package:
                    potential_package.append(city)
            
            for i in range(len(potential_package)):
                if Data.release_date[potential_package[i]] == 0:
                    continue
                
                continue744 = False
                
                # Kiểm tra xem gói hàng muốn gộp có hợp lệ vị trí giao hàng tại điểm gộp mới không
                for ii in range(start1+1, index_chosen_city_in_truck):
                    if solution[0][index_truck][ii][0] in potential_package:
                        continue744 = True
                        break
                    
                if continue744:
                    continue
                
                if demand_package + Data.city_demand[potential_package[i]] <= Data.drone_capacity:
                    demand_package += Data.city_demand[potential_package[i]]
                    solution[0][index_truck][start1][1].remove(potential_package[i])
                    solution[0][index_truck][index_chosen_city_in_truck][1] += [potential_package[i]]
                    solution[1][index_drone_trip][index_in_trip][1] += [potential_package[i]]
        
        else:           
            move_package = solution[1][index_drone_trip_choose_to_group][index_in_trip_choose_to_group][1]
            
            continue771 = False
            
            for i in range(index_chosen_city_in_truck):
                if solution[0][index_truck][i][0] in move_package:
                    continue771 = True
                    break
            
            if not continue771:
                if demand_package + Function.sum_weight(solution[1][index_drone_trip_choose_to_group][index_in_trip_choose_to_group][1]) <= Data.drone_capacity:
                    if Function.max_release_date(stone_package) + Data.standard_deviation > Function.max_release_date(solution[1][index_drone_trip_choose_to_group][index_in_trip_choose_to_group][1]):
                        solution = group_two_trip(solution, index_drone_trip, index_in_trip, index_drone_trip_choose_to_group, index_in_trip_choose_to_group)
    else:
        
        index_drone_trip_choose_to_group = -1
        index_in_trip_choose_to_group = -1
        stop761 = False
        for i in range(index_drone_trip + 1, len(solution[1])):
            for j in range(len(solution[1][i])):
                city1 = solution[1][i][j][0]
                index_truck1 = Function.index_truck_of_cities[city1]
                if Function.index_truck_of_cities[solution[1][i][j][0]] == index_truck:
                    start2, end2 = Function.determine_start_end(solution, index_truck1, city1)
                    if start2 == start1:
                        index_drone_trip_choose_to_group = i
                        index_in_trip_choose_to_group = j
                        stop761 = True
                        break
            if stop761:
                break
        if index_drone_trip_choose_to_group != -1:
            if demand_package + Function.sum_weight(solution[1][index_drone_trip_choose_to_group][index_in_trip_choose_to_group][1]) <= Data.drone_capacity:
                if Function.max_release_date(stone_package) + Data.standard_deviation > Function.max_release_date(solution[1][index_drone_trip_choose_to_group][index_in_trip_choose_to_group][1]):
                    solution = group_two_trip(solution, index_drone_trip, index_in_trip, index_drone_trip_choose_to_group, index_in_trip_choose_to_group)

    return solution

# def Neighborghood_change_drone_route_max_pro_plus(solution):
#     neighborhood = []
#     Function.update_per_loop(solution)
#     package = copy.deepcopy(solution[1])
    
#     for i in range(Data.number_of_trucks):
#         pack = []
#         for j in range(len(solution[0][i][0][1])):
#             pack.append(solution[0][i][0][1][j])
#         package.insert(0,[[0,pack]])
        
#     for i in range(len(package)):
#         for j in range(len(package[i])):
#             index_truck = Function.index_truck_of_cities[package[i][j][0]]
#             remained_pack = len(package[i][j][1])
#             for k in range(len(solution[0][index_truck])):
#                 city = solution[0][index_truck][k][0]
#                 if city in package[i][j][1]:
#                     remained_pack -= 1
#                     package[i][j][1].remove(city)
#                     if Data.release_date[city] > 0:
#                         package[i][j][1].append(city)
#                 if remained_pack == 0:
#                     break
#     coutt = 0
#     for i in range(len(package)):
#         for j in range(len(package[i])):
#             initial_demand_package = Function.sum_weight(package[i][j][1])
#             for k in range(1, len(package[i][j][1])+1):
#                 Total_case = takeAmountBeginAndEndPackage(package[i][j][1])
#                 for ii in range(len(Total_case)):
#                     NewSolution = copy.deepcopy(solution)
#                     ChangePackages = copy.deepcopy(Total_case[ii])
#                     ChangeInTruck = Function.city_in_which_truck(solution, package[i][j][1][0])
#                     IndexOfReceiveCityInTruck = -1
#                     #print("Total: ", Total_case[ii])
#                     for l in range(len(ChangePackages)):
#                         # print("hehe: ", ChangePackages)
#                         # print("-----------------------------", ChangePackages)
#                         ChangePackage = ChangePackages[l]
#                         #ChangePackages.append(ChangePackage)
#                         #print(ChangePackage)
#                         #print(ChangePackages)
#                         # Xoá ở New Solution
#                         if package[i][j][0] != 0:
#                             NewSolution[1][i-Data.number_of_trucks][j][1].remove(ChangePackage)
#                             for ii in range(len(NewSolution[0][ChangeInTruck])):
#                                 if ChangePackage in NewSolution[0][ChangeInTruck][ii][1]:
#                                     IndexOfReceiveCityInTruck = ii
#                                     NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
#                                     break
#                         else:
#                             for ii in range(len(NewSolution[0][ChangeInTruck])):
#                                 if ChangePackage in NewSolution[0][ChangeInTruck][ii][1]:
#                                     IndexOfReceiveCityInTruck = ii
#                                     NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
#                                     break
#                         #print(ChangePackages)
#                     #print("Change-1: ",ChangePackages)
#                     if Function.sum_weight(ChangePackages) > Data.drone_capacity:
#                         continue
#                     if NewSolution[0][ChangeInTruck][IndexOfReceiveCityInTruck][0] in ChangePackages:
#                         continue
                    
#                     if package[i][j][0] != 0:
#                         if NewSolution[1][i-Data.number_of_trucks][j][1] == []:
#                             NewSolution[1][i-Data.number_of_trucks].pop(j)
#                             if NewSolution[1][i-Data.number_of_trucks] == []:
#                                 NewSolution[1].pop(i-Data.number_of_trucks)
#                         else:
#                             NewSolution = Rearrange_index_trip(NewSolution, i-Data.number_of_trucks, False)
#                     stop = False
#                     start_, end_ = Function.determine_start_end(NewSolution, ChangeInTruck, ChangePackages[0])
#                     # for l in range(len(NewSolution[0][ChangeInTruck])):
#                     for l in range(start_, end_):
                    
#                         if l == IndexOfReceiveCityInTruck:
#                             continue

#                         New_solution1 = copy.deepcopy(NewSolution)
                        
#                         ReceiveCity = New_solution1[0][ChangeInTruck][l][0]
#                         if ReceiveCity in ChangePackages: 
#                             stop = True
                        
#                         if Data.euclid_flight_matrix[0][ReceiveCity] * 2 + Data.unloading_time > Data.drone_limit_time:
#                             if stop:
#                                 break
#                             else:
#                                 continue
                        
#                         demand_change_package = Function.sum_weight(ChangePackages)
                        
#                         # Trường hợp 1: Điểm giao đến không phải điểm nhận hàng
#                         if New_solution1[0][ChangeInTruck][l][1] == []:
#                             # Add điểm giao hàng tại truck route
#                             for ll in range(len(ChangePackages)):
#                                 New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + [ChangePackages[ll]]
#                             #Add điểm giao hàng tại drone package
#                             if Data.euclid_flight_matrix[0][ReceiveCity] * 2 + Data.unloading_time <= Data.drone_limit_time:
#                                 if ReceiveCity != 0:
#                                     index_drone_trip = -1
#                                     index_in_trip = -1
#                                     New_solution1, index_drone_trip, index_in_trip = Neighborhood.addNewTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)
                                
                                
#                                 # if len(neighborhood) == 72:
#                                 #     print("heheh")
#                                 #     print(New_solution1[0][0])
#                                 #     print(New_solution1[1])
#                                 #     print("--next--")
                                
#                                     if l > IndexOfReceiveCityInTruck: 
#                                         if demand_change_package <= 0.5 * Data.drone_capacity:
#                                             New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, True)
#                                         if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
#                                             if initial_demand_package != demand_change_package:
#                                                 if i - Data.number_of_trucks >= 0:
#                                                     New_solution1 = choose_what_to_group(New_solution1, i - Data.number_of_trucks, j, False)
#                                     else:
#                                         if initial_demand_package != demand_change_package:
#                                             if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
#                                                 if ReceiveCity != 0:
#                                                     New_solution1 = choose_what_to_group(New_solution1, i - Data.number_of_trucks + 1, j, True)
#                                                 else:
#                                                     New_solution1 = choose_what_to_group(New_solution1, i - Data.number_of_trucks, j, True)
#                                         if demand_change_package <= 0.5 * Data.drone_capacity:
#                                             if  ReceiveCity != 0:
#                                                 New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, False)
                                    
#                             else:
#                                 continue
#                         # Trường hợp 2: Điểm giao đến cũng là một điểm nhận hàng
#                         else:
                            
#                             # Add điểm giao hàng tại truck route
#                             for ll in range(len(ChangePackages)):
#                                 New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + [ChangePackages[ll]]
#                             #Add điểm giao hàng tại drone package
#                             if_group = True
#                             # print(New_solution1[0][0])
#                             # print(New_solution1[1])
#                             # print("l: ",l)
#                             # print("Change: ", ChangePackages)
#                             # print("--firstt--")
#                             # if len(neighborhood) == 72:
#                             #     print("uhuh")
#                             #     print(New_solution1[0][0])
#                             #     print(New_solution1[1])
#                             #     print("--next--")
                            
#                             if  ReceiveCity != 0: 
#                                 index_drone_trip = -1
#                                 index_in_trip = -1
#                                 # if len(neighborhood) == 72:
#                                 #     print(New_solution1)
#                                 #     print(ChangePackages)
#                                 #     print(ChangeInTruck)
#                                 #     print(l)
#                                 #     print("kkakak")
#                                 New_solution1, index_drone_trip, index_in_trip, if_group = Neighborhood.groupTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)

#                                 if if_group:
#                                     NewSolution = Rearrange_index_trip(NewSolution, index_drone_trip, True)
                            
                            
#                             # if len(neighborhood) == 221:
#                             #     print("ehehe")
#                             #     print(New_solution1[0][0])
#                             #     print(New_solution1[1])
#                             #     print("--next--")
                                 
#                                 if if_group:    # Gộp thành công
                                    
#                                     if l > IndexOfReceiveCityInTruck:
#                                         if Function.sum_weight(New_solution1[1][index_drone_trip][index_in_trip][1]) <= 0.5 * Data.drone_capacity:
#                                             New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, True)
#                                         if initial_demand_package != demand_change_package:
#                                             if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
#                                                 if i - Data.number_of_trucks >= 0:
#                                                     New_solution1 = choose_what_to_group(New_solution1, i - Data.number_of_trucks, j, False)
#                                     else:
#                                         if initial_demand_package != demand_change_package:
#                                             if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
#                                                 New_solution1 = choose_what_to_group(New_solution1, i - Data.number_of_trucks, j, True)
                                            
#                                         if ReceiveCity != 0:
#                                             if Function.sum_weight(New_solution1[1][index_drone_trip][index_in_trip][1]) <= 0.5 * Data.drone_capacity:
#                                                 New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, False)
                            
#                                 else:           # Gộp thất bại, tạo trip mới riêng
#                                     if l > IndexOfReceiveCityInTruck:
#                                         if demand_change_package <= 0.5 * Data.drone_capacity:
#                                             New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, True)
#                                         if i - Data.number_of_trucks >= 0:
#                                             if initial_demand_package != demand_change_package:
#                                                 if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
#                                                     New_solution1 = choose_what_to_group(New_solution1, i - Data.number_of_trucks, j, False)
#                                     else:
#                                         if initial_demand_package != demand_change_package:
#                                             if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
#                                                 New_solution1 = choose_what_to_group(New_solution1, i - Data.number_of_trucks + 1, j, True)
#                                         if demand_change_package <= 0.5 * Data.drone_capacity:
#                                             if ReceiveCity != 0:
#                                                 New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, False)
                                        

#                         # if len(neighborhood) == 221:
#                         #     print(New_solution1[0][0])
#                         #     print(New_solution1[1])
#                         # print(New_solution1[0][0])
#                         # print(New_solution1[1])
#                         # print("-------------------------------")
#                         temp = []
#                         temp.append(New_solution1)
#                         fit, dt, tt = Function.fitness(New_solution1)
#                         temp.append([fit, dt, tt])
#                         temp.append(-1)
#                         temp.append(-1)
#                         neighborhood.append(temp)
#                         if stop == True:
#                             break              
#     return neighborhood

def Neighborghood_change_drone_route_max_pro_plus(solution):
    """
    Rewritten function to properly handle multiple pickup points and fix indexing issues
    """
    neighborhood = []
    Function.update_per_loop(solution)
    
    # Helper function for safe bounds checking
    def safe_choose_what_to_group(sol, trip_idx, pickup_idx, find_forward):
        # Check bounds before calling
        if (trip_idx >= 0 and trip_idx < len(sol[1]) and 
            pickup_idx >= 0 and pickup_idx < len(sol[1][trip_idx])):
            return choose_what_to_group(sol, trip_idx, pickup_idx, find_forward)
        return sol
    
    # Collect all pickup points with proper tracking
    all_pickup_points = []
    
    # 1. Process depot packages (packages loaded at depot)
    for truck_idx in range(Data.number_of_trucks):
        depot_packages = []
        if len(solution[0][truck_idx]) > 0:
            for pkg in solution[0][truck_idx][0][1]:
                depot_packages.append(pkg)
        
        if depot_packages:
            all_pickup_points.append({
                'source': 'depot',
                'truck_idx': truck_idx,
                'pickup_city': 0,
                'packages': depot_packages,
                'original_trip_idx': -1,
                'original_pickup_idx': -1
            })
    
    # 2. Process drone packages
    for trip_idx in range(len(solution[1])):
        for pickup_idx in range(len(solution[1][trip_idx])):
            pickup_city = solution[1][trip_idx][pickup_idx][0]
            packages = solution[1][trip_idx][pickup_idx][1].copy()
            
            if packages:
                all_pickup_points.append({
                    'source': 'drone',
                    'truck_idx': Function.city_in_which_truck(solution, pickup_city),
                    'pickup_city': pickup_city,
                    'packages': packages,
                    'original_trip_idx': trip_idx,
                    'original_pickup_idx': pickup_idx
                })
    
    # 3. Clean up packages based on truck route order
    for pickup_point in all_pickup_points:
        if pickup_point['pickup_city'] == 0:
            continue
            
        truck_idx = pickup_point['truck_idx']
        packages = pickup_point['packages']
        remained_pack = len(packages)
        
        for k in range(len(solution[0][truck_idx])):
            city = solution[0][truck_idx][k][0]
            if city in packages:
                remained_pack -= 1
                packages.remove(city)
                if Data.release_date[city] > 0:
                    packages.append(city)
            if remained_pack == 0:
                break
        
        pickup_point['packages'] = packages
    
    # 4. Generate neighborhoods for each pickup point
    for point_idx, pickup_point in enumerate(all_pickup_points):
        if not pickup_point['packages']:
            continue
            
        source = pickup_point['source']
        truck_idx = pickup_point['truck_idx']
        pickup_city = pickup_point['pickup_city']
        packages = pickup_point['packages']
        original_trip_idx = pickup_point['original_trip_idx']
        original_pickup_idx = pickup_point['original_pickup_idx']
        
        initial_demand_package = Function.sum_weight(packages)
        
        # Generate package combinations
        Total_cases = takeAmountBeginAndEndPackage(packages)
        
        for case in Total_cases:
            if not case:
                continue
                
            NewSolution = copy.deepcopy(solution)
            ChangePackages = copy.deepcopy(case)
            ChangeInTruck = truck_idx
            IndexOfReceiveCityInTruck = -1
            
            # Validate capacity constraint
            if Function.sum_weight(ChangePackages) > Data.drone_capacity:
                continue
            
            # Remove packages from original locations
            for pkg in ChangePackages:
                # Remove from drone trips if source is drone
                if source == 'drone':
                    if (original_trip_idx >= 0 and original_trip_idx < len(NewSolution[1]) and
                        original_pickup_idx >= 0 and original_pickup_idx < len(NewSolution[1][original_trip_idx])):
                        if pkg in NewSolution[1][original_trip_idx][original_pickup_idx][1]:
                            NewSolution[1][original_trip_idx][original_pickup_idx][1].remove(pkg)
                
                # Remove from truck routes
                for pos in range(len(NewSolution[0][ChangeInTruck])):
                    if pkg in NewSolution[0][ChangeInTruck][pos][1]:
                        IndexOfReceiveCityInTruck = pos
                        NewSolution[0][ChangeInTruck][pos][1].remove(pkg)
                        break
            
            # Clean up empty drone pickup points
            if source == 'drone':
                if (original_trip_idx >= 0 and original_trip_idx < len(NewSolution[1]) and
                    original_pickup_idx >= 0 and original_pickup_idx < len(NewSolution[1][original_trip_idx])):
                    if not NewSolution[1][original_trip_idx][original_pickup_idx][1]:
                        # Remove empty pickup point
                        NewSolution[1][original_trip_idx].pop(original_pickup_idx)
                        if not NewSolution[1][original_trip_idx]:
                            # Remove empty trip
                            NewSolution[1].pop(original_trip_idx)
                    else:
                        # Rearrange trip if needed
                        NewSolution = Rearrange_index_trip(NewSolution, original_trip_idx, False)
            
            # Validate constraints
            if (IndexOfReceiveCityInTruck >= 0 and IndexOfReceiveCityInTruck < len(NewSolution[0][ChangeInTruck]) and
                NewSolution[0][ChangeInTruck][IndexOfReceiveCityInTruck][0] in ChangePackages):
                continue
            
            # Find valid delivery positions
            if ChangePackages:
                start_pos, end_pos = Function.determine_start_end(NewSolution, ChangeInTruck, ChangePackages[0])
            else:
                continue
                
            stop = False
            
            for delivery_pos in range(start_pos, end_pos):
                if delivery_pos == IndexOfReceiveCityInTruck:
                    continue
                
                if delivery_pos >= len(NewSolution[0][ChangeInTruck]):
                    continue
                
                New_solution1 = copy.deepcopy(NewSolution)
                ReceiveCity = New_solution1[0][ChangeInTruck][delivery_pos][0]
                
                # Check stop condition
                if ReceiveCity in ChangePackages:
                    stop = True
                
                # Check drone time limit
                if Data.euclid_flight_matrix[0][ReceiveCity] * 2 + Data.unloading_time > Data.drone_limit_time:
                    if stop:
                        break
                    else:
                        continue
                
                demand_change_package = Function.sum_weight(ChangePackages)
                
                # Add packages to delivery position
                for pkg in ChangePackages:
                    New_solution1[0][ChangeInTruck][delivery_pos][1].append(pkg)
                
                # Handle drone route creation/grouping
                if ReceiveCity == 0:
                    # Don't create drone trips for depot delivery
                    pass
                elif not New_solution1[0][ChangeInTruck][delivery_pos][1] or \
                     len(New_solution1[0][ChangeInTruck][delivery_pos][1]) == len(ChangePackages):
                    # Case 1: Empty position or only our packages - create new trip
                    if (Data.euclid_flight_matrix[0][ReceiveCity] * 2 + Data.unloading_time <= 
                        Data.drone_limit_time):
                        
                        index_drone_trip = -1
                        index_in_trip = -1
                        New_solution1, index_drone_trip, index_in_trip = Neighborhood.addNewTripInDroneRoute(
                            New_solution1, ChangePackages, ChangeInTruck, delivery_pos)
                        
                        # Apply grouping optimization with proper bounds checking
                        if index_drone_trip >= 0 and index_in_trip >= 0:
                            if delivery_pos > IndexOfReceiveCityInTruck:
                                # Forward direction
                                if demand_change_package <= 0.5 * Data.drone_capacity:
                                    New_solution1 = safe_choose_what_to_group(
                                        New_solution1, index_drone_trip, index_in_trip, True)
                                
                                if (source == 'drone' and 
                                    initial_demand_package != demand_change_package and
                                    initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity):
                                    # Find current position of original pickup point
                                    current_trip_idx = -1
                                    current_pickup_idx = -1
                                    
                                    for t_idx in range(len(New_solution1[1])):
                                        for p_idx in range(len(New_solution1[1][t_idx])):
                                            if New_solution1[1][t_idx][p_idx][0] == pickup_city:
                                                current_trip_idx = t_idx
                                                current_pickup_idx = p_idx
                                                break
                                        if current_trip_idx >= 0:
                                            break
                                    
                                    if current_trip_idx >= 0 and current_pickup_idx >= 0:
                                        New_solution1 = safe_choose_what_to_group(
                                            New_solution1, current_trip_idx, current_pickup_idx, False)
                            else:
                                # Backward direction
                                if (source == 'drone' and 
                                    initial_demand_package != demand_change_package and
                                    initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity):
                                    # Find current position of original pickup point
                                    current_trip_idx = -1
                                    current_pickup_idx = -1
                                    
                                    for t_idx in range(len(New_solution1[1])):
                                        for p_idx in range(len(New_solution1[1][t_idx])):
                                            if New_solution1[1][t_idx][p_idx][0] == pickup_city:
                                                current_trip_idx = t_idx
                                                current_pickup_idx = p_idx
                                                break
                                        if current_trip_idx >= 0:
                                            break
                                    
                                    if current_trip_idx >= 0 and current_pickup_idx >= 0:
                                        New_solution1 = safe_choose_what_to_group(
                                            New_solution1, current_trip_idx, current_pickup_idx, True)
                                
                                if demand_change_package <= 0.5 * Data.drone_capacity:
                                    New_solution1 = safe_choose_what_to_group(
                                        New_solution1, index_drone_trip, index_in_trip, False)
                    else:
                        continue
                
                else:
                    # Case 2: Group with existing pickup point
                    if_group = True
                    index_drone_trip = -1
                    index_in_trip = -1
                    
                    New_solution1, index_drone_trip, index_in_trip, if_group = Neighborhood.groupTripInDroneRoute(
                        New_solution1, ChangePackages, ChangeInTruck, delivery_pos)
                    
                    if if_group and index_drone_trip >= 0 and index_in_trip >= 0:
                        # Successful grouping
                        NewSolution = Rearrange_index_trip(NewSolution, index_drone_trip, True)
                        
                        if delivery_pos > IndexOfReceiveCityInTruck:
                            # Forward direction
                            if (index_drone_trip < len(New_solution1[1]) and 
                                index_in_trip < len(New_solution1[1][index_drone_trip]) and
                                Function.sum_weight(New_solution1[1][index_drone_trip][index_in_trip][1]) <= 
                                0.5 * Data.drone_capacity):
                                New_solution1 = safe_choose_what_to_group(
                                    New_solution1, index_drone_trip, index_in_trip, True)
                            
                            if (source == 'drone' and 
                                initial_demand_package != demand_change_package and
                                initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity):
                                # Find current position of original pickup point
                                current_trip_idx = -1
                                current_pickup_idx = -1
                                
                                for t_idx in range(len(New_solution1[1])):
                                    for p_idx in range(len(New_solution1[1][t_idx])):
                                        if New_solution1[1][t_idx][p_idx][0] == pickup_city:
                                            current_trip_idx = t_idx
                                            current_pickup_idx = p_idx
                                            break
                                    if current_trip_idx >= 0:
                                        break
                                
                                if current_trip_idx >= 0 and current_pickup_idx >= 0:
                                    New_solution1 = safe_choose_what_to_group(
                                        New_solution1, current_trip_idx, current_pickup_idx, False)
                        else:
                            # Backward direction
                            if (source == 'drone' and 
                                initial_demand_package != demand_change_package and
                                initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity):
                                # Find current position of original pickup point
                                current_trip_idx = -1
                                current_pickup_idx = -1
                                
                                for t_idx in range(len(New_solution1[1])):
                                    for p_idx in range(len(New_solution1[1][t_idx])):
                                        if New_solution1[1][t_idx][p_idx][0] == pickup_city:
                                            current_trip_idx = t_idx
                                            current_pickup_idx = p_idx
                                            break
                                    if current_trip_idx >= 0:
                                        break
                                
                                if current_trip_idx >= 0 and current_pickup_idx >= 0:
                                    New_solution1 = safe_choose_what_to_group(
                                        New_solution1, current_trip_idx, current_pickup_idx, True)
                            
                            if (index_drone_trip < len(New_solution1[1]) and 
                                index_in_trip < len(New_solution1[1][index_drone_trip]) and
                                Function.sum_weight(New_solution1[1][index_drone_trip][index_in_trip][1]) <= 
                                0.5 * Data.drone_capacity):
                                New_solution1 = safe_choose_what_to_group(
                                    New_solution1, index_drone_trip, index_in_trip, False)
                    
                    elif index_drone_trip >= 0 and index_in_trip >= 0:
                        # Failed grouping, but created new trip
                        if delivery_pos > IndexOfReceiveCityInTruck:
                            # Forward direction
                            if demand_change_package <= 0.5 * Data.drone_capacity:
                                New_solution1 = safe_choose_what_to_group(
                                    New_solution1, index_drone_trip, index_in_trip, True)
                            
                            if (source == 'drone' and 
                                initial_demand_package != demand_change_package and
                                initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity):
                                # Find current position of original pickup point
                                current_trip_idx = -1
                                current_pickup_idx = -1
                                
                                for t_idx in range(len(New_solution1[1])):
                                    for p_idx in range(len(New_solution1[1][t_idx])):
                                        if New_solution1[1][t_idx][p_idx][0] == pickup_city:
                                            current_trip_idx = t_idx
                                            current_pickup_idx = p_idx
                                            break
                                    if current_trip_idx >= 0:
                                        break
                                
                                if current_trip_idx >= 0 and current_pickup_idx >= 0:
                                    New_solution1 = safe_choose_what_to_group(
                                        New_solution1, current_trip_idx, current_pickup_idx, False)
                        else:
                            # Backward direction
                            if (source == 'drone' and 
                                initial_demand_package != demand_change_package and
                                initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity):
                                # Find current position of original pickup point
                                current_trip_idx = -1
                                current_pickup_idx = -1
                                
                                for t_idx in range(len(New_solution1[1])):
                                    for p_idx in range(len(New_solution1[1][t_idx])):
                                        if New_solution1[1][t_idx][p_idx][0] == pickup_city:
                                            current_trip_idx = t_idx
                                            current_pickup_idx = p_idx
                                            break
                                    if current_trip_idx >= 0:
                                        break
                                
                                if current_trip_idx >= 0 and current_pickup_idx >= 0:
                                    New_solution1 = safe_choose_what_to_group(
                                        New_solution1, current_trip_idx, current_pickup_idx, True)
                            
                            if demand_change_package <= 0.5 * Data.drone_capacity:
                                New_solution1 = safe_choose_what_to_group(
                                    New_solution1, index_drone_trip, index_in_trip, False)
                
                # Add to neighborhood if valid
                if New_solution1:
                    if (Function.has_duplicate_synchonize_point(New_solution1)):
                        print ("this solution has duplicate synchonixe point see drone que: \n")
                        print (New_solution1[1])
                    else:
                        temp = []
                        temp.append(New_solution1)
                        fit, dt, tt = Function.fitness(New_solution1)
                        temp.append([fit, dt, tt])
                        temp.append(-1)
                        temp.append(-1)
                        neighborhood.append(temp)
                
                if stop:
                    break
    
    return neighborhood

def Neighborghood_change_drone_route_max_pro_plus_for_specific_truck(solution, accept_truck_list):
    # print("solution0000: ", solution)
    neighborhood = []
    minus_for_number_of_trucks = Data.number_of_trucks
    Function.update_per_loop(solution)
    package = copy.deepcopy(solution[1])
    
    for i in range(Data.number_of_trucks):
        if i in accept_truck_list:
            pack = []
            for j in range(len(solution[0][i][0][1])):
                pack.append(solution[0][i][0][1][j])
            package.insert(0,[[0,pack]])
        else:
            minus_for_number_of_trucks -= 1
        
    # print("solution1111: ", solution)
    for i in reversed(range(len(package))):
        for j in reversed(range(len(package[i]))):
            if package[i][j][0] == 0:
                continue
            index_truck = Function.index_truck_of_cities[package[i][j][0]]
            
            remained_pack = len(package[i][j][1])
            if index_truck in accept_truck_list:
                for k in range(len(solution[0][index_truck])):
                    city = solution[0][index_truck][k][0]
                    if city in package[i][j][1]:
                        remained_pack -= 1
                        package[i][j][1].remove(city)
                        if Data.release_date[city] > 0:
                            package[i][j][1].append(city)
                    if remained_pack == 0:
                        break    
        
    # print(package)
    # print("solution111: ", solution)
    for i in range(len(package)):
        for j in range(len(package[i])):
            if package[i][j][0] != 0:
                if Function.index_truck_of_cities[package[i][j][0]] not in accept_truck_list:
                    continue
            initial_demand_package = Function.sum_weight(package[i][j][1]) 
            Total_case = takeAmountBeginAndEndPackage(package[i][j][1])
            for ii in range(len(Total_case)):
                NewSolution = copy.deepcopy(solution)
                ChangePackages = Total_case[ii]
                ChangeInTruck = Function.city_in_which_truck(solution, package[i][j][1][0])
                # print("ChangePackages: ", ChangePackages)
                # print("solution: ", NewSolution)
                IndexOfReceiveCityInTruck = -1
                # print("Package: ", Total_case[ii])
                
                for l in range(len(ChangePackages)):
                    # print("hehe: ", ChangePackages)
                    #print("-----------------------------", ChangePackages)
                    ChangePackage = ChangePackages[l]
                    
                    #ChangePackages.append(ChangePackage)
                    #print(ChangePackage)
                    #print(ChangePackages)
                    # Xoá ở New Solution
                    if package[i][j][0] != 0:
                        NewSolution[1][i-minus_for_number_of_trucks][j][1].remove(ChangePackage)
                        for ii in range(len(NewSolution[0][ChangeInTruck])):
                            if ChangePackage in NewSolution[0][ChangeInTruck][ii][1]:
                                IndexOfReceiveCityInTruck = ii
                                NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
                                break
                    else:
                        for ii in range(len(NewSolution[0][ChangeInTruck])):
                            if ChangePackage in NewSolution[0][ChangeInTruck][ii][1]:
                                IndexOfReceiveCityInTruck = ii
                                NewSolution[0][ChangeInTruck][ii][1].remove(ChangePackage)
                                break
                    #print(ChangePackages)
                #print("Change-1: ",ChangePackages)
                # print("heheee: ", IndexOfReceiveCityInTruck)
                if Function.sum_weight(ChangePackages) > Data.drone_capacity:
                    continue
                if NewSolution[0][ChangeInTruck][IndexOfReceiveCityInTruck][0] in ChangePackages:
                    continue
                if package[i][j][0] != 0:
                    if NewSolution[1][i-minus_for_number_of_trucks][j][1] == []:
                        NewSolution[1][i-minus_for_number_of_trucks].pop(j)
                        if NewSolution[1][i-minus_for_number_of_trucks] == []:
                            NewSolution[1].pop(i-minus_for_number_of_trucks)
                stop = False
                for l in range(len(NewSolution[0][ChangeInTruck])):
                    
                    if l == IndexOfReceiveCityInTruck:
                        continue

                    New_solution1 = copy.deepcopy(NewSolution)
                    # print("Package: ", ChangePackages)
                    
                    # for iii in range(Data.number_of_trucks):
                    #     print(New_solution1[0][iii])
                    # print(New_solution1[1])
                    # print("------")
                    
                    demand_change_package = Function.sum_weight(ChangePackages)
                    
                    ReceiveCity = New_solution1[0][ChangeInTruck][l][0]
                    if ReceiveCity in ChangePackages: 
                        stop = True
                    
                    if Data.euclid_flight_matrix[0][ReceiveCity] * 2 + Data.unloading_time > Data.drone_limit_time:
                        if stop:
                            break
                        else:
                            continue
                    
                    # Trường hợp 1: Điểm giao đến không phải điểm nhận hàng
                    if New_solution1[0][ChangeInTruck][l][1] == []:
                        # Add điểm giao hàng tại truck route
                        for ll in range(len(ChangePackages)):
                            New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + [ChangePackages[ll]]
                        #Add điểm giao hàng tại drone package
                        if Data.euclid_flight_matrix[0][ReceiveCity] * 2 <= Data.drone_limit_time:
                            if l != 0:
                                index_drone_trip = -1
                                index_in_trip = -1
                                New_solution1, index_drone_trip, index_in_trip = Neighborhood.addNewTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)
                            
                            # print(New_solution1)
                            # print("----after1-----")
                            
                            if l > IndexOfReceiveCityInTruck:
                                if demand_change_package <= 0.5 * Data.drone_capacity:
                                    New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, True)
                                if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
                                    if initial_demand_package != demand_change_package:
                                        if i - minus_for_number_of_trucks >= 0:
                                            New_solution1 = choose_what_to_group(New_solution1, i - minus_for_number_of_trucks, j, False)
                            else:
                                if initial_demand_package != demand_change_package:
                                    if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
                                        if l != 0:
                                            New_solution1 = choose_what_to_group(New_solution1, i - minus_for_number_of_trucks + 1, j, True)
                                        else:
                                            New_solution1 = choose_what_to_group(New_solution1, i - minus_for_number_of_trucks, j, True)
                                if demand_change_package <= 0.5 * Data.drone_capacity:
                                    if l != 0:
                                        New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, False)

                                
                            
                        else:
                            continue
                    # Trường hợp 2: Điểm giao đến cũng là một điểm nhận hàng
                    else:
                        
                        # Add điểm giao hàng tại truck route
                        for ll in range(len(ChangePackages)):
                            New_solution1[0][ChangeInTruck][l][1] = New_solution1[0][ChangeInTruck][l][1] + [ChangePackages[ll]]
                        #Add điểm giao hàng tại drone package
                        if_group = True
                        if l != 0: 
                            index_drone_trip = -1
                            index_in_trip = -1
                            New_solution1, index_drone_trip, index_in_trip, if_group = Neighborhood.groupTripInDroneRoute(New_solution1, ChangePackages, ChangeInTruck, l)
                        
                        # print(New_solution1)
                        # print("----after1-----")
                        
                        if if_group:    # Gộp thành công
                            
                            if l > IndexOfReceiveCityInTruck:
                                # print("IndexOfReceiveCityInTruck: ", IndexOfReceiveCityInTruck)
                                # print("l: ", l)
                                # print("index_drone_trip: ", index_drone_trip)
                                if Function.sum_weight(New_solution1[1][index_drone_trip][index_in_trip][1]) <= 0.5 * Data.drone_capacity:
                                    New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, True)
                                if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
                                    if initial_demand_package != demand_change_package:
                                        if i - minus_for_number_of_trucks >= 0:
                                            New_solution1 = choose_what_to_group(New_solution1, i - minus_for_number_of_trucks, j, False)
                            else:
                                if initial_demand_package != demand_change_package:
                                    if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
                                        New_solution1 = choose_what_to_group(New_solution1, i - minus_for_number_of_trucks, j, True)
                                if l != 0:
                                    if Function.sum_weight(New_solution1[1][index_drone_trip][index_in_trip][1]) <= 0.5 * Data.drone_capacity:
                                        New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, False)
                        
                        else:           # Gộp thất bại, tạo trip mới riêng
                            if l > IndexOfReceiveCityInTruck:
                                if demand_change_package <= 0.5 * Data.drone_capacity:
                                    New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, True)
                                if i - minus_for_number_of_trucks >= 0:
                                    if initial_demand_package != demand_change_package:
                                        if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
                                            New_solution1 = choose_what_to_group(New_solution1, i - minus_for_number_of_trucks, j, False)
                            else:
                                if initial_demand_package != demand_change_package:
                                    if initial_demand_package - demand_change_package <= 0.5 * Data.drone_capacity:
                                        # print("index_drone_trip11: ", i - Data.number_of_trucks, "index_in_trip1: ", j)
                                        # print("second: ", New_solution1)
                                        New_solution1 = choose_what_to_group(New_solution1, i - minus_for_number_of_trucks + 1, j, True)
                                    
                                if demand_change_package <= 0.5 * Data.drone_capacity:
                                    if l != 0:
                                        New_solution1 = choose_what_to_group(New_solution1, index_drone_trip, index_in_trip, False)
                    # print(New_solution1)
                    # print(Function.fitness(New_solution1)[0])
                    # print(len(neighborhood))
                    # print("-------------------------------")
                    
                    temp = []
                    temp.append(New_solution1)
                    fit, dt, tt = Function.fitness(New_solution1)
                    temp.append([fit, dt, tt])
                    temp.append(-1)
                    temp.append(-1)
                    neighborhood.append(temp)
                    if stop == True:
                        break              
    return neighborhood

def takeRetrieval(Package, ChangePackes, PackageTrip, CurrentNumber, CurrentAmount, TakenAmount):
    if CurrentAmount == 0:
        for i in range(len(PackageTrip)- (TakenAmount - CurrentAmount) + 1):          
            Package[CurrentAmount] = PackageTrip[i]
            CurrentNumber = i + 1
            if CurrentAmount == TakenAmount - 1:
                temp = copy.deepcopy(Package)
                ChangePackes.append(temp)
            else:
                takeRetrieval(Package, ChangePackes, PackageTrip, CurrentNumber, CurrentAmount + 1, TakenAmount)
    else:
        for i in range(CurrentNumber, len(PackageTrip)- (TakenAmount - CurrentAmount) + 1):
            Package[CurrentAmount] = PackageTrip[i]
            CurrentNumber = i + 1
            if CurrentAmount == TakenAmount - 1:
                temp = copy.deepcopy(Package)
                ChangePackes.append(temp)
            else:
                takeRetrieval(Package, ChangePackes, PackageTrip, CurrentNumber, CurrentAmount + 1, TakenAmount)

def takePermutationPackage(PackageTrip, TakenAmount):
    ChangePackages = []
    Package = [-1] * TakenAmount
    takeRetrieval(Package, ChangePackages, PackageTrip, 0, 0, TakenAmount)
    return ChangePackages

def takeAmountBeginAndEndPackage(PackageTrip):
    ChangePackages = []
    for i in range(1, len(PackageTrip) + 1):
        if len(PackageTrip) == i:
            package = copy.deepcopy(PackageTrip)
            ChangePackages.append(package)
        else:
            package1 = copy.deepcopy(PackageTrip[:i])
            ChangePackages.append(package1)
            package2 = copy.deepcopy(PackageTrip[-i:])
            ChangePackages.append(package2)
    return ChangePackages

def Rearrange_index_trip(solution, index_trip, forward):
    max_release_date_time = Function.max_release_date_update(solution[1][index_trip])
    shortest_route_by_point, shortest_route_by_truck = Function.find_drone_flight_shortest(solution, solution[1][index_trip])
    time_fly = Data.euclid_flight_matrix[0][shortest_route_by_point[0]] + Data.euclid_flight_matrix[shortest_route_by_point[-1]][0]
    for i in range(len(shortest_route_by_point) - 1):
        time_fly += Data.euclid_flight_matrix[shortest_route_by_point[i]][shortest_route_by_point[i+1]]
    total_time = time_fly + max_release_date_time 
    next_index = index_trip
    index_truck = []
    for i in range(len(solution[1][index_trip])):
        index_truck.append(Function.index_truck_of_cities[solution[1][index_trip][i][0]])
    max_index = len(solution[1]) - 1
    stop_loop = False
    if forward:
        convert = True
        stop = False
        while not stop:
            if next_index == max_index:
                break
            for i in range(len(solution[1][next_index + 1])):
                if Function.index_truck_of_cities[solution[1][next_index + 1][i][0]] in index_truck:
                    stop_loop = True
            if stop_loop:
                break
            next_index += 1
            compared_time_fly = Function.cal_time_fly_a_trip(solution[1][next_index])
            if compared_time_fly + Function.max_release_date_update(solution[1][next_index]) < total_time:
                convert = False
            else:
                stop = True
        if convert:
            stop = False
            while not stop:
                if next_index == 0:
                    break
                for i in range(len(solution[1][next_index - 1])):
                    if Function.index_truck_of_cities[solution[1][next_index - 1][i][0]] in index_truck:
                        stop_loop = True
                if stop_loop:
                    break
                next_index -= 1
                compared_time_fly = Function.cal_time_fly_a_trip(solution[1][next_index])
                if compared_time_fly + Function.max_release_date_update(solution[1][next_index]) < total_time:
                    stop = True
    else:
        convert = True
        stop = False
        while not stop:
            if next_index == 0:
                break
            for i in range(len(solution[1][next_index - 1])):
                if Function.index_truck_of_cities[solution[1][next_index - 1][i][0]] in index_truck:
                    stop_loop = True
            if stop_loop:
                break
            next_index -= 1
            compared_time_fly = Function.cal_time_fly_a_trip(solution[1][next_index])
            if compared_time_fly + Function.max_release_date_update(solution[1][next_index]) > total_time:
                convert = False
            else:
                stop = True
        if convert:
            stop = False
            while not stop:
                if next_index == max_index:
                    break
                for i in range(len(solution[1][next_index + 1])):
                    if Function.index_truck_of_cities[solution[1][next_index + 1][i][0]] in index_truck:
                        stop_loop = True
                if stop_loop:
                    break
                next_index += 1
                compared_time_fly = Function.cal_time_fly_a_trip(solution[1][next_index])
                if compared_time_fly + Function.max_release_date_update(solution[1][next_index]) > total_time:
                    stop = True
                    
    if next_index > index_trip:
        temp = solution[1][index_trip]
        solution[1].pop(index_trip)
        solution[1].insert(next_index, temp)
    elif next_index < index_trip:
        temp = solution[1][index_trip]
        solution[1].pop(index_trip)
        solution[1].insert(next_index, temp)
                
    return solution

def Change_index_trip(solution, index_of_trip, to_index):
    temp = solution[1][index_of_trip]
    solution[1].pop(index_of_trip)
    if index_of_trip > to_index:
        solution[1].insert(to_index, temp)
    else:
        solution[1].insert(to_index - 1, temp)
    return solution

def Neighborhood_change_index_trip(solution):
    Function.update_per_loop(solution)
    neighborhood = []
    if Data.number_of_trucks < 2:
        return neighborhood
    for i in range(len(solution[1])):
        below = i
        above = i
        list_city_stop = []
        for j in range(len(solution[1][i])):
            list_city_stop.append(Function.index_truck_of_cities[solution[1][i][j][0]])
        for j in range(i + 1, len(solution[1])):
            stop = False
            for k in range(len(solution[1][j])):
                if Function.index_truck_of_cities[solution[1][j][k][0]] in list_city_stop:
                    stop = True
            if stop:
                break
            else:
                above += 1
        for j in range(i - 1, -1, -1):
            stop = False
            for k in range(len(solution[1][j])):
                if Function.index_truck_of_cities[solution[1][j][k][0]] in list_city_stop:
                    stop = True
            if stop:
                break
            else:
                below -= 1
        # print(i, ": ", below, " ", above)
        for j in range(below, above + 1):
            if j == i or j == i + 1:
                continue
            new_solution = copy.deepcopy(solution)
            new_solution = Change_index_trip(new_solution, i, j)
            
            
            # print(new_solution[0])
            # print(new_solution[1])
            # print(Function.Check_if_feasible(new_solution))
            # print(Function.fitness(new_solution)[0])
            # print(len(neighborhood))
            # print("--------------")
            temp = []
            if (Function.has_duplicate_synchonize_point(new_solution)):
                print ("this solution has duplicate synchonixe point see drone que: \n")
                print (new_solution[1])
            else:
                temp.append(new_solution)
                fit, dt, tt = Function.fitness(new_solution)
                temp.append([fit, dt, tt])
                temp.append(-1)
                temp.append(-1)
                neighborhood.append(temp)
    return neighborhood
 