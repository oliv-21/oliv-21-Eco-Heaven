import 'package:flutter/material.dart';
import '../models/product_model.dart';
import '../widgets/product_card.dart';
import 'product_details_page.dart';

class SearchResultsPage extends StatelessWidget {
  final String query;
  final List<Product> products;
  final int buyerId;

  const SearchResultsPage({
    super.key,
    required this.query,
    required this.products,
    required this.buyerId,
  });

  @override
  Widget build(BuildContext context) {
    final filtered = products.where((product) =>
      product.name.toLowerCase().contains(query.toLowerCase())
    ).toList();

    return Scaffold(
      appBar: AppBar(
        title: Text('Search Results'),
      ),
      body: filtered.isEmpty
          ? const Center(child: Text('No products found'))
          : GridView.builder(
              padding: const EdgeInsets.all(8),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.7,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
              ),
              itemCount: filtered.length,
              itemBuilder: (context, index) {
                final product = filtered[index];
                return GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ProductDetailsPage(
                          product: product,
                          productData: [],
                          buyer_id: buyerId,
                          shop_logo: product.shop_logo,
                        ),
                      ),
                    );
                  },
                  child: ProductCard(product: product),
                );
              },
            ),
    );
  }
}
