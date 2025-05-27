import 'package:ecohaven_app/models/product_model.dart';

class CartModel {
  final int id;
  final Product product;
  int quantity;
  bool isSelected;

  CartModel({ required this.id,required this.product, required this.quantity ,this.isSelected = false, });

  String get shopName => product.shopName;
  
}
