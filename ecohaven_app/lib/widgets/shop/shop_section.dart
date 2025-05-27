import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '/models/cart_model.dart';
import '/providers/cart_provider.dart';
import 'package:ecohaven_app/configport.dart';

class ShopSection extends StatelessWidget {
  final String shopName;
  final List<CartModel> cartItems;
  final int buyer_id;

  const ShopSection({Key? key, required this.shopName, required this.cartItems,required this.buyer_id,})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    final cartProvider = Provider.of<CartProvider>(context);
    bool isAllSelected = cartItems.every((item) => item.isSelected);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Checkbox(
                    value: isAllSelected,
                    onChanged: (value) {
                      cartProvider.selectAll(value ?? false); // Select all items
                    },
                  ), // TODO: Make selectable
                  Text(
                    '$shopName >',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              TextButton(onPressed: () {}, child: const Text("Edit")),
            ],
          ),
        ),
        Column(
          children:
              cartItems.map((cartItem) {
                return Card(
                  margin: const EdgeInsets.symmetric(
                    vertical: 8,
                    horizontal: 16,
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      children: [
                        Checkbox(
                              value: cartItem.isSelected,
                              onChanged: (value) {
                                // Update the isSelected value for the specific item
                                Provider.of<CartProvider>(context, listen: false)
                                    .toggleItemSelection(cartItem.id, value ?? false);
                              },
                            ),


                        Image.network(
                          cartItem.product.productImage.isNotEmpty
                              ? '${Config.baseUrl}/assets/upload/${cartItem.product.productImage}'
                              : 'https://via.placeholder.com/60', // fallback
                              
                          fit: BoxFit.cover,
                          width: 60,
                          height: 60,
                        ),
                                      const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                cartItem.product.name,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '₱${cartItem.product.price.toStringAsFixed(2)}',
                                style: const TextStyle(color: Colors.orange),
                              ),
                              Row(
                                children: [
                                  IconButton(
                                    icon: const Icon(Icons.remove),
                                    onPressed: () {
                                      if (cartItem.quantity > 1) {
                                        cartProvider.updateQuantity(
                                          cartItem.product.id,
                                          cartItem.quantity - 1,
                                        );
                                      } else {
                                        cartProvider.removeFromCart(
                                          cartItem.product.id,
                                        );
                                      }
                                    },
                                  ),
                                  Text(
                                    '${cartItem.quantity}',
                                  ), // Quantity displayed
                                  IconButton(
                                    icon: const Icon(Icons.add),
                                    onPressed: () {
                                       print('Attempting to update quantity for itemId: ${cartItem.id}');
                                      cartProvider.updateQuantity(
                                        cartItem.id,
                                        cartItem.quantity + 1,
                                      );
                                      print(cartItem.product.id);
                                      print("!!!!!!!!!!!!!!!!!!!!");
                                      print(cartItem.quantity + 1);
                                    },
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.delete, color: Colors.red),
                           onPressed: () {
                            cartProvider.deleteCartItem( cartItem.id, buyer_id);
                             // Pass actual buyer_id here
                          print('buyer_id${buyer_id}');
                          print(buyer_id);
                          print(cartItem.product.id);
                          print(cartItem.id);
                          },
                          
                        ),

                      ],
                    ),
                  ),
                );
              }).toList(),
        ),
      ],
    );
  }
}
