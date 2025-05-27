import 'dart:convert';
import 'dart:io';
import 'package:ecohaven_app/configport.dart';
import 'package:ecohaven_app/pages/track_order_page.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;

import '../providers/order_provider.dart';
import 'package:ecohaven_app/pages/notification_page.dart';
import 'package:ecohaven_app/pages/profile_page.dart';
import 'package:ecohaven_app/pages/homepage.dart';

class OrderHistoryPage extends StatefulWidget {
  final int buyer_id;
  const OrderHistoryPage({Key? key, required this.buyer_id}) : super(key: key);

  static const Color primaryColor = Color(0xFFADC8EE);
  static const Color accentColor = Color(0xFF133056);

  @override
  State<OrderHistoryPage> createState() => _OrderHistoryPageState();
}

class _OrderHistoryPageState extends State<OrderHistoryPage> {
  int _selectedIndex = 2;
  bool _isLoading = true;
  bool _isCancelling = false;

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _showTracking(BuildContext context, int orderId, int buyerId) async {
    final url = Uri.parse('${Config.baseUrl}/track_orderMobile/$orderId?buyer_id=$buyerId');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final data = Map<String, dynamic>.from(jsonDecode(response.body));
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => TrackOrderPage(orderDetails: data),
          ),
        );
      } else if (response.statusCode == 404) {
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('No Tracking Info'),
            content: const Text('No tracking information available for this order.'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error fetching tracking info')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  Future<void> _loadOrders() async {
    final orderProvider = Provider.of<OrderProvider>(context, listen: false);
    setState(() {
      _isLoading = true;
    });
    await orderProvider.fetchOrders(widget.buyer_id.toString());
    setState(() {
      _isLoading = false;
    });
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
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => NotificationPage(buyer_id: widget.buyer_id)),
          );
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

  Widget _buildStatusIndicator(String status) {
    Color color;
    switch (status) {
      case 'Pending':
        color = Colors.orange;
        break;
      case 'Completed':
        color = Colors.green;
        break;
      case 'Cancelled':
        color = Colors.red;
        break;
      default:
        color = Colors.grey;
    }
    return CircleAvatar(
      radius: 8,
      backgroundColor: color,
    );
  }

  Future<void> _showCancelReasonDialog(String orderId) async {
    final List<String> reasons = [
      'Changed mind',
      'Found a better price',
      'Order placed by mistake',
      'Other',
    ];
    String? selectedReason;

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (BuildContext context) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
            top: 16,
            left: 16,
            right: 16,
          ),
          child: StatefulBuilder(
            builder: (BuildContext context, StateSetter setState) {
              return Wrap(
                children: [
                  const Text(
                    'Select a reason for cancellation',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  ...reasons.map((reason) {
                    return RadioListTile<String>(
                      title: Text(reason),
                      value: reason,
                      groupValue: selectedReason,
                      onChanged: (value) {
                        setState(() {
                          selectedReason = value;
                        });
                      },
                    );
                  }).toList(),
                  const SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(
                        onPressed: () {
                          Navigator.pop(context);
                        },
                        child: const Text('Cancel'),
                      ),
                      ElevatedButton(
                        onPressed: selectedReason == null
                            ? null
                            : () async {
                                Navigator.pop(context);
                                await _cancelOrder(orderId, selectedReason!);
                              },
                        child: const Text('Confirm'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                ],
              );
            },
          ),
        );
      },
    );
  }

  Future<void> _cancelOrder(String orderId, String reason) async {
    setState(() {
      _isCancelling = true;
    });

    try {
      final url = Uri.parse('${Config.baseUrl}/update_order_status_cancelled_userMobile');

      final response = await http.post(
        url,
        body: {
          'order_id': orderId,
          'reason': reason,
          'buyer_id': widget.buyer_id.toString(),
        },
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Order cancelled successfully.')),
        );
        await _loadOrders();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to cancel order. Please try again later. (${response.statusCode})')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error cancelling order: $e')),
      );
    } finally {
      setState(() {
        _isCancelling = false;
      });
    }
  }

  Future<void> _showRateDialog(String orderId, BuildContext context) async {
    final _formKey = GlobalKey<FormState>();
    double? rating;
    final TextEditingController commentController = TextEditingController();
    File? _selectedImage;

    Future<void> _pickImage() async {
      final pickedFile = await ImagePicker().pickImage(source: ImageSource.gallery);
      if (pickedFile != null) {
        setState(() {
          _selectedImage = File(pickedFile.path);
        });
      }
    }

    await showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Rate Your Order'),
          content: Form(
            key: _formKey,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DropdownButtonFormField<double>(
                    decoration: const InputDecoration(labelText: 'Rating'),
                    items: List.generate(5, (index) {
                      final value = (index + 1).toDouble();
                      return DropdownMenuItem(
                        value: value,
                        child: Text(value.toString()),
                      );
                    }),
                    onChanged: (val) {
                      setState(() {
                        rating = val;
                      });
                    },
                    validator: (val) => val == null ? 'Please select a rating' : null,
                  ),
                  TextFormField(
                    controller: commentController,
                    decoration: const InputDecoration(labelText: 'Comment'),
                    maxLines: 3,
                  ),
                  ElevatedButton(
                    onPressed: () async {
                      await _pickImage();
                    },
                    child: const Text('Pick Image'),
                  ),
                  if (_selectedImage != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text('Selected Image: ${path.basename(_selectedImage!.path)}'),
                    ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                if (_formKey.currentState!.validate()) {
                  Navigator.pop(context);
                  await _submitRating(orderId, rating!, commentController.text, _selectedImage, context);
                }
              },
              child: const Text('Submit'),
            ),
          ],
        );
      },
    );
  }

Future<void> _submitRating(
  String orderId,
  double rating,
  String description,
  File? imageFile,
  BuildContext context,
) async {
  try {
    final url = Uri.parse('${Config.baseUrl}/submit-ratingmobile');
    final request = http.MultipartRequest('POST', url);

    request.fields['order_id'] = orderId;
    request.fields['rating'] = rating.toString();
    request.fields['description'] = description;
    request.fields['buyer_id'] = widget.buyer_id.toString();

    if (imageFile != null) {
      request.files.add(await http.MultipartFile.fromPath(
        'picture',
        imageFile.path,
        filename: path.basename(imageFile.path),
      ));
    }

    final response = await request.send();
    final responseBody = await response.stream.bytesToString();

    if (!mounted) return;

    if (response.statusCode == 200) {
      print('Rating submitted successfully.');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Thank you for your rating!')),
      );
    } else {
      print('Failed to submit rating: ${response.statusCode}');
      print('Response body: $responseBody');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to submit rating. Please try again.')),
      );
    }
  } catch (e) {
    print('Error submitting rating: $e');
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error submitting rating: $e')),
    );
  }
}



  @override
  Widget build(BuildContext context) {
    final orderProvider = Provider.of<OrderProvider>(context);
    final orders = orderProvider.orders;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Orders'),
        backgroundColor: OrderHistoryPage.primaryColor,
        automaticallyImplyLeading: false,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : orders.isEmpty
              ? const Center(child: Text('No orders found.'))
              : Stack(
                  children: [
                    ListView.builder(
                      itemCount: orders.length,
                      itemBuilder: (context, index) {
                        final order = orders[index];
                        return Card(
                          margin: const EdgeInsets.all(10),
                          child: Padding(
                            padding: const EdgeInsets.all(10),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  color: OrderHistoryPage.primaryColor,
                                  padding: const EdgeInsets.all(8),
                                  child: Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          'Order Placed: ${order.orderDate.toString().substring(0, 10)}',
                                          overflow: TextOverflow.ellipsis,
                                          style: const TextStyle(
                                              fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          'Status: ${order.status}',
                                          overflow: TextOverflow.ellipsis,
                                          textAlign: TextAlign.end,
                                          style: const TextStyle(
                                              fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 8),
                                ...order.items.map(
                                  (item) => ListTile(
                                    isThreeLine: true,
                                    leading: Image.network(
                                      '${Config.baseUrl}/assets/upload/${item.product.imageUrl}',
                                      width: 60,
                                      height: 60,
                                      loadingBuilder:
                                          (context, child, loadingProgress) {
                                        if (loadingProgress == null)
                                          return child;
                                        return const CircularProgressIndicator();
                                      },
                                      errorBuilder: (context, error, stackTrace) =>
                                          const Icon(Icons.error),
                                    ),
                                    title: Text(item.product.name),
                                    subtitle: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text('Quantity: ${item.quantity}'),
                                        Text(
                                            'Price: ₱${item.product.price.toStringAsFixed(2)}'),
                                        Text(
                                            'Total: ₱${item.totalPrice.toStringAsFixed(2)}'),
                                      ],
                                    ),
                                    trailing: Column(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        _buildStatusIndicator(order.status),
                                        if (order.status == 'Pending')
                                          Padding(
                                            padding: const EdgeInsets.only(top: 4.0),
                                            child: ElevatedButton(
                                              onPressed: _isCancelling
                                                  ? null
                                                  : () => _showCancelReasonDialog(order.orderId),
                                              style: ElevatedButton.styleFrom(
                                                padding: const EdgeInsets.symmetric(
                                                    horizontal: 8, vertical: 4),
                                                minimumSize: const Size(0, 28),
                                                tapTargetSize:
                                                    MaterialTapTargetSize.shrinkWrap,
                                                textStyle:
                                                    const TextStyle(fontSize: 12),
                                              ),
                                              child: const Text('Cancel'),
                                            ),
                                          ),
                                        if (order.status == 'Completed')
                                          Padding(
                                            padding: const EdgeInsets.only(top: 4.0),
                                            child: ElevatedButton(
                                              onPressed: () => _showRateDialog(order.orderId, context),
                                              style: ElevatedButton.styleFrom(
                                                padding: const EdgeInsets.symmetric(
                                                    horizontal: 8, vertical: 4),
                                                minimumSize: const Size(0, 28),
                                                tapTargetSize:
                                                    MaterialTapTargetSize.shrinkWrap,
                                                textStyle:
                                                    const TextStyle(fontSize: 12),
                                              ),
                                              child: const Text('Rate'),
                                            ),
                                          ),
                                      ],
                                    ),
                                    onTap: () {
                                      final orderIdInt =
                                          int.tryParse(order.orderId.toString());
                                      if (orderIdInt != null) {
                                        _showTracking(context, orderIdInt, widget.buyer_id);
                                      } else {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('Invalid order ID')),
                                        );
                                      }
                                    },
                                  ),
                                ),
                                const SizedBox(height: 10),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                    if (_isCancelling)
                      Container(
                        color: Colors.black54,
                        child: const Center(
                          child: CircularProgressIndicator(),
                        ),
                      ),
                  ],
                ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: OrderHistoryPage.accentColor,
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
