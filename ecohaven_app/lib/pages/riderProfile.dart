import 'dart:convert';
import 'package:ecohaven_app/configport.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../auth/login_page.dart'; // Adjust path to your login page

class RiderProfilePage extends StatefulWidget {
  final int riderId;
  const RiderProfilePage({Key? key, required this.riderId}) : super(key: key);

  @override
  State<RiderProfilePage> createState() => _RiderProfilePageState();
}

class _RiderProfilePageState extends State<RiderProfilePage> {
  Map<String, dynamic>? riderData;
  bool isLoading = true;
  final Color primaryColor = const Color(0xFF133157);

  @override
  void initState() {
    super.initState();
    _fetchRiderProfile();
  }

  Future<void> _fetchRiderProfile() async {
    try {
      final response = await http.get(
        Uri.parse('${Config.baseUrl}/rider_profile?rider_id=${widget.riderId}'),
      );
      if (response.statusCode == 200) {
        setState(() {
          riderData = jsonDecode(response.body);
          isLoading = false;
        });
      } else {
        setState(() => isLoading = false);
      }
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  Future<void> _handleLogout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    // Navigate to login page and remove all previous routes
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => const LoginPage()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Rider Profile'),
        backgroundColor: primaryColor,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () async {
              final confirm = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Confirm Logout'),
                  content: const Text('Are you sure you want to logout?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      child: const Text('Cancel'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, true),
                      child: const Text('Logout'),
                    ),
                  ],
                ),
              );
              if (confirm == true) {
                await _handleLogout();
              }
            },
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : riderData == null
              ? const Center(child: Text('No data found'))
              : SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      CircleAvatar(
                        radius: 60,
                        backgroundColor: Colors.grey[300],
                        backgroundImage: riderData!['profile_pic'] != null && riderData!['profile_pic'].isNotEmpty
                            ? NetworkImage('${Config.baseUrl}/assets/upload/${riderData!['profile_pic']}')
                            : null,
                        child: (riderData!['profile_pic'] == null || riderData!['profile_pic'].isEmpty)
                            ? Icon(Icons.person, size: 60, color: Colors.grey[600])
                            : null,
                      ),
                      const SizedBox(height: 20),
                      Text(
                        '${riderData!['Fname']} ${riderData!['Lname']}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF133157),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        riderData!['mobile_number'] ?? '',
                        style: TextStyle(
                          color: Colors.grey[700],
                          fontSize: 16,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 30),
                      Card(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        elevation: 3,
                        child: ListTile(
                          leading: Icon(Icons.location_on, color: primaryColor),
                          title: const Text(
                            'Address',
                            style: TextStyle(fontWeight: FontWeight.w600),
                          ),
                          subtitle: Text(
                            riderData!['address'] ?? 'No address provided',
                            style: const TextStyle(fontSize: 16),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
      // Optional floating logout button (uncomment if you want)
      
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final confirm = await showDialog<bool>(
            context: context,
            builder: (ctx) => AlertDialog(
              title: const Text('Confirm Logout'),
              content: const Text('Are you sure you want to logout?'),
              actions: [
                TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Logout')),
              ],
            ),
          );
          if (confirm == true) {
            await _handleLogout();
          }
        },
        label: const Text('Logout'),
        icon: const Icon(Icons.logout),
        backgroundColor: Colors.red,
      ),
      
    );
  }
}
