import 'package:ecohaven_app/configport.dart';
import 'package:flutter/material.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';

class TrackOrderPage extends StatelessWidget {
  final Map<String, dynamic> orderDetails;

  const TrackOrderPage({Key? key, required this.orderDetails}) : super(key: key);

  // Define the order steps in sequence
  static const List<String> orderSteps = [
    'Order Placed',     // Treat 'Pending' as this step
    'Approved',
    'Shipped',
    'Out For Delivery',
    'Completed',
  ];

  // Map status string to step index
  int getCurrentStep(String? status) {
    if (status == null) return 0;
    switch (status.toLowerCase()) {
      case 'pending':
      case 'order placed':
        return 0;
      case 'approved':
        return 1;
      case 'shipped':
        return 2;
      case 'out for delivery':
        return 3;
      case 'completed':
        return 4;
      case 'cancelled':
        return -1; // Special case for cancelled
      default:
        return 0;
    }
  }
  Future<void> markOrderCompleted(BuildContext context, String orderId) async {
  final uri = Uri.parse('${Config.baseUrl}/api/markOrderCompleted');
  try {
    final response = await http.post(uri, body: {'order_id': orderId});
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? 'Order marked completed')),
        );
        // Optionally update UI or refresh data here
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? 'Failed to update order')),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Server error: ${response.statusCode}')),
      );
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error: $e')),
    );
  }
}

  @override
  Widget build(BuildContext context) {
    final status = orderDetails['order_status']?.toString().toLowerCase() ?? '';
    final currentStep = getCurrentStep(status);
    final deliveryStatus = orderDetails['delivery_status']?.toString().toLowerCase() ?? '';
    print(deliveryStatus);

    return Scaffold(
      appBar: AppBar(
        title: Text('Track Order #${orderDetails['order_id']}'),
        backgroundColor: const Color(0xFF133056),
        titleTextStyle: const TextStyle(color: Colors.white),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Product Info Card
          Card(
            elevation: 3,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    orderDetails['product_name'] ?? 'Product',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF133056),
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (orderDetails['image'] != null && orderDetails['image'].isNotEmpty)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.network(
                        '${Config.baseUrl}/assets/upload/${orderDetails['image']}',
                        height: 180,
                        width: double.infinity,
                        fit: BoxFit.fill,
                        errorBuilder: (context, error, stackTrace) => Container(
                          height: 180,
                          color: Colors.grey[300],
                          child: const Center(child: Icon(Icons.broken_image, size: 50)),
                        ),
                      ),
                    ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 16,
                    runSpacing: 8,
                    children: [
                      _infoChip('Quantity', '${orderDetails['quantity'] ?? '-'}'),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Total Price: ₱${orderDetails['total_price'] ?? '-'}',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF133056),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Order Date: ${orderDetails['created_at'] ?? '-'}',
                    style: TextStyle(color: Colors.grey[700]),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Order Status Section Title
          Text(
            'Order Status',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
          const SizedBox(height: 12),

          // Show stepper if not cancelled
          if (currentStep >= 0)
            _buildOrderProgress(currentStep)
          else
            Center(
              child: Text(
                'Order Cancelled',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
            ),

          const SizedBox(height: 24),

          // Current Status Text
          Center(
            child: Text(
              orderDetails['order_status'] ?? 'Unknown',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: status == 'cancelled'
                    ? Colors.red
                    : currentStep == orderSteps.length - 1
                        ? Colors.green
                        : Colors.orange,
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Button: Show if status is "Out For Delivery"
          if (status == 'out for delivery')
            Center(
              child: ElevatedButton(
                onPressed: deliveryStatus == 'completed'
                    ? () {
                         markOrderCompleted(context, orderDetails['order_id'].toString());
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Delivery confirmed!')),
                        );
                      }
                    : null, // Disabled if not completed
                style: ElevatedButton.styleFrom(
                  backgroundColor: deliveryStatus == 'completed' ? Colors.green : Colors.grey,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                ),
                child: Text(
                  deliveryStatus == 'completed'
                      ? 'Confirm Delivery'
                      : 'Waiting for Completion',
                  style: const TextStyle(fontSize: 16),
                ),
              ),
            ),
        ],
      ),
    );
  }

  // Info chip widget for attributes like quantity, color, size
  Widget _infoChip(String label, String value) {
    return Chip(
      label: Text('$label: $value'),
      backgroundColor: Colors.blue.shade50,
      labelStyle: const TextStyle(color: Color(0xFF133056)),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    );
  }

  // Horizontal stepper widget showing progress
  Widget _buildOrderProgress(int currentStep) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: List.generate(orderSteps.length, (index) {
        final isActive = index == currentStep;
        final isCompleted = index < currentStep;

        return Flexible(
          fit: FlexFit.tight,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircleAvatar(
                radius: 14,
                backgroundColor: isCompleted || isActive ? Colors.green : Colors.grey[300],
                child: isCompleted
                    ? const Icon(Icons.check, color: Colors.white)
                    : Text(
                        '${index + 1}',
                        style: TextStyle(
                          color: isActive ? Colors.white : Colors.grey[700],
                          fontWeight: FontWeight.bold,
                          fontSize: 12.0,
                        ),
                      ),
              ),
              const SizedBox(height: 8),
              Text(
                orderSteps[index],
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                  color: isActive ? Colors.green[700] : Colors.grey[600],
                ),
              ),
              if (index != orderSteps.length - 1)
                Container(
                  margin: const EdgeInsets.symmetric(vertical: 12),
                  height: 4,
                  color: index < currentStep ? Colors.green : Colors.grey[300],
                  width: 40,
                ),
            ],
          ),
        );
      }),
    );
  }
}
