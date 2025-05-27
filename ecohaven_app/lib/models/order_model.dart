class Order {
  final String orderId;
  final DateTime orderDate;
  final String status;
  final List<OrderItem> items;

  Order({
    required this.orderId,
    required this.orderDate,
    required this.status,
    required this.items,
  });
}

class OrderItem {
  final Product product;
  final int quantity;
  final double totalPrice;

  OrderItem({
    required this.product,
    required this.quantity,
    required this.totalPrice,
  });
}

class Product {
  final String id;
  final String name;
  final String imageUrl;
  final double price;
 

  Product({
    required this.id,
    required this.name,
    required this.imageUrl,
    required this.price,
    
  });
}
