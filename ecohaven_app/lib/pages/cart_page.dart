
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ecohaven_app/pages/checkout_page.dart';
import '/models/cart_model.dart';
import '/providers/cart_provider.dart';
import '/widgets/shop/shop_section.dart';
import 'package:http/http.dart' as http;
import 'package:ecohaven_app/configport.dart';

class CartPage extends StatefulWidget {
  final int buyer_id;
  const CartPage({Key? key, required this.buyer_id}) : super(key: key);

  @override
  CartPageState createState() => CartPageState();
}

class CartPageState extends State<CartPage> {
  static const Color primaryColor = Color(0xFFADC8EE);
  static const Color accentColor = Color(0xFF133056);

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      final cartProvider = Provider.of<CartProvider>(context, listen: false);
    cartProvider.fetchCartItems(widget.buyer_id.toString());
    });
  }

  Map<String, List<CartModel>> _groupCartItemsByShop(List<CartModel> items) {
  final groupedItems = <String, List<CartModel>>{};

  for (var item in items) {
    if (!groupedItems.containsKey(item.shopName)) {
      groupedItems[item.shopName] = [];
    }
    groupedItems[item.shopName]!.add(item);

    print("Grouped under shop: ${item.shopName}");
    for (var i in groupedItems[item.shopName]!) {
      print(" - Product: ${i.product.name}, Qty: ${i.quantity}");
    }
  }

  return groupedItems;
}


  @override
  Widget build(BuildContext context) {
    final cartProvider = Provider.of<CartProvider>(context);
    final cartItems = cartProvider.cartItems;
    final groupedCartItems = _groupCartItemsByShop(cartItems);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Shopping Cart (${cartItems.length})',
          style: const TextStyle(color: Colors.black),
        ),
        backgroundColor: primaryColor,
        foregroundColor: Colors.black,
        elevation: 0,
        actions: [
          TextButton(
                onPressed: () async {
                  final response = await http.post(
                    Uri.parse('${Config.baseUrl}/delete_cart_allitem_mobile'),
                    body: {'buyer_id': widget.buyer_id.toString()},
                  );

                  if (response.statusCode == 200) {
                    final cartProvider = Provider.of<CartProvider>(context, listen: false);
                    cartProvider.clearCart();  // clear local state
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Cart cleared successfully')),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Failed to clear cart')),
                    );
                  }
                },
                child: const Text('Clear', style: TextStyle(color: Colors.black)),
              ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: groupedCartItems.isEmpty
                ? const Center(child: Text("Your cart is empty"))
                : ListView.builder(
                    itemCount: groupedCartItems.length,
                    itemBuilder: (context, index) {
                      final shopName = groupedCartItems.keys.elementAt(index);
                      final items = groupedCartItems[shopName]!;
                      return ShopSection(
                        shopName: shopName,
                        cartItems: items,
                        buyer_id: widget.buyer_id,
                      );
                    },
                  ),
          ),
          _buildBottomBar(cartProvider),
        ],
      ),
    );
  }

  Widget _buildBottomBar(CartProvider cartProvider) {
    double total = cartProvider.totalPrice;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: Colors.grey[300]!)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Checkbox(value: true, onChanged: (value) {}),
              const Text('All'),
            ],
          ),
          Row(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  const Text('Total'),
                  Text(
                    '₱${total.toStringAsFixed(2)}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(width: 16),
             ElevatedButton(
                  onPressed: cartProvider.cartItems.where((item) => item.isSelected).isEmpty
                      ? null
                      : () {
                          // Filter the selected items from the cart
                          final selectedItems = cartProvider.cartItems
                              .where((item) => item.isSelected)
                              .toList();

                          // Navigate to the CheckoutPage and pass selected items
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => CheckoutPage(
                                buyer_id: widget.buyer_id,
                                selectedItems: selectedItems,
                                buying: 0, // Pass only selected items
                              ),
                            ),
                          );
                        },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: accentColor,
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Check Out (${cartProvider.cartItems.where((item) => item.isSelected).length})', // Count only selected items
                    style: const TextStyle(color: Colors.white),
                  ),
                ),

            ],
          ),
        ],
      ),
    );
  }
}

