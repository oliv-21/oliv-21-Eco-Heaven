import 'dart:convert';
import 'package:ecohaven_app/pages/ChatHistoryPage.dart';
import 'package:ecohaven_app/pages/SearchResultsPage.dart';
import 'package:ecohaven_app/pages/cart_page.dart';
import 'package:ecohaven_app/pages/notification_page.dart';
import 'package:ecohaven_app/pages/order_history.dart';
import 'package:ecohaven_app/pages/profile_page.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../widgets/category_card.dart';
import '../widgets/product_card.dart';
import '../widgets/banner_widget.dart';
import '../models/product_model.dart';
import 'product_details_page.dart';
import 'package:ecohaven_app/configport.dart';

class HomePage extends StatefulWidget {
  final int buyer_id;

  const HomePage({super.key, required this.buyer_id});

  static const Color primaryColor = Color(0xFFADC8EE);
  static const Color accentColor = Color(0xFF133056);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;
  List<Product> products = [];
  List<Product> filteredProducts = [];
  String selectedCategory = '';
  int cartItemCount = 0;
  final TextEditingController _searchController = TextEditingController();

  Future<void> fetchProducts() async {
    final response = await http.get(Uri.parse('${Config.baseUrl}/api/products'));

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['products'];
      setState(() {
        products = Product.getAllProducts(List<Map<String, dynamic>>.from(data));
        filteredProducts = products;
      });
    } else {
      throw Exception('Failed to load products');
    }
  }

  @override
  void initState() {
    super.initState();
    fetchProducts();
     fetchCartItemCount();
    // _searchController.addListener(_filterProducts); //para gumalaw yung product display
  }
  Future<void> fetchCartItemCount() async {
  try {
    final response = await http.get(
      Uri.parse('${Config.baseUrl}/api/products_cart?buyer_id=${widget.buyer_id}'),
    );
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['status'] == 'success') {
        // cart_items is a map of shop_name -> list of items
        final cartItemsGrouped = data['cart_items'] as Map<String, dynamic>;
        int count = 0;
        cartItemsGrouped.forEach((shop, items) {
          count += (items as List).length;
        });
        setState(() {
          cartItemCount = count;
        });
      }
    }
  } catch (e) {
    // Optionally handle error
  }
}


  void _filterProducts() {
    final query = _searchController.text.trim().toLowerCase();

    setState(() {
      if (query.isEmpty && selectedCategory.isEmpty) {
        filteredProducts = products;
      } else {
        filteredProducts = products.where((product) {
          bool categoryMatch = selectedCategory.isEmpty ||
              product.category.toLowerCase() == selectedCategory.toLowerCase();
          bool searchMatch = query.isEmpty ||
              product.name.toLowerCase().contains(query);
          return categoryMatch && searchMatch;
        }).toList();
      }
    });
  }


  void filterByCategory(String category) {
    setState(() {
      selectedCategory = category;
    });
    _filterProducts();
  }

  void showAllProducts() {
    setState(() {
      selectedCategory = '';
       _searchController.clear(); 
    });
     _filterProducts();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onItemTapped(int index) {
    if (index != _selectedIndex) {
      switch (index) {
        case 0:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => HomePage(buyer_id: widget.buyer_id)),
          );
          break;
        case 1:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => NotificationPage(buyer_id: widget.buyer_id)),
          );
          break;
        case 2:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => OrderHistoryPage(buyer_id: widget.buyer_id)),
          );
          break;
        case 3:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => ProfilePage(buyer_id: widget.buyer_id)),
          );
          break;
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: HomePage.primaryColor,
        title: Row(
          children: [
            Expanded(
  child: Container(
    height: 40,
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
    ),
    child: TextField(
      controller: _searchController,
      decoration: InputDecoration(
        hintText: 'Search for products...',
        prefixIcon: const Icon(Icons.search, color: HomePage.accentColor),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(20.0)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20.0),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20.0),
          borderSide: BorderSide.none,
        ),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(vertical: 10.0),
      ),
      style: const TextStyle(fontSize: 14),
      onSubmitted: (value) {
        if (value.trim().isNotEmpty) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SearchResultsPage(
                query: value.trim(),
                products: products, // full product list
                buyerId: widget.buyer_id,
              ),
            ),
          );
        }
      },
    ),
  ),
),

            const SizedBox(width: 10),
           Stack(
  children: [
    IconButton(
      icon: const Icon(Icons.shopping_cart, color: HomePage.accentColor),
      onPressed: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => CartPage(buyer_id: widget.buyer_id),
          ),
        );
      },
    ),
    if (cartItemCount > 0)
      Positioned(
        right: 5,
        top: 5,
        child: Container(
          padding: const EdgeInsets.all(2),
          decoration: BoxDecoration(
            color: Colors.red,
            borderRadius: BorderRadius.circular(10),
          ),
          constraints: const BoxConstraints(
            minWidth: 16,
            minHeight: 16,
          ),
          child: Text(
            cartItemCount > 99 ? '99+' : '$cartItemCount',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 10,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
  ],
),

            IconButton(
              icon: const Icon(Icons.message, color: HomePage.accentColor),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ChatHistoryPage(buyerId: widget.buyer_id),
                  ),
                );
              },
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const BannerWidget(),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('CATEGORIES', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8.0),
                  SizedBox(
                    height: 120,
                    child: Container(
                      decoration: BoxDecoration(
                       color: const Color.fromARGB(255, 220, 220, 224),
                          borderRadius: BorderRadius.circular(5),
                          border: Border.all(
                            color: const Color.fromARGB(255, 10, 35, 143), // Set your desired border color here
                            width: 10,           // Set the border width here
                          ),
                      ),
                      child: ListView(
                        scrollDirection: Axis.horizontal,
                        children: [
                          CategoryCard(
                            title: 'Gardening Tools',
                            imagePath: 'assets/categoryAssets/gardening.png',
                            onTap: () => filterByCategory('Gardening Tools'),
                            isSelected: selectedCategory == 'Gardening Tools',
                          ),
                          CategoryCard(
                            title: 'Outdoor Living',
                            imagePath: 'assets/categoryAssets/outdoor.png',
                            onTap: () => filterByCategory('Outdoor Living'),
                            isSelected: selectedCategory == 'Outdoor Living',
                          ),
                          CategoryCard(
                            title: 'Home Tools',
                            imagePath: 'assets/categoryAssets/hometool.png',
                            onTap: () => filterByCategory('Home Tools'),
                            isSelected: selectedCategory == 'Home Tools',
                          ),
                          CategoryCard(
                            title: 'Kitchen Appliances',
                            imagePath: 'assets/categoryAssets/kitchenapp.png',
                            onTap: () => filterByCategory('Kitchen Appliances'),
                            isSelected: selectedCategory == 'Kitchen Appliances',
                          ),
                          CategoryCard(
                            title: 'Furniture',
                            imagePath: 'assets/categoryAssets/furniture.png',
                            onTap: () => filterByCategory('Furniture'),
                            isSelected: selectedCategory == 'Furniture',
                          ),
                          CategoryCard(
                            title: 'Decor',
                            imagePath: 'assets/categoryAssets/decor.png',
                            onTap: () => filterByCategory('Decor'),
                            isSelected: selectedCategory == 'Decor',
                          ),
                          CategoryCard(
                            title: 'Bedding',
                            imagePath: 'assets/categoryAssets/bedding.png',
                            onTap: () => filterByCategory('Bedding'),
                            isSelected: selectedCategory == 'Bedding',
                          ),
                          CategoryCard(
                            title: 'Bath',
                            imagePath: 'assets/categoryAssets/bath.png',
                            onTap: () => filterByCategory('Bath'),
                            isSelected: selectedCategory == 'Bath',
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 15.0),
                  const Text('PRODUCTS',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: HomePage.accentColor)),
                  const SizedBox(height: 8.0),
                  filteredProducts.isEmpty
                      ? const Center(child: Text('No products found'))
                      : GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            childAspectRatio: 0.7,
                            crossAxisSpacing: 8,
                            mainAxisSpacing: 8,
                          ),
                          itemCount: filteredProducts.length,
                          itemBuilder: (context, index) {
                            final product = filteredProducts[index];
                            return GestureDetector(
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => ProductDetailsPage(
                                      product: product,
                                      productData: [],
                                      buyer_id: widget.buyer_id,
                                      shop_logo: product.shop_logo,
                                    ),
                                  ),
                                );
                              },
                              child: ProductCard(product: product),
                            );
                          },
                        ),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: HomePage.accentColor,
        unselectedItemColor: Colors.grey[800],
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_outlined), activeIcon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.notifications_outlined), activeIcon: Icon(Icons.notifications), label: 'Notifications'),
          BottomNavigationBarItem(icon: Icon(Icons.history_outlined), activeIcon: Icon(Icons.history), label: 'Order History'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), activeIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
