from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from fleet.models import Vehicle
from shipments.models import Shipment
from warehouse.models import Warehouse
from transport.models import Route, Schedule


class LogiCraftCoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_superuser(
            username='testadmin',
            email='testadmin@logicraft.com',
            password='password123'
        )
        self.wh = Warehouse.objects.create(
            code="WH-TEST",
            name="Test Warehouse",
            city="Delhi",
            state="Delhi",
            address="Test address"
        )
        self.vehicle = Vehicle.objects.create(
            reg_number="DL-01-TEST",
            model_name="Tata Test 123",
            capacity_kg=5000.0
        )
        self.shipment = Shipment.objects.create(
            tracking_number="LC-TEST-999",
            sender_name="Sender Co",
            sender_phone="1234567890",
            sender_address="Delhi",
            receiver_name="Receiver Co",
            receiver_phone="9876543210",
            receiver_address="Mumbai",
            weight_kg=120.0,
            description="Sample Cargo",
            origin_warehouse=self.wh
        )

    def test_public_tracker_accessible_unauthenticated(self):
        url = reverse('shipments:track_public')
        response = self.client.get(url, {'tracking_number': 'LC-TEST-999'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LC-TEST-999')

    def test_dashboard_requires_login(self):
        url = reverse('dashboard:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_when_logged_in(self):
        self.client.login(username='testadmin', password='password123')
        url = reverse('dashboard:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logistics & Fleet Dashboard')

    def test_fleet_views(self):
        self.client.login(username='testadmin', password='password123')
        res = self.client.get(reverse('fleet:fleet_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'DL-01-TEST')

        detail_res = self.client.get(reverse('fleet:vehicle_detail', args=[self.vehicle.id]))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, 'Tata Test 123')

    def test_warehouse_views(self):
        self.client.login(username='testadmin', password='password123')
        res = self.client.get(reverse('warehouse:warehouse_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'WH-TEST')
