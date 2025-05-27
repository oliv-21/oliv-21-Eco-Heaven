import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/cart_model.dart';
import '../models/product_model.dart';
import 'package:ecohaven_app/configport.dart';
class CartProvider with ChangeNotifier {
  final List<CartModel> _cartItems = [];

  List<CartModel> get cartItems => _cartItems;

  double get totalPrice {
    double total = 0.0;
    for (var item in _cartItems) {
      if (item.isSelected) { // Only add selected items to the total
        total += item.product.price * item.quantity;
      }
    }
    return total;
  }

  void addToCart(CartModel newItem) {
    for (var item in _cartItems) {
      if (_isSameProduct(item, newItem)) {
        item.quantity += newItem.quantity;
        notifyListeners();
        return;
      }
    }
    _cartItems.add(newItem);
    notifyListeners();
  }

  bool _isSameProduct(CartModel a, CartModel b) {
    return a.product.id == b.product.id &&
           a.product.color == b.product.color &&
           a.product.size == b.product.size;
  }

  void removeFromCart(int productId) {
    _cartItems.removeWhere((item) => item.product.id == productId);
    notifyListeners();
  }

  Future<void> updateQuantity(int itemId, int newQuantity) async {
    final item = _cartItems.firstWhere((item) => item.id == itemId);
    item.quantity = newQuantity;
    print('this is from provider ${item}');
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('${Config.baseUrl}/update_cart_quantity_mobile'),
        body: {
          'item_id': itemId.toString(),
          'quantity': newQuantity.toString(),
        },
      );

      if (response.statusCode != 200) {
        print('Error updating cart: ${json.decode(response.body)['message']}');
      }
    } catch (e) {
      print('Exception: $e');
    }
  }

  void clearCart() {
    _cartItems.clear();
    notifyListeners();
  }

  Future<void> fetchCartItems(String buyerId) async {
  final url = '${Config.baseUrl}/api/products_cart?buyer_id=$buyerId';

  try {
    print(buyerId);
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);

      if (data['status'] == 'success') {
        print(data);
        final List<CartModel> loadedCartItems = [];
        Map<String, dynamic> groupedCartItems = data['cart_items'];

        groupedCartItems.forEach((shopName, items) {
          for (var item in items) {
            // Optional: print each item for debugging
            print('Cart item: $item');

            final product = Product(
              id: item['product_id']?? '',
              shopName: shopName,
              name: item['product_name'] ?? '',
              description: item['Description'] ?? 'No description available',
              price: double.tryParse(item['price']?.toString() ?? '') ?? 0,
              sold: '0',
              rating: '0.0',
              imagePath: item['image'] ?? '',
              shopimagePath: '',
              productImage: item['image'] ?? '',
              shop_logo: item['shop_logo'] ?? '',
              category: item['category'] ?? 'unknown',
            );

            loadedCartItems.add(CartModel(
              id: item['cart_id'] ?? '',
              product: product,
              quantity: item['quantity'] ?? 1,
            ));
          }
        });

        _cartItems.clear();
        _cartItems.addAll(loadedCartItems);
        notifyListeners();
      }
    }
  } catch (error) {
    print(buyerId);
    print('Error fetching cart items: $error');
  }
}

  void toggleItemSelection(int cartItemId, bool isSelected) {
  final index = _cartItems.indexWhere((item) => item.id == cartItemId);
  if (index != -1) {
    _cartItems[index].isSelected = isSelected;
    notifyListeners(); // Notify listeners after updating the state
  } else {
    print('Item with ID $cartItemId not found in the cart.');
  }
  }


  void selectAll(bool isSelected) {
  for (var item in _cartItems) {
    item.isSelected = isSelected;
  }
  notifyListeners(); // Notify listeners after selecting/deselecting all items
  }

  Future<void> deleteCartItem(int cartId, int buyerId) async {
  final url = Uri.parse('${Config.baseUrl}/delete_cart_item_mobile');
  print('ito ay galing sa provider${cartId}');
  try {
    final response = await http.post(
      url,
      body: {
        'item_id': cartId.toString(),
        'buyer_id': buyerId.toString(), // optional
      },
    );

    final responseData = json.decode(response.body);
    if (response.statusCode == 200 && responseData['status'] == 'success') {
      _cartItems.removeWhere((item) => item.id == cartId);
      notifyListeners();
    } else {
      print('Error deleting item: ${responseData['message']}');
    }
  } catch (e) {
    print('Exception deleting item: $e');
  }
}

 
}
