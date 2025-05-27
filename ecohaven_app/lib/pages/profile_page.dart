import 'dart:convert';
import 'package:ecohaven_app/auth/login_page.dart';
import 'package:ecohaven_app/pages/edit_profile_page.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:ecohaven_app/configport.dart';
import 'package:ecohaven_app/pages/homepage.dart';
import 'package:ecohaven_app/pages/order_history.dart';
import 'package:ecohaven_app/pages/notification_page.dart';
import 'package:shared_preferences/shared_preferences.dart';
class ProfilePage extends StatefulWidget {
  final int buyer_id;
  const ProfilePage({super.key, required this.buyer_id});

  @override
  _ProfilePageState createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  int _selectedIndex = 3;
  static const Color primaryColor = Color(0xFFADC8EE);
  static const Color accentColor = Color(0xFF133056);

  bool _isLoading = true;
  Map<String, dynamic> _profileData = {};

  @override
  void initState() {
    super.initState();
    _fetchProfileData();
  }

  Future<void> _fetchProfileData() async {
    final response = await http.post(
      Uri.parse('${Config.baseUrl}/buyer_dashboard/buyer_profile/mobile'),
      body: {'buyer_id': widget.buyer_id.toString()},
    );

    if (response.statusCode == 200) {
      setState(() {
        _isLoading = false;
        _profileData = json.decode(response.body);
      });
    } else {
      setState(() {
        _isLoading = false;
        _profileData = {};
      });
      print("Failed to fetch profile. Status: ${response.statusCode}");
    }
  }
  

  void _onItemTapped(int index) {
    if (index != _selectedIndex) {
      setState(() {
        _selectedIndex = index;
      });

      switch (index) {
        case 0:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => HomePage(buyer_id: widget.buyer_id),
            ),
          );
          break;
        case 1:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => NotificationPage(buyer_id: widget.buyer_id),
            ),
          );
          break;
        case 2:
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => OrderHistoryPage(buyer_id: widget.buyer_id),
            ),
          );
          break;
        case 3:
          // Already on profile page
          break;
      }
    }
  }

  Future<void> _handleLogout(BuildContext context) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.clear(); // Clear all saved session data

  // Navigate to LoginPage and remove all previous routes
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
        title: const Text('Profile'),
        backgroundColor: primaryColor,
        automaticallyImplyLeading: false,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundImage: (_profileData['profile_pic'] != null &&
                                _profileData['profile_pic'].toString().isNotEmpty)
                            ? NetworkImage(
                                '${Config.baseUrl}/assets/upload/${_profileData['profile_pic']}')
                            : const AssetImage(
                                    'assets/uploads/profile-icon-design-free-vector.jpg')
                                as ImageProvider,
                      ),
                      const SizedBox(width: 20),
                      Expanded(
                        child: Text(
                          '${_profileData['Fname']} ${_profileData['Mname']} ${_profileData['Lname']}',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(5),
                      border: Border.all(color: Colors.black26),
                      boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 2)],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              "Buyer's Profile",
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            IconButton(
                              icon: const Icon(Icons.settings, color: accentColor),
                              onPressed: () async {
                                final updatedProfile = await Navigator.push<Map<String, dynamic>>(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => EditProfilePage(
                                      profileData: _profileData,
                                      buyer_id: widget.buyer_id,
                                    ),
                                  ),
                                );

                                if (updatedProfile != null) {
                                  setState(() {
                                    _profileData = updatedProfile;
                                  });
                                }
                              },
                            ),
                          ],
                        ),
                        const Text(
                          "Manage and Protect your Account",
                          style: TextStyle(color: Colors.grey),
                        ),
                        const Divider(),
                        _profileDetail("Full Name",
                            '${_profileData['Fname']} ${_profileData['Mname']} ${_profileData['Lname']}'),
                        _profileDetail("Email Address", _profileData['email']),
                        _profileDetail("Gender", _profileData['gender']),
                        _profileDetail("Contact #", _profileData['contact_num']),
                        _profileDetail("Birth Date", _profileData['birthday']),
                        _profileDetail(
                          "Address",
                          '${_profileData['houseNo']} ${_profileData['street']} ${_profileData['barangay']} ${_profileData['city']} ${_profileData['Province']} ${_profileData['postal_code']}',
                        ),
                        const SizedBox(height: 25),
                        Align(
                          alignment: Alignment.centerRight,
                          child: ElevatedButton(
                              onPressed: () => _handleLogout(context),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.red,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(2),
                                ),
                              ),
                              child: const Text(
                                "Logout",
                                style: TextStyle(color: Colors.white),
                              ),
                            ),

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
        selectedItemColor: accentColor,
        unselectedItemColor: Colors.grey[800],
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.notifications), label: 'Notifications'),
          BottomNavigationBarItem(icon: Icon(Icons.history), label: 'Orders'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }

  Widget _profileDetail(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: RichText(
        text: TextSpan(
          style: const TextStyle(fontSize: 16, color: Colors.black),
          children: [
            TextSpan(text: "$label: ", style: const TextStyle(fontWeight: FontWeight.bold)),
            TextSpan(text: value),
          ],
        ),
      ),
    );
  }
}
