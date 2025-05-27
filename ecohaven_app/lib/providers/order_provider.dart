import 'dart:convert';
import 'package:flutter/material.dart';
import '../models/order_model.dart';
import 'package:http/http.dart' as http;
import 'package:ecohaven_app/configport.dart';

class OrderProvider with ChangeNotifier {
  List<Order> _orders = [];
  final String _baseUrl = '${Config.baseUrl}/user-ordersmoble';

  List<Order> get orders => _orders; // ✅ Add this getter

  Future<void> fetchOrders(String buyerId) async {
  try {
    final response = await http.post(
      Uri.parse(_baseUrl),
      body: {'buyer_id': buyerId},
    );

    if (response.statusCode == 200) {
      final responseData = json.decode(response.body);

      if (responseData['status'] == 'success') {
        final ordersData = responseData['orders'] as List;
        final orders = <Order>[];

        // Directly map the order data into OrderItem and Order objects
        for (var orderData in ordersData) {
          final items = <OrderItem>[
            OrderItem(
              product: Product(
                id: orderData['order_id'].toString(),
                name: orderData['product_name'],
                imageUrl: orderData['product_image'],
                price: double.parse(orderData['Price']),
              ),
              quantity: orderData['quantity'],
              totalPrice: double.parse(orderData['total_price']),
            )
          ];

          orders.add(Order(
            orderId: orderData['order_id'].toString(),
            orderDate: DateTime.parse(orderData['created_at']),
            status: orderData['order_status'],
            items: items,
          ));
        }

        _orders = orders;
        notifyListeners();
      } else {
        print('Failed to fetch orders: ${responseData['message']}');
      }
    } else {
      print('Failed to load data: ${response.statusCode}');
    }
  } catch (error) {
    print('Error fetching orders: $error');
  }
}


}
