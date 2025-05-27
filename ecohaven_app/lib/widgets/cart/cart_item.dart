import 'package:flutter/material.dart';
import '/models/cart_model.dart';
import 'package:ecohaven_app/configport.dart';

class CartItemWidget extends StatelessWidget {
  final CartModel cartItem;
  final VoidCallback onRemove;
  final VoidCallback onIncrease;
  final VoidCallback onDecrease;

  const CartItemWidget({
    Key? key,
    required this.cartItem,
    required this.onRemove,
    required this.onIncrease,
    required this.onDecrease,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            
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
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '₱${cartItem.product.price.toStringAsFixed(2)}',
                    style: const TextStyle(color: Colors.orange),
                  ),
                  Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.remove),
                        onPressed: onDecrease,
                      ),
                      Text('${cartItem.quantity}'),
                      IconButton(
                        icon: const Icon(Icons.add),
                        onPressed: onIncrease,
                      ),
                    ],
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: onRemove,
            ),
          ],
        ),
      ),
    );
  }
}
