import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:ecohaven_app/configport.dart';

class AvailableDeliveriesPage extends StatefulWidget {
  final int riderId;
  const AvailableDeliveriesPage({super.key, required this.riderId});

  @override
  State<AvailableDeliveriesPage> createState() => _AvailableDeliveriesPageState();
}

class _AvailableDeliveriesPageState extends State<AvailableDeliveriesPage> {
  List<dynamic> parcels = [];
  final primaryColor = const Color(0xFF133157);
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    _fetchDeliveries();
  }

  Future<void> _fetchDeliveries() async {
    setState(() => isLoading = true);
    try {
     final response = await http.get(
  Uri.parse('${Config.baseUrl}/rider_dashboardmobile?rider_id=${widget.riderId}'),
);
print(widget.riderId);

      if (response.statusCode == 200) {
        setState(() => parcels = jsonDecode(response.body));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to load deliveries')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> _assignDelivery(String orderId) async {
    setState(() => isLoading = true);
    try {
      final response = await http.post(
        Uri.parse('${Config.baseUrl}/assign_delivery'),
        body: {
          'order_id': orderId,
          'rider_id': widget.riderId.toString(),
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['message'] != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(data['message'])),
          );
          _fetchDeliveries(); // Refresh list
        } else if (data['error'] != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${data['error']}')),
          );
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to assign order')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  void _showConfirmDialog(String orderId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Assign Delivery'),
        content: const Text('Are you sure you want to assign this delivery to yourself?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _assignDelivery(orderId);
            },
            child: const Text('Assign'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Available Deliveries'),
        backgroundColor: primaryColor,
        titleTextStyle: TextStyle(color: Colors.white),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : parcels.isEmpty
              ? const Center(child: Text('No available deliveries'))
              : ListView.builder(
                  itemCount: parcels.length,
                  itemBuilder: (context, index) {
                    final parcel = parcels[index];
                    return DeliveryCard(
                      tracking: parcel['order_id'].toString(),
                      name: parcel['fullname'],
                      address: parcel['full_address'],
                      onAssign: () => _showConfirmDialog(parcel['order_id'].toString()),
                    );
                  },
                ),
    );
  }
}

class DeliveryCard extends StatelessWidget {
  final String tracking;
  final String name;
  final String address;
  final VoidCallback onAssign;
  final Color primaryColor = const Color(0xFF133157);

  const DeliveryCard({
    super.key,
    required this.tracking,
    required this.name,
    required this.address,
    required this.onAssign,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              tracking,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 6),
            Text(name, style: TextStyle(color: Colors.grey[900])),
            Text(address, style: TextStyle(color: Colors.grey[900])),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton(
                onPressed: onAssign,
                style: ElevatedButton.styleFrom(
                  backgroundColor: primaryColor,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 10,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Assign to Me',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
