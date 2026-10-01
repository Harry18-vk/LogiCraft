from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser
from fleet.models import Vehicle, Driver, MaintenanceRecord
from warehouse.models import Warehouse, InventoryItem
from transport.models import Route, Schedule
from shipments.models import Shipment, ShipmentStatusHistory
from bookings.models import Booking


class Command(BaseCommand):
    help = "Populate LogiCraft database with realistic prototype logistics data."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding LogiCraft sample data..."))

        # 1. Users
        admin_user, _ = CustomUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@logicraft.com",
                "role": CustomUser.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Divya",
                "last_name": "Admin",
            }
        )
        admin_user.set_password("admin123")
        admin_user.save()

        manager_user, _ = CustomUser.objects.get_or_create(
            username="manager1",
            defaults={
                "email": "manager@logicraft.com",
                "role": CustomUser.Role.LOGISTICS_MANAGER,
                "is_staff": True,
                "first_name": "Suresh",
                "last_name": "Kumar",
                "phone_number": "+91-9876543210",
                "city": "Delhi",
            }
        )
        manager_user.set_password("manager123")
        manager_user.save()

        # 2. Warehouses
        wh_delhi, _ = Warehouse.objects.get_or_create(
            code="WH-DEL-01",
            defaults={
                "name": "Delhi North Central Hub",
                "city": "New Delhi",
                "state": "Delhi",
                "address": "Plot 42, Okhla Industrial Area Phase III",
                "total_capacity_sqft": 75000.0,
                "manager_name": "Rohan Verma",
                "contact_phone": "+91-9811002233",
                "status": Warehouse.Status.ACTIVE,
                "latitude": 28.5355,
                "longitude": 77.2678,
            }
        )
        wh_delhi.latitude = 28.5355
        wh_delhi.longitude = 77.2678
        wh_delhi.save()

        wh_mumbai, _ = Warehouse.objects.get_or_create(
            code="WH-MUM-01",
            defaults={
                "name": "Mumbai Port & Coastal Logistics Center",
                "city": "Navi Mumbai",
                "state": "Maharashtra",
                "address": "Sector 19, Turbhe MIDC",
                "total_capacity_sqft": 120000.0,
                "manager_name": "Pooja Patil",
                "contact_phone": "+91-9822334455",
                "status": Warehouse.Status.ACTIVE,
                "latitude": 19.0560,
                "longitude": 73.0169,
            }
        )
        wh_mumbai.latitude = 19.0560
        wh_mumbai.longitude = 73.0169
        wh_mumbai.save()

        wh_blr, _ = Warehouse.objects.get_or_create(
            code="WH-BLR-01",
            defaults={
                "name": "Bengaluru Tech & Electronics Hub",
                "city": "Bengaluru",
                "state": "Karnataka",
                "address": "Whitefield Export Promotion Industrial Park",
                "total_capacity_sqft": 60000.0,
                "manager_name": "Karthik Gowda",
                "contact_phone": "+91-9844556677",
                "status": Warehouse.Status.ACTIVE,
                "latitude": 12.9698,
                "longitude": 77.7500,
            }
        )
        wh_blr.latitude = 12.9698
        wh_blr.longitude = 77.7500
        wh_blr.save()

        # 3. Inventory Items
        inventory_data = [
            (wh_delhi, "SKU-ELEC-01", "55-inch 4K Smart TV Units", InventoryItem.Category.ELECTRONICS, 140, 18.5),
            (wh_delhi, "SKU-RET-09", "Cotton Apparel Consignment (Cartons)", InventoryItem.Category.RETAIL, 420, 12.0),
            (wh_mumbai, "SKU-IND-50", "Industrial Hydraulic Pumps", InventoryItem.Category.INDUSTRIAL, 65, 85.0),
            (wh_mumbai, "SKU-PER-12", "Vaccines & Cold-Storage Medical Kits", InventoryItem.Category.PHARMACEUTICAL, 300, 2.5),
            (wh_blr, "SKU-ELEC-44", "High-Density Server Racks", InventoryItem.Category.ELECTRONICS, 45, 110.0),
            (wh_blr, "SKU-RET-15", "Office Ergonomic Workstations", InventoryItem.Category.RETAIL, 180, 22.0),
        ]
        for wh, sku, name, cat, qty, wt in inventory_data:
            InventoryItem.objects.get_or_create(
                warehouse=wh,
                sku=sku,
                defaults={"item_name": name, "category": cat, "quantity": qty, "unit_weight_kg": wt}
            )

        # 4. Vehicles
        v1, _ = Vehicle.objects.get_or_create(
            reg_number="DL-01-AB-1001",
            defaults={
                "model_name": "Tata Signa 4825.TK Heavy Hauler",
                "vehicle_type": Vehicle.VehicleType.HEAVY_TRUCK,
                "capacity_kg": 28000.0,
                "fuel_type": Vehicle.FuelType.DIESEL,
                "odometer_km": 64200.0,
                "status": Vehicle.Status.ON_TRIP,
                "current_location": "En route Delhi to Mumbai (NH 48)",
                "latitude": 26.9124,
                "longitude": 75.7873,
            }
        )
        v1.latitude = 26.9124
        v1.longitude = 75.7873
        v1.save()

        v2, _ = Vehicle.objects.get_or_create(
            reg_number="MH-04-CD-2020",
            defaults={
                "model_name": "Ashok Leyland Ecomet Star 1415",
                "vehicle_type": Vehicle.VehicleType.MEDIUM_TRUCK,
                "capacity_kg": 9500.0,
                "fuel_type": Vehicle.FuelType.DIESEL,
                "odometer_km": 38150.0,
                "status": Vehicle.Status.AVAILABLE,
                "current_location": "Mumbai Warehouse Hub",
                "latitude": 19.0560,
                "longitude": 73.0169,
            }
        )
        v2.latitude = 19.0560
        v2.longitude = 73.0169
        v2.save()

        v3, _ = Vehicle.objects.get_or_create(
            reg_number="KA-03-EF-3030",
            defaults={
                "model_name": "Mahindra Bolero Maxi Truck Delivery",
                "vehicle_type": Vehicle.VehicleType.DELIVERY_VAN,
                "capacity_kg": 1800.0,
                "fuel_type": Vehicle.FuelType.CNG,
                "odometer_km": 19400.0,
                "status": Vehicle.Status.AVAILABLE,
                "current_location": "Bengaluru Tech Hub",
                "latitude": 12.9698,
                "longitude": 77.7500,
            }
        )
        v3.latitude = 12.9698
        v3.longitude = 77.7500
        v3.save()

        v_bus1, _ = Vehicle.objects.get_or_create(
            reg_number="DL-01-TR-9009",
            defaults={
                "model_name": "Volvo 9400 B11R Multi-Axle Intercity Coach",
                "vehicle_type": Vehicle.VehicleType.PASSENGER_BUS,
                "capacity_kg": 3500.0,
                "passenger_capacity": 45,
                "fuel_type": Vehicle.FuelType.DIESEL,
                "odometer_km": 112000.0,
                "status": Vehicle.Status.AVAILABLE,
                "current_location": "ISBT Kashmiri Gate, Delhi",
                "latitude": 28.6675,
                "longitude": 77.2285,
            }
        )
        v_bus1.latitude = 28.6675
        v_bus1.longitude = 77.2285
        v_bus1.save()


        # 5. Drivers
        driver_users_data = [
            ("driver_rajesh", "Rajesh", "Sharma", "DL-1420110098234", 12, v1),
            ("driver_vikram", "Vikram", "Singh", "MH-0320140065431", 8, v2),
            ("driver_anita", "Anita", "Deshmukh", "KA-0520160087652", 6, v3),
        ]
        for uname, fname, lname, lic, exp, veh in driver_users_data:
            u, _ = CustomUser.objects.get_or_create(
                username=uname,
                defaults={
                    "email": f"{uname}@logicraft.com",
                    "role": CustomUser.Role.DRIVER,
                    "first_name": fname,
                    "last_name": lname,
                    "phone_number": "+91-9711223344",
                }
            )
            u.set_password("driver123")
            u.save()
            Driver.objects.get_or_create(
                user=u,
                defaults={
                    "license_number": lic,
                    "license_expiry": date.today() + timedelta(days=730),
                    "years_of_experience": exp,
                    "assigned_vehicle": veh,
                    "status": Driver.Status.ON_TRIP if veh.status == Vehicle.Status.ON_TRIP else Driver.Status.ON_DUTY,
                }
            )

        # 6. Maintenance Record
        MaintenanceRecord.objects.get_or_create(
            vehicle=v1,
            service_date=date.today() - timedelta(days=15),
            defaults={
                "service_type": MaintenanceRecord.ServiceType.ROUTINE,
                "description": "50,000 km Scheduled engine oil change, air filter replacement, and tire pressure alignment.",
                "cost": 14500.00,
                "odometer_at_service": 62000.0,
                "status": MaintenanceRecord.Status.COMPLETED,
            }
        )

        # 7. Public Transport Routes & Schedules
        route1, _ = Route.objects.get_or_create(
            route_code="EXP-101",
            defaults={
                "source_city": "New Delhi",
                "source_terminal": "ISBT Kashmiri Gate Terminal 2",
                "destination_city": "Agra",
                "destination_terminal": "Idgah Bus Station, Agra",
                "distance_km": 235.0,
                "estimated_duration_hours": 3.75,
                "is_active": True,
            }
        )

        route2, _ = Route.objects.get_or_create(
            route_code="EXP-202",
            defaults={
                "source_city": "Mumbai",
                "source_terminal": "Dadar Asiad Bus Stand",
                "destination_city": "Pune",
                "destination_terminal": "Swargate Bus Terminal, Pune",
                "distance_km": 148.0,
                "estimated_duration_hours": 3.0,
                "is_active": True,
            }
        )

        sched1, _ = Schedule.objects.get_or_create(
            route=route1,
            departure_time=time(6, 30),
            defaults={
                "arrival_time": time(10, 15),
                "vehicle": v_bus1,
                "frequency": Schedule.Frequency.DAILY,
                "fare": 480.00,
                "total_seats": 45,
                "available_seats": 38,
            }
        )

        sched2, _ = Schedule.objects.get_or_create(
            route=route1,
            departure_time=time(14, 0),
            defaults={
                "arrival_time": time(17, 45),
                "vehicle": v_bus1,
                "frequency": Schedule.Frequency.DAILY,
                "fare": 520.00,
                "total_seats": 45,
                "available_seats": 42,
            }
        )

        # 8. Shipments & Timeline Milestones
        d1 = Driver.objects.get(user__username="driver_rajesh")
        s1, _ = Shipment.objects.get_or_create(
            tracking_number="LC-2026-DELMUM",
            defaults={
                "sender_name": "Bharat Electronics Ltd",
                "sender_phone": "+91-9810112233",
                "sender_address": "Sector 18, Noida, Uttar Pradesh",
                "receiver_name": "Reliance Digital Retail Hub",
                "receiver_phone": "+91-9820334455",
                "receiver_address": "Ghansoli Tech Park, Navi Mumbai",
                "origin_warehouse": wh_delhi,
                "destination_warehouse": wh_mumbai,
                "weight_kg": 4500.0,
                "description": "55-inch Smart TV units & display panels",
                "shipping_cost": 28500.00,
                "assigned_vehicle": v1,
                "assigned_driver": d1,
                "current_status": Shipment.Status.IN_TRANSIT,
                "estimated_delivery": date.today() + timedelta(days=2),
                "created_by": manager_user,
            }
        )

        # Milestones for s1
        if not ShipmentStatusHistory.objects.filter(shipment=s1, status=Shipment.Status.BOOKED).exists():
            ShipmentStatusHistory.objects.create(
                shipment=s1,
                status=Shipment.Status.BOOKED,
                location_checkpoint="Delhi North Central Hub",
                notes="Shipment booked and verified"
            )
        if not ShipmentStatusHistory.objects.filter(shipment=s1, status=Shipment.Status.PICKED_UP).exists():
            ShipmentStatusHistory.objects.create(
                shipment=s1,
                status=Shipment.Status.PICKED_UP,
                location_checkpoint="Noida Factory Gate 4",
                notes="Cargo loaded onto Tata Signa 4825"
            )
        if not ShipmentStatusHistory.objects.filter(shipment=s1, status=Shipment.Status.IN_TRANSIT).exists():
            ShipmentStatusHistory.objects.create(
                shipment=s1,
                status=Shipment.Status.IN_TRANSIT,
                location_checkpoint="Jaipur Bypass Highway Toll",
                notes="Vehicle cleared toll checkpoint on schedule"
            )

        # 9. Bookings
        Booking.objects.get_or_create(
            ticket_number="TKT-DL-1001",
            defaults={
                "schedule": sched1,
                "user": admin_user,
                "passenger_name": "Aakash Mehta",
                "passenger_phone": "+91-9876501234",
                "passenger_email": "aakash@example.com",
                "travel_date": date.today() + timedelta(days=1),
                "seat_number": "12A",
                "fare_paid": 480.00,
                "status": Booking.Status.CONFIRMED,
            }
        )

        self.stdout.write(self.style.SUCCESS("LogiCraft database successfully populated!"))
