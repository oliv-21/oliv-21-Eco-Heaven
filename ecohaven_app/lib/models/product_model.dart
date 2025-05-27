class Product {
  final int id;
  final String shopName;
  final String name;
  final String description;
  final double price;
  final String sold;
  final String rating;
  final String imagePath;
  final String shopimagePath;
  final String productImage;
  final String shop_logo;
  final String category;

  Product({
    required this.id,
    required this.shopName,
    required this.name,
    required this.description,
    required this.price,
    required this.sold,
    required this.rating,
    required this.imagePath,
    required this.shopimagePath, 
    required this. productImage,
    required this. shop_logo,
    required this.category
  });

  get color => null;

  get size => null;

  static List<Product> getAllProducts(List<Map<String, dynamic>> data) {
    List<Product> products = [];

    for (var item in data) {
      products.add(
        Product(
          id: item['id'] ?? 0,
          shopName: item['shop_name'] ?? 'Error Shop',
          name: item['Product_Name'] ?? 'Unnamed Product',
          description: item['Description'] ?? 'No description available',
          price: double.tryParse(item['Price'].toString()) ?? 0,
          sold: (item['sold'] ?? 0.0).toString(),
          rating: (item['rating'] ?? 0.0).toString(),
          imagePath: 'assets/uploads/${item['Image']}',
          shopimagePath: 'assets/uploads/${item['shop_logo']}',
          productImage: '${item['Image']}',
          shop_logo:'${item['shop_logo']}',
          category: '${item['category']}',


        ),
      );
    }
    return products;
  }

  factory Product.fromJson(Map<String, dynamic> item, String shopName, String shopimagePath) {
    return Product(
      id: item['Id'] ?? 0,
      shopName: shopName,
      name: item['Product_Name'] ?? 'Unnamed Product',
      description: item['description'] ?? 'No description available',
      price: double.tryParse(item['price'].toString()) ?? 0,
      sold: (item['total_sold'] ?? 0).toString(),
      rating: (item['average_rate'] ?? 0.0).toString(),
      imagePath: 'assets/uploads/${item['image'] ?? ''}',
      shopimagePath: shopimagePath,
      productImage: item['image'] ?? '',
      shop_logo: item['shop_logo'] ?? '',
      category: '${item['category']}',
    );
  }
}
