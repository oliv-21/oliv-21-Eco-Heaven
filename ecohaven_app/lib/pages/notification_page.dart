import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:ecohaven_app/pages/profile_page.dart';
import '/pages/homepage.dart';
import 'package:ecohaven_app/pages/order_history.dart';
import 'dart:convert';
import 'package:ecohaven_app/configport.dart';

class NotificationPage extends StatefulWidget {
  final int buyer_id;
  const NotificationPage({super.key, required this.buyer_id});

  @override
  _NotificationPageState createState() => _NotificationPageState();
}

class _NotificationPageState extends State<NotificationPage> {
  int _selectedIndex = 1;
  List<NotificationItem> _notifications = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchNotifications();
  }

  Future<void> _fetchNotifications() async {
    try {
      final response = await http.get(
        Uri.parse('${Config.baseUrl}/notificationMobile?buyer_id=${widget.buyer_id}'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _notifications = _buildNotifications(
          reports: data['reports'] ?? [],
          orders: data['orders'] ?? [],
          cancelled: data['cancelled'] ?? [],
        );
      } else {
        throw Exception('Failed to load notifications');
      }
    } catch (e) {
      // Fallback to local notifications if API fails
      _notifications = _buildFallbackNotifications();
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  List<NotificationItem> _buildFallbackNotifications() {
    return [
      NotificationItem(
        title: 'Order Shipped',
        subtitle: 'Your order #1234 has been shipped.',
        time: '2h ago',
        icon: Icons.local_shipping,
      ),
      NotificationItem(
        title: 'New Promotion!',
        subtitle: 'Check out our latest discounts!',
        time: '5h ago',
        icon: Icons.campaign,
      ),
      NotificationItem(
        title: 'Payment Received',
        subtitle: 'We have received your payment.',
        time: '1d ago',
        icon: Icons.payment,
      ),
    ];
  }

  List<NotificationItem> _buildNotifications({
    required List<dynamic> reports,
    required List<dynamic> orders,
    required List<dynamic> cancelled,
  }) {
    final notifications = <NotificationItem>[];
    
    // Add reports notifications
    for (final report in reports) {
      notifications.add(
        NotificationItem(
          title: 'Report Status',
          subtitle: 'Report against ${report['shop_name'] ?? 'seller'}',
          time: 'Recently',
          icon: Icons.warning_amber,
        ),
      );
    }

    // Add cancelled orders notifications
    for (final cancel in cancelled) {
      notifications.add(
        NotificationItem(
          title: 'Order Cancelled',
          subtitle: '${cancel['shop_name'] ?? 'Seller'}: ${cancel['cancel_reason'] ?? 'Order cancelled'}',
          time: 'Recently',
          icon: Icons.cancel,
        ),
      );
    }

    // Add order status notifications
    for (final order in orders) {
      notifications.add(
        NotificationItem(
          title: 'Order Update',
          subtitle: '${order['product_name'] ?? 'Product'}: ${order['order_status'] ?? 'In progress'}',
          time: 'Recently',
          icon: Icons.shopping_bag,
        ),
      );
    }

    return notifications.isNotEmpty ? notifications : _buildFallbackNotifications();
  }

  void _onItemTapped(int index) {
    if (index != _selectedIndex) {
      switch (index) {
        case 0:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => HomePage(buyer_id: widget.buyer_id)),
          );
          break;
        case 1:
          break;
        case 2:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => OrderHistoryPage(buyer_id: widget.buyer_id)),
          );
          break;
        case 3:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => ProfilePage(buyer_id: widget.buyer_id)),
          );
          break;
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        backgroundColor: const Color(0xFFADC8EE),
        automaticallyImplyLeading: false,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _fetchNotifications,
              child: ListView.builder(
                itemCount: _notifications.length,
                itemBuilder: (context, index) {
                  final notification = _notifications[index];
                  return ListTile(
                    leading: Icon(notification.icon, color: const Color(0xFF133056)),
                    title: Text(
                      notification.title,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(notification.subtitle),
                    trailing: Text(
                      notification.time,
                      style: const TextStyle(color: Colors.grey),
                    ),
                  );
                },
              ),
            ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: const Color(0xFF133056),
        unselectedItemColor: Colors.grey[800],
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.notifications_outlined),
            activeIcon: Icon(Icons.notifications),
            label: 'Notifications',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_outlined),
            activeIcon: Icon(Icons.history),
            label: 'Order History',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class NotificationItem {
  final String title;
  final String subtitle;
  final String time;
  final IconData icon;

  NotificationItem({
    required this.title,
    required this.subtitle,
    required this.time,
    required this.icon,
  });
}
