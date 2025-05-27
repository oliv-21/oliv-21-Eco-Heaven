
import 'package:ecohaven_app/pages/chat_page.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:http/http.dart' as http;
import 'package:ecohaven_app/configport.dart';
// ignore: file_names
import 'dart:convert';
class ChatHistoryPage extends StatefulWidget {
  final int buyerId;
  const ChatHistoryPage({Key? key, required this.buyerId}) : super(key: key);

  @override
  State<ChatHistoryPage> createState() => _ChatHistoryPageState();
}

class _ChatHistoryPageState extends State<ChatHistoryPage> {
  List<Map<String, dynamic>> _chats = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadChats();
  }

  Future<void> _loadChats() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${Config.baseUrl}/chatMobile?buyer_id=${widget.buyerId}'),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        setState(() {
          _chats = data.map<Map<String, dynamic>>((chat) {
            final mapChat = Map<String, dynamic>.from(chat as Map);
            // Parse timestamp safely
            DateTime lastTime;
            try {
              lastTime = DateFormat('yyyy-MM-dd HH:mm:ss').parse(mapChat['last_message_time']);
            } catch (_) {
              lastTime = DateTime.now();
            }
            mapChat['last_message_time'] = lastTime;
            return mapChat;
          }).toList();
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = 'Failed to load chats (${response.statusCode})';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Connection error: $e';
        _isLoading = false;
      });
    }
  }

  Widget _buildChatTile(Map<String, dynamic> chat) {
    return ListTile(
      leading: CircleAvatar(
        backgroundImage: NetworkImage(
          '${Config.baseUrl}/assets/upload/${chat['shop_logo']}',
        ),
        onBackgroundImageError: (_, __) {},
        child: chat['shop_logo'] == null
            ? const Icon(Icons.store)
            : null,
      ),
      title: Text(chat['shop_name'] ?? 'Unknown Shop'),
      subtitle: Text(chat['last_message'] ?? ''),
      trailing: Text(
        DateFormat('MMM d, HH:mm').format(chat['last_message_time']),
        style: const TextStyle(fontSize: 12, color: Colors.grey),
      ),
      onTap: () {
        // Navigate to ChatPage for this shop
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ChatPage(
              shopName: chat['shop_name'],
              shopLogo: chat['shop_logo'],
              buyerId: widget.buyerId,
            ),
          ),
        );
      },
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, color: Colors.red, size: 48),
              const SizedBox(height: 16),
              Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadChats,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }
    if (_chats.isEmpty) {
      return const Center(child: Text('No chats found.'));
    }
    return RefreshIndicator(
      onRefresh: _loadChats,
      child: ListView.separated(
        itemCount: _chats.length,
        separatorBuilder: (_, __) => const Divider(height: 0),
        itemBuilder: (context, index) => _buildChatTile(_chats[index]),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Chats'),
      ),
      body: _buildBody(),
    );
  }
}
