import 'package:flutter/material.dart';

class CartTotal extends StatelessWidget {
  const CartTotal({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Checkbox(value: true, onChanged: (value) {}),
            const Text('TOTAL PAYMENT: ₱499.00'),
          ],
        ),
        Center(
          child: ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
            child: const Text(
              'Place Order',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ),
      ],
    );
  }
}
