import 'dart:convert';
import 'package:ecohaven_app/models/cart_model.dart';
import 'package:ecohaven_app/pages/shoppage.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import '../models/product_model.dart';
import 'package:ecohaven_app/providers/cart_provider.dart';
import 'package:ecohaven_app/pages/checkout_page.dart';
import 'package:ecohaven_app/configport.dart';

class ProductDetailsPage extends StatefulWidget {
  final Product product;
  final int buyer_id;
  final String shop_logo;
  final List<Map<String, dynamic>> productData;

  const ProductDetailsPage({
    Key? key,
    required this.product,
    required this.productData,
    required this.buyer_id,
    required this.shop_logo,
  }) : super(key: key);

  @override
  State<ProductDetailsPage> createState() => _ProductDetailsPageState();
}

class _ProductDetailsPageState extends State<ProductDetailsPage> {
  List<dynamic> reviews = [];
  bool isLoadingReviews = true;

  @override
  void initState() {
    super.initState();
    fetchReviews();
  }

  Future<void> fetchReviews() async {
    final url = Uri.parse('${Config.baseUrl}/product-reviews/${widget.product.id}');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        setState(() {
          reviews = json.decode(response.body);
          isLoadingReviews = false;
        });
      } else {
        setState(() {
          isLoadingReviews = false;
        });
      }
    } catch (e) {
      setState(() {
        isLoadingReviews = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final allProducts = Product.getAllProducts(widget.productData);
    allProducts.where((p) => p.shopName == widget.product.shopName).toList();

    return Scaffold(
      appBar: AppBar(),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product Image
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(5.0),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(5.0),
                child: Image.network(
                  '${Config.baseUrl}/assets/upload/${widget.product.productImage}',
                  height: 250,
                  fit: BoxFit.contain,
                  errorBuilder: (context, error, stackTrace) =>
                      const Icon(Icons.broken_image, size: 100),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Product Name
            Text(
              widget.product.name,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),

            // Price
            Text(
              '₱${widget.product.price.toStringAsFixed(2)}',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Color(0xFF133056),
              ),
            ),
            const SizedBox(height: 16),

            // Sold Count
            Row(
              children: [
                const Icon(Icons.shopping_bag, color: Colors.green, size: 20),
                const SizedBox(width: 8),
                Text(
                  '${widget.product.sold} Sold',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                    color: Colors.black87,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Rating Summary
            Row(
              children: [
                Icon(Icons.star, color: Colors.yellow[700], size: 20),
                const SizedBox(width: 8),
                Text(
                  widget.product.rating.toString(),
                  style: const TextStyle(fontSize: 16, color: Colors.grey),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Shop Info
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey, width: 1),
                borderRadius: BorderRadius.circular(2),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 75,
                        height: 75,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          image: DecorationImage(
                            image: NetworkImage(
                                '${Config.baseUrl}/assets/upload/${widget.shop_logo}'),
                            fit: BoxFit.contain,
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        widget.product.shopName,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ShopPage(
                            shopimagePath: widget.product.shopimagePath,
                            shop_logo: widget.shop_logo,
                            shopName: widget.product.shopName,
                            buyer_id: widget.buyer_id,
                          ),
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF133056),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    child: const Text(
                      'Visit',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20.0),

            // Description
            const Text(
              'Description',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Color(0xFF133056),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              widget.product.description,
              style: const TextStyle(fontSize: 16, color: Colors.black54),
            ),
            const SizedBox(height: 24),

            // Ratings & Reviews Header
            const Text(
              'Ratings & Reviews',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Color(0xFF133056),
              ),
            ),
            const SizedBox(height: 8),

            // Reviews List
            if (isLoadingReviews)
              const Center(child: CircularProgressIndicator())
            else if (reviews.isEmpty)
              const Text('No reviews yet.')
            else
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: reviews.length,
                separatorBuilder: (_, __) => const Divider(),
                itemBuilder: (context, index) {
                  final review = reviews[index];
                  final fullname = review['Fullname'] ?? 'Anonymous';
                  final rate = review['rate'] ?? 0;
                  final description = review['description'] ?? '';
                  final productPic = review['product_pic'];

                  return ListTile(
                    leading: productPic != null && productPic.isNotEmpty
                        ? Image.network(
                            '${Config.baseUrl}/assets/upload/$productPic',
                            width: 50,
                            height: 50,
                            fit: BoxFit.cover,
                          )
                        : const Icon(Icons.image_not_supported),
                    title: Text(fullname),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: List.generate(
                            5,
                            (starIndex) => Icon(
                              starIndex < rate ? Icons.star : Icons.star_border,
                              color: Colors.amber,
                              size: 16,
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(description),
                      ],
                    ),
                  );
                },
              ),

            const SizedBox(height: 24),
          ],
        ),
      ),

      // Bottom Checkout Bar (your existing buttons)
      bottomNavigationBar: BottomAppBar(
        color: Colors.white,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: ElevatedButton(
                  onPressed: () async {
                    final response = await http.post(
                      Uri.parse('${Config.baseUrl}/buyer_dashboard/add_to_cart/mobile'),
                      body: {
                        'product_id': widget.product.id.toString(),
                        'quantity': '1',
                        'buyer_id': widget.buyer_id.toString(),
                        'description': widget.product.description,
                        'productName': widget.product.name,
                        'shop_name': widget.product.shopName,
                        'price': widget.product.price.toString(),
                        'product_image': widget.product.productImage,
                        'buying': '0',
                      },
                    );

                    if (response.statusCode == 200) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('${widget.product.name} added to cart!'),
                          duration: const Duration(seconds: 2),
                        ),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Failed to add to cart'),
                          duration: Duration(seconds: 2),
                        ),
                      );
                    }
                    final cartProvider = Provider.of<CartProvider>(
                      context,
                      listen: false,
                    );
                    cartProvider.addToCart(
                      CartModel(id: widget.product.id, product: widget.product, quantity: 1),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFADC8EE),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  child: const Padding(
                    padding: EdgeInsets.symmetric(vertical: 7),
                    child: Text(
                      'Add to Cart',
                      style: TextStyle(fontSize: 16, color: Colors.white),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => CheckoutPage(
                          buyer_id: widget.buyer_id,
                          buying: 1,
                          selectedItems: [
                            CartModel(
                              id: widget.product.id,
                              product: widget.product,
                              quantity: 1,
                              isSelected: true,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF133056),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  child: const Padding(
                    padding: EdgeInsets.symmetric(vertical: 7),
                    child: Text(
                      'Buy Now',
                      style: TextStyle(fontSize: 16, color: Colors.white),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
