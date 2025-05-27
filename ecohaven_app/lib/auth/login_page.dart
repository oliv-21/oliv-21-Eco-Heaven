import 'dart:convert';
import 'package:ecohaven_app/configport.dart';
import 'package:ecohaven_app/pages/dashboard.dart';
import 'package:ecohaven_app/pages/homepage.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'forgot_pass.dart';
import 'signup_page.dart';

class LoginPage extends StatefulWidget {
   final String? errorMessage;
  final String? successMessage;
  const LoginPage({Key? key, this.errorMessage, this.successMessage}) : super(key: key);

  @override
  _LoginPageState createState() => _LoginPageState();
  
}

class _LoginPageState extends State<LoginPage> {
  @override
  void initState() {
    super.initState();

    if (widget.errorMessage != null && widget.errorMessage!.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(widget.errorMessage!), backgroundColor: const Color.fromARGB(255, 116, 114, 218)),
        );
      });
    }

    // Show success message if passed
    if (widget.successMessage != null && widget.successMessage!.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(widget.successMessage!), backgroundColor: const Color.fromARGB(255, 99, 101, 224)),
        );
      });
    }
  }
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  
  Future<void> loginUser() async {
    if (!_formKey.currentState!.validate()) return;

    final url = Uri.parse('${Config.baseUrl}/api/login');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': _emailController.text.trim(),
        'password': _passwordController.text.trim(),
      }),
    );

    if (response.statusCode == 200) {
      try {
        final data = jsonDecode(response.body);
        final buyerId = data['buyer_id'];
        final roleId = data['role_id'];

        // Save session data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setInt('buyer_id', buyerId);
        await prefs.setInt('role_id', roleId);

        if (roleId == 1) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => HomePage(buyer_id: buyerId)),
          );
        } else if (roleId == 4) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => Dashboard(rider_id: buyerId)),
          );
        } else {
          showDialog(
            context: context,
            builder: (_) => AlertDialog(
              title: const Text("Unauthorized"),
              content: const Text("Your role is not allowed to login here."),
              actions: [
                TextButton(onPressed: () => Navigator.pop(context), child: const Text("OK"))
              ],
            ),
          );
        }
      } catch (e) {
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text("Error"),
            content: const Text("Failed to parse login response."),
            actions: [
              TextButton(onPressed: () => Navigator.pop(context), child: const Text("OK"))
            ],
          ),
        );
      }
    } else {
      final error = jsonDecode(response.body);
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text("Login Failed"),
          content: Text(error['message'] ?? 'Invalid credentials'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text("OK"))
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Login",
          style: TextStyle(color: Color(0xFF133056), fontSize: 22.0, fontWeight: FontWeight.bold),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              const SizedBox(height: 30.0),
              Image.asset('assets/logo.png', height: MediaQuery.of(context).size.height * 0.2),
              const SizedBox(height: 40.0),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: "Email", border: OutlineInputBorder()),
                validator: (value) => value!.isEmpty ? 'Please enter your email' : null,
              ),
              const SizedBox(height: 18.0),
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(labelText: "Password", border: OutlineInputBorder()),
                validator: (value) => value!.isEmpty ? 'Please enter your password' : null,
              ),
              TextButton(
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const ForgotPass())),
                child: const Text('Forgot Password?'),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF133056),
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.zero),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  onPressed: loginUser,
                  child: const Text("Login", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w500)),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const SignupPage())),
                child: const Text.rich(
                  TextSpan(
                    text: "Don't have an account? ",
                    style: TextStyle(color: Colors.black, fontWeight: FontWeight.w400),
                    children: [TextSpan(text: 'Sign Up', style: TextStyle(color: Color(0xFFFBB51F), fontWeight: FontWeight.w600))],
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
