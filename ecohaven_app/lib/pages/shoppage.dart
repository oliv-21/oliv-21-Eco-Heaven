import 'dart:convert';
import 'dart:io';
import 'package:ecohaven_app/pages/chat_page.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;

import 'product_details_page.dart';
import '../models/product_model.dart';
import '../widgets/product_card.dart';
import 'package:ecohaven_app/configport.dart';

class ShopPage extends StatefulWidget {
  final int buyer_id;
  final String shopName;
  final String shopimagePath;
  final String shop_logo;

  static const Color primaryColor = Color(0xFFADC8EE);
  static const Color accentColor = Color(0xFF133056);

  const ShopPage({
    Key? key,
    required this.shopName,
    required this.shopimagePath,
    required this.shop_logo,
    required this.buyer_id,
  }) : super(key: key);

  @override
  State<ShopPage> createState() => _ShopPageState();
}

class _ShopPageState extends State<ShopPage> {
  late Future<List<Product>> _productsFuture;

  @override
  void initState() {
    super.initState();
    _productsFuture = _fetchProducts();
  }

  Future<List<Product>> _fetchProducts() async {
    final response = await http.get(Uri.parse(
      '${Config.baseUrl}/buyer_dashboard/seller-profileMobile/${widget.shopName}'
    ));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final List productsJson = data['products'];
      return productsJson
          .map<Product>((item) => Product.fromJson(
                item,
                data['shop_name'] ?? 'Error Shop',
                data['shop_image'] ?? '',
              ))
          .toList();
    } else {
      throw Exception('Failed to load shop data');
    }
  }

  void _showReportDialog() {
    showDialog(
      context: context,
      builder: (dialogContext) => ReportSellerDialog(
        shopName: widget.shopName,
        buyerId: widget.buyer_id,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: ShopPage.primaryColor,
        title: Row(
          children: [
            Expanded(
              child: Container(
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: 'Search for products...',
                          prefixIcon: const Icon(
                            Icons.search,
                            color: ShopPage.accentColor,
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(2.0),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(2.0),
                            borderSide: BorderSide.none,
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(2.0),
                            borderSide: BorderSide.none,
                          ),
                          filled: true,
                          fillColor: Colors.white,
                          contentPadding: const EdgeInsets.symmetric(
                            vertical: 10.0,
                          ),
                        ),
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      backgroundColor: const Color(0xFFFCEEEF),
      body: FutureBuilder<List<Product>>(
        future: _productsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No products found.'));
          } else {
            final productsFromShop = snapshot.data!;
            return Column(
              children: [
                // SHOP HEADER SECTION
                Container(
                  color: ShopPage.primaryColor,
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      // Shop Logo
                      ClipOval(
                        child: Builder(
                          builder: (context) {
                            if (widget.shop_logo.isEmpty) {
                              return const Icon(Icons.store, size: 48, color: Colors.white);
                            }
                            final imageUrl = '${Config.baseUrl}/assets/upload/${widget.shop_logo}';
                            return Image.network(
                              imageUrl,
                              width: 90,
                              height: 90,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return const Icon(Icons.store, size: 48, color: Colors.white);
                              },
                            );
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Shop Name
                            Text(
                              widget.shopName,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                const SizedBox(width: 8),
                              ],
                            ),
                            const SizedBox(height: 8),
                            // Report and Chat Buttons
                            Row(
                              children: [
                                Expanded(
                                  child: ElevatedButton.icon(
                                    onPressed: _showReportDialog,
                                    icon: const Icon(Icons.flag, color: Colors.white),
                                    label: const Text("Report"),
                                    style: ElevatedButton.styleFrom(
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(2),
                                      ),
                                      backgroundColor: ShopPage.accentColor,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 16),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: ElevatedButton.icon(
                                    onPressed: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => ChatPage(
                                            shopName: widget.shopName,
                                            shopLogo: widget.shop_logo,
                                            buyerId: widget.buyer_id,
                                          ),
                                        ),
                                      );
                                    },
                                    icon: const Icon(Icons.message, color: Colors.white),
                                    label: const Text("Chat"),
                                    style: ElevatedButton.styleFrom(
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(2),
                                      ),
                                      backgroundColor: ShopPage.accentColor,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 16),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                // "All Products" Header
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: const Center(
                    child: Text(
                      'All Products',
                      style: TextStyle(
                        color: ShopPage.accentColor,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                // PRODUCT GRID
                Expanded(
                  child: GridView.builder(
                    padding: const EdgeInsets.all(8),
                    itemCount: productsFromShop.length,
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      childAspectRatio: 0.7,
                      crossAxisSpacing: 8,
                      mainAxisSpacing: 8,
                    ),
                    itemBuilder: (context, index) {
                      final product = productsFromShop[index];
                      return GestureDetector(
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => ProductDetailsPage(
                                product: product,
                                productData: [],
                                shop_logo: widget.shop_logo,
                                buyer_id: widget.buyer_id,
                              ),
                            ),
                          );
                        },
                        child: ProductCard(
                          product: product,
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }
}

// ================== REPORT SELLER DIALOG ======================
class ReportSellerDialog extends StatefulWidget {
  final String shopName;
  final int buyerId;

  const ReportSellerDialog({Key? key, required this.shopName, required this.buyerId})
      : super(key: key);

  @override
  State<ReportSellerDialog> createState() => _ReportSellerDialogState();
}

class _ReportSellerDialogState extends State<ReportSellerDialog> {
  final _formKey = GlobalKey<FormState>();
  String? _violationType;
  final TextEditingController _descriptionController = TextEditingController();
  File? _proofImage;

  final List<String> _violationTypes = [
    'Fake Product',
    'Poor Service',
    'Misleading Information',
    'Other',
  ];

  Future<void> _pickImage() async {
    final pickedFile = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _proofImage = File(pickedFile.path);
      });
    }
  }

  Future<void> _submitReport() async {
    if (!_formKey.currentState!.validate()) return;

    final uri = Uri.parse(
      '${Config.baseUrl}/seller-profile-report-seller/${widget.shopName}/${widget.buyerId}',
    );
    final request = http.MultipartRequest('POST', uri);

    request.fields['violation-type'] = _violationType!;
    request.fields['description'] = _descriptionController.text;

    if (_proofImage != null) {
      request.files.add(await http.MultipartFile.fromPath(
        'proof-image',
        _proofImage!.path,
        filename: path.basename(_proofImage!.path),
      ));
    }

    try {
      final response = await request.send();
      final respStr = await response.stream.bytesToString();
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Report submitted successfully.')),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to submit report: $respStr')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error submitting report: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Report Seller'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(labelText: 'Violation Type'),
                items: _violationTypes
                    .map((type) => DropdownMenuItem(value: type, child: Text(type)))
                    .toList(),
                onChanged: (val) => setState(() => _violationType = val),
                validator: (val) => val == null ? 'Please select a violation type' : null,
              ),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(labelText: 'Description'),
                maxLines: 3,
                validator: (val) =>
                    val == null || val.isEmpty ? 'Please enter a description' : null,
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  ElevatedButton.icon(
                    onPressed: _pickImage,
                    icon: const Icon(Icons.image),
                    label: const Text('Upload Proof Image'),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _proofImage != null ? path.basename(_proofImage!.path) : 'No image selected',
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _submitReport,
          child: const Text('Submit Report'),
        ),
      ],
    );
  }
}
