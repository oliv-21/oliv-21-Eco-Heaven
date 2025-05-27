import 'package:ecohaven_app/auth/login_page.dart';
import 'package:ecohaven_app/pages/dashboard.dart';
import 'package:ecohaven_app/pages/homepage.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';


import 'providers/cart_provider.dart';   // Your CartProvider import
import 'providers/order_provider.dart';  // Your OrderProvider import

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  Future<Map<String, dynamic>> getSession() async {
    final prefs = await SharedPreferences.getInstance();
    final buyerId = prefs.getInt('buyer_id');
    final roleId = prefs.getInt('role_id');
    return {
      'buyer_id': buyerId,
      'role_id': roleId,
    };
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => CartProvider()),
        ChangeNotifierProvider(create: (context) => OrderProvider()),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'EcoHaven App',
        theme: ThemeData(
          primaryColor: const Color(0xFF133056),
        ),
        home: FutureBuilder<Map<String, dynamic>>(
          future: getSession(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Scaffold(
                body: Center(child: CircularProgressIndicator()),
              );
            } else {
              final data = snapshot.data;
              final buyerId = data?['buyer_id'];
              final roleId = data?['role_id'];

              if (buyerId != null && roleId != null) {
                if (roleId == 1) {
                  return HomePage(buyer_id: buyerId);
                } else if (roleId == 4) {
                  return Dashboard(rider_id: buyerId);
                }
              }
              return const LoginPage();
            }
          },
        ),
      ),
    );
  }
}
