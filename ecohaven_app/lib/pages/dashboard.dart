import 'package:ecohaven_app/pages/riderProfile.dart';
import 'package:flutter/material.dart';
import 'available_deliveries.dart';
import 'ongoing_delivery.dart';
import 'completed_deliveries.dart';

class Dashboard extends StatefulWidget {
  final int rider_id;
  const Dashboard({Key? key, required this.rider_id}) : super(key: key); // ✅ required rider_id

  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  int _selectedIndex = 0;

  final Color primaryColor = const Color(0xFF133157);

  @override
  Widget build(BuildContext context) {
    final List<Widget> _pages = [
      AvailableDeliveriesPage(riderId: widget.rider_id),
      OngoingDeliveryPage(riderId: widget.rider_id),
      CompletedDeliveriesPage(riderId: widget.rider_id),
      RiderProfilePage(riderId: widget.rider_id),
    ];

    return Scaffold(
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        selectedItemColor: primaryColor,
        unselectedItemColor: Colors.grey,
        selectedLabelStyle: TextStyle(fontWeight: FontWeight.w600),
        onTap: (index) => setState(() => _selectedIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.list_alt),
            label: 'Available',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.local_shipping),
            label: 'My Deliveries',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.check_circle),
            label: 'Completed',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class PlaceholderWidget extends StatelessWidget {
  final String label;
  const PlaceholderWidget({Key? key, required this.label}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text(
        '$label Page',
        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
      ),
    );
  }
}
