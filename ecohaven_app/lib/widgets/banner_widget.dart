import 'package:flutter/material.dart';

class BannerWidget extends StatelessWidget {
  const BannerWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(10),
      height: 150,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(5),
        color: Colors.blue.shade300,
        image: const DecorationImage(
          image: AssetImage('assets/banner.png'),
          fit: BoxFit.cover, // Ensures the image covers the entire container
        ),
      ),
    );
  }
}
