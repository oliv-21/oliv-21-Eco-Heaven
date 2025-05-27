import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:ecohaven_app/configport.dart';

class OngoingDeliveryPage extends StatefulWidget {
  final int riderId;
  const OngoingDeliveryPage({super.key, required this.riderId});

  @override
  State<OngoingDeliveryPage> createState() => _OngoingDeliveryPageState();
}

class _OngoingDeliveryPageState extends State<OngoingDeliveryPage> {
  List<dynamic> parcels = [];
  bool isLoading = false;
  final Color primaryColor = const Color(0xFF133157);

  @override
  void initState() {
    super.initState();
    _fetchOngoingDeliveries();
  }

  Future<void> _fetchOngoingDeliveries() async {
    setState(() => isLoading = true);
    try {
      final response = await http.get(Uri.parse(
        '${Config.baseUrl}/ongoing_deliveries?rider_id=${widget.riderId}',
      ));
      if (response.statusCode == 200) {
        setState(() => parcels = jsonDecode(response.body));
      } else {
        setState(() => parcels = []);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load ongoing deliveries')),
        );
      }
    } catch (e) {
      setState(() => parcels = []);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }
  Future<void> _markAsDelivered(String orderId) async {
    setState(() => isLoading = true);
    try {
      final response = await http.post(
        Uri.parse('${Config.baseUrl}/rider-deliveredMobile'),
        body: {
          'order_id': orderId,
          'rider_id': widget.riderId.toString(),
        },
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? 'Marked as delivered!')),
        );
        _fetchOngoingDeliveries(); // Refresh list
      } else {
        final data = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['error'] ?? 'Failed to mark as delivered')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  void _showDetailsDialog(BuildContext context, Map<String, dynamic> parcel) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          elevation: 8,
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Text(
                    'Receiver Information',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 20,
                      letterSpacing: 0.2,
                    ),
                  ),
                ),
                Divider(thickness: 1, height: 20),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.grey[50],
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  padding: EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        parcel['order_id'].toString(),
                        style: TextStyle(
                          color: primaryColor,
                          fontWeight: FontWeight.bold,
                          fontSize: 17,
                          letterSpacing: 0.5,
                        ),
                      ),
                      SizedBox(height: 8),
                      RichText(
                        text: TextSpan(
                          style: TextStyle(fontSize: 15.5, color: Colors.grey[900]),
                          children: [
                            TextSpan(
                              text: 'Name: ',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            TextSpan(
                              text: parcel['fullname'] ?? '',
                            ),
                          ],
                        ),
                      ),
                      SizedBox(height: 2),
                      RichText(
                        text: TextSpan(
                          style: TextStyle(fontSize: 15.5, color: Colors.grey[800]),
                          children: [
                            TextSpan(
                              text: 'Address: ',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            TextSpan(
                              text: parcel['Fulladdress'] ?? '',
                            ),
                          ],
                        ),
                      ),
                      SizedBox(height: 2),
                      RichText(
                        text: TextSpan(
                          style: TextStyle(fontSize: 15.5, color: Colors.grey[700]),
                          children: [
                            TextSpan(
                              text: 'Mobile Number: ',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            TextSpan(
                              text: parcel['mobile_number'] ?? '',
                            ),
                          ],
                        ),
                      ),

                    ],
                  ),
                ),
                SizedBox(height: 18),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Amount',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    Text(
                      'Php ${parcel['total_price'] ?? '0.00'}',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),

                  ],
                ),
                SizedBox(height: 22),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color.fromARGB(255, 240, 76, 76),
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      elevation: 0,
                    ),
                    child: Text(
                      'Close',
                      style: TextStyle(
                        fontSize: 16.5,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.1,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: PreferredSize(
        preferredSize: Size.fromHeight(110),
        child: AppBar(
          backgroundColor: primaryColor.withOpacity(0.85),
          automaticallyImplyLeading: false,
          elevation: 0,
          flexibleSpace: Padding(
            padding: const EdgeInsets.only(top: 50.0, left: 16.0, right: 16.0),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search parcels...',
                prefixIcon: Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                contentPadding: EdgeInsets.symmetric(horizontal: 16.0),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            color: primaryColor,
            padding: EdgeInsets.symmetric(vertical: 14.0),
            child: Center(
              child: Text(
                'Ongoing Deliveries',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                  fontSize: 18,
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Available Parcels: ${parcels.length}',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
              ),
            ),
          ),
          Divider(),
          Expanded(
            child: isLoading
                ? Center(child: CircularProgressIndicator())
                : parcels.isEmpty
                    ? Center(child: Text('No ongoing deliveries'))
                    : ListView.builder(
                        itemCount: parcels.length,
                        itemBuilder: (context, index) {
                          final parcel = parcels[index];
                          return Card(
                            margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                              side: BorderSide(color: Colors.grey.shade300),
                            ),
                            elevation: 2,
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    parcel['order_id'].toString(),
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                  SizedBox(height: 6),
                                  Text(
                                    parcel['fullname'] ?? '',
                                    style: TextStyle(color: Colors.grey[900]),
                                  ),
                                  Text(
                                    parcel['full_address'] ?? '',
                                    style: TextStyle(color: Colors.grey[900]),
                                  ),
                                  SizedBox(height: 12),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: [
                                      SizedBox(
                                        width: 120,
                                        child: OutlinedButton(
                                          onPressed: () {
                                            _showDetailsDialog(context, parcel);
                                          },
                                          style: OutlinedButton.styleFrom(
                                            backgroundColor: Colors.white,
                                            side: BorderSide(
                                              color: primaryColor,
                                              width: 2,
                                            ),
                                            padding: EdgeInsets.symmetric(
                                              horizontal: 20,
                                              vertical: 10,
                                            ),
                                            shape: RoundedRectangleBorder(
                                              borderRadius: BorderRadius.circular(8),
                                            ),
                                          ),
                                          child: Text(
                                            'Details',
                                            style: TextStyle(
                                              color: primaryColor,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                        ),
                                      ),
                                      SizedBox(width: 12),
                                      SizedBox(
                                        width: 120,
                                        child: ElevatedButton(
                                          onPressed: () {
                                              _markAsDelivered(parcel['order_id'].toString());
                                            },
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: primaryColor,
                                            padding: EdgeInsets.symmetric(
                                              horizontal: 20,
                                              vertical: 10,
                                            ),
                                            shape: RoundedRectangleBorder(
                                              borderRadius: BorderRadius.circular(8),
                                            ),
                                          ),
                                          child: Text(
                                            'Delivered',
                                            style: TextStyle(
                                              color: Colors.white,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
