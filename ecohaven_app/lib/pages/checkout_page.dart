import 'package:ecohaven_app/pages/homepage.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '/providers/cart_provider.dart';
import 'package:ecohaven_app/models/cart_model.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:ecohaven_app/configport.dart';

class CheckoutPage extends StatefulWidget {
  final int buyer_id;
  final int buying;
  final List<CartModel> selectedItems;

  const CheckoutPage({
    Key? key,
    required this.buyer_id,
    required this.selectedItems,
    required this.buying,
  }) : super(key: key);

  static const Color primaryColor = Color(0xFFADC8EE);
  static const Color accentColor = Color(0xFF133056);

  @override
  State<CheckoutPage> createState() => _CheckoutPageState();
}

class _CheckoutPageState extends State<CheckoutPage> {
  Map<String, dynamic>? _address;
  bool _isLoadingAddress = true;
  String? _addressError;

  @override
  void initState() {
    super.initState();
    _fetchBuyerAddress();
  }

  Future<void> _fetchBuyerAddress() async {
    setState(() {
      _isLoadingAddress = true;
      _addressError = null;
    });
    try {
      final response = await http.post(
        Uri.parse('${Config.baseUrl}/get-buyer-address'),
        body: {'buyer_id': widget.buyer_id.toString()},
      );
      if (response.statusCode == 200) {
        setState(() {
          _address = Map<String, dynamic>.from(json.decode(response.body));
          _isLoadingAddress = false;
        });
      } else {
        setState(() {
          _address = null;
          _isLoadingAddress = false;
          _addressError = 'No address found for this buyer.';
        });
      }
    } catch (e) {
      setState(() {
        _address = null;
        _isLoadingAddress = false;
        _addressError = 'Failed to load address.';
      });
    }
  }

  Future<void> placeOrder(BuildContext context) async {
    print('Selected items: ${widget.selectedItems}');
    widget.selectedItems.forEach((item) {
      print('Item id: ${item.id}, Product id: ${item.product.id}, Quantity: ${item.quantity}');
    });

    final response = await http.post(
      Uri.parse('${Config.baseUrl}/checkoutPostMobile'),
      body: {
        'buyer_id': widget.buyer_id.toString(),
        'buying': widget.buying.toString(),
        'variation_id': '0',
        'cart_ids[]': widget.selectedItems.map((item) => item.id.toString()).join(','),
        'product_id': widget.selectedItems.map((item) => item.product.id.toString()).join(','),
        'quantity': widget.selectedItems.map((item) => item.quantity.toString()).join(','),
      },
    );

    if (response.statusCode == 200) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text('Your order has been placed successfully!'),
      backgroundColor: Colors.green,
      duration: Duration(seconds: 2),
    ),
  );
  // Navigate to HomePage and remove all previous routes
  Navigator.pushAndRemoveUntil(
    context,
    MaterialPageRoute(
      builder: (context) => HomePage(buyer_id: widget.buyer_id),
    ),
    (route) => false,
  );
}
 else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to place order.'),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final cartProvider = Provider.of<CartProvider>(context);
    final cartItems = cartProvider.cartItems;
    final double total = widget.selectedItems.fold(0, (sum, item) {
      return sum + (item.product.price * item.quantity);
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Checkout', style: TextStyle(color: Colors.black)),
        backgroundColor: CheckoutPage.primaryColor,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: widget.selectedItems.isEmpty
          ? const Center(
              child: Text(
                'Your cart is empty!',
                style: TextStyle(fontSize: 18),
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionTitle('Shipping Address'),
                  _buildAddressCard(context),
                  const SizedBox(height: 16),
                  _buildSectionTitle('Items'),
                  const SizedBox(height: 8),
                  ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: widget.selectedItems.length,
                    itemBuilder: (context, index) {
                      final item = widget.selectedItems[index];
                      return _buildItemCard(item);
                    },
                  ),
                  const SizedBox(height: 16),
                  _buildSectionTitle('Courier'),
                  _buildCourierCard(),
                  const SizedBox(height: 16),
                  _buildSectionTitle('Payment Method'),
                  _buildPaymentCard(context),
                  const SizedBox(height: 16),
                ],
              ),
            ),
      bottomNavigationBar: _buildBottomBar(context, cartItems, total),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
    );
  }

  Widget _buildAddressCard(BuildContext context) {
    if (_isLoadingAddress) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_addressError != null) {
      return Card(
        margin: const EdgeInsets.symmetric(vertical: 8),
        child: ListTile(
          leading: const Icon(Icons.location_on, color: CheckoutPage.accentColor),
          title: const Text('No Address'),
          subtitle: Text(_addressError!),
          trailing: TextButton(
            onPressed: () {
              // TODO: Navigate to address add/edit page
            },
            child: const Text(''),
          ),
        ),
      );
    }
    if (_address == null) {
      return const SizedBox();
    }

    final fullName =
        '${_address!['Fname'] ?? ''} ${_address!['Lname'] ?? ''}'.trim();
    final addressStr =
        '${_address!['houseNo'] ?? ''} ${_address!['street'] ?? ''}, '
        '${_address!['barangay'] ?? ''}, ${_address!['city'] ?? ''}, '
        '${_address!['Province'] ?? ''} ${_address!['postal_code'] ?? ''}';

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: ListTile(
        leading: const Icon(Icons.location_on, color: CheckoutPage.accentColor),
        title: Text(fullName.isNotEmpty ? fullName : 'No Name'),
        subtitle: Text(addressStr),
        
      ),
    );
  }

  Widget _buildItemCard(CartModel cartItem) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        leading: Image.network(
          cartItem.product.productImage.isNotEmpty
              ? '${Config.baseUrl}/assets/upload/${cartItem.product.productImage}'
              : 'https://via.placeholder.com/60',
          fit: BoxFit.cover,
          width: 60,
          height: 60,
        ),
        title: Text(cartItem.product.name),
        subtitle: Text('Quantity: ${cartItem.quantity}'),
        trailing: Text(
          '₱${(cartItem.product.price * cartItem.quantity).toStringAsFixed(2)}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  Widget _buildCourierCard() {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: const ListTile(
        leading: Icon(Icons.local_shipping, color: CheckoutPage.accentColor),
        title: Text('Standard Delivery'),
        subtitle: Text('3-5 business days'),
      ),
    );
  }

  Widget _buildPaymentCard(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: ListTile(
        leading: const Icon(Icons.payment, color: CheckoutPage.accentColor),
        title: const Text('Cash on Delivery'),
        trailing: TextButton(
          onPressed: () {
            // TODO: Navigate to payment method selection page
          },
          child: const Text('Change'),
        ),
      ),
    );
  }

  Widget _buildBottomBar(BuildContext context, List cartItems, double total) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: const BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 8,
            offset: Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                RichText(
                  text: TextSpan(
                    style: const TextStyle(fontSize: 16, color: Colors.black),
                    children: [
                      const TextSpan(text: 'Total: '),
                      TextSpan(
                        text: '₱${total.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: CheckoutPage.accentColor,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          SizedBox(
            height: 48,
            child: ElevatedButton(
              onPressed: () async {  // Always enabled
                await placeOrder(context);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: CheckoutPage.accentColor,
              ),
              child: const Text('Place Order', style: TextStyle(fontSize: 16, color: Colors.white)),
            ),
          ),
        ],
      ),
    );
  }
}
