import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:ecohaven_app/configport.dart';
import 'package:http/http.dart' as http;

class ChatPage extends StatefulWidget {
  final String shopName;
  final String shopLogo;
  final int buyerId;

  static const Color primaryColor = Color(0xFFADC8EE);
  static const Color accentColor = Color(0xFF133056);

  const ChatPage({
    Key? key,
    required this.shopName,
    required this.shopLogo,
    required this.buyerId,
  }) : super(key: key);

  @override
  State<ChatPage> createState() => _ChatPageState();
}

// Helper: Parse MySQL datetime string (e.g. "2024-12-08 21:45:26")
DateTime parseMysqlDatetime(String dateStr) {
  try {
    return DateFormat('yyyy-MM-dd HH:mm:ss').parse(dateStr);
  } catch (_) {
    return DateTime.now();
  }
}

// Helper: Parse RFC 1123 datetime string (e.g. "Wed, 30 Apr 2025 22:49:58 GMT")
DateTime parseRfc1123Date(String dateStr) {
  try {
    return DateFormat("EEE, dd MMM yyyy HH:mm:ss 'GMT'", 'en_US').parseUtc(dateStr);
  } catch (_) {
    return DateTime.now();
  }
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _messageController = TextEditingController();
  List<Map<String, dynamic>> _messages = [];
  bool _isLoading = true;
  String? _errorMessage;
  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    _loadMessages();
  }

  Future<void> _loadMessages() async {
    try {
      final response = await http.get(
        Uri.parse('${Config.baseUrl}/chatMobile/${widget.shopName}/${widget.buyerId}'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _messages = (data['messages'] as List)
            .map<Map<String, dynamic>>((msg) {
              // Ensure msg is Map<String, dynamic>
              final mapMsg = Map<String, dynamic>.from(msg as Map);
              DateTime timestamp;
              try {
                timestamp = DateTime.parse(mapMsg['timestamp']);
              } catch (e) {
                timestamp = DateTime.now();
                debugPrint('Date parse error: ${mapMsg['timestamp']}');
              }
              return {...mapMsg, 'timestamp': timestamp};
            })
            .toList();

          _isLoading = false;
          _errorMessage = null;
        });
      } else {
        setState(() {
          _errorMessage = 'Failed to load messages (${response.statusCode})';
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

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    setState(() => _isSending = true);

    try {
      final response = await http.post(
        Uri.parse('${Config.baseUrl}/chatMobile/${widget.shopName}/${widget.buyerId}'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': text}),
      );

      if (response.statusCode == 200) {
        _messageController.clear();
        await _loadMessages();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send message: ${response.statusCode}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Network error: $e')),
      );
    } finally {
      setState(() => _isSending = false);
    }
  }

  Widget _buildMessageBubble(Map<String, dynamic> message) {
    final isMe = message['sender_id'] == widget.buyerId;
    final timestamp = message['timestamp'] as DateTime;

    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.7,
        ),
        decoration: BoxDecoration(
          color: isMe ? ChatPage.primaryColor : ChatPage.accentColor,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              message['message'],
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  DateFormat('HH:mm').format(timestamp),
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
                if (isMe)
                  const Padding(
                    padding: EdgeInsets.only(left: 4),
                    child: Icon(
                      Icons.check_circle_outline,
                      size: 12,
                      color: Colors.white70,
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingIndicator() => const Center(child: CircularProgressIndicator());

  Widget _buildErrorDisplay() => Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, color: Colors.red, size: 48),
              const SizedBox(height: 16),
              Text(
                _errorMessage ?? 'Unknown error',
                style: const TextStyle(color: Colors.red),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadMessages,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFCEEEF),
      appBar: AppBar(
        backgroundColor: ChatPage.primaryColor,
        title: Row(
          children: [
            ClipOval(
              child: Image.network(
                '${Config.baseUrl}/assets/upload/${widget.shopLogo}',
                width: 40,
                height: 40,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => const Icon(Icons.store, size: 40),
              ),
            ),
            const SizedBox(width: 10),
            Text(
              widget.shopName,
              style: const TextStyle(color: Colors.white),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: RefreshIndicator(
              onRefresh: _loadMessages,
              child: _isLoading
                  ? _buildLoadingIndicator()
                  : _errorMessage != null
                      ? _buildErrorDisplay()
                      : ListView.builder(
                          reverse: true,
                          padding: const EdgeInsets.all(8),
                          itemCount: _messages.length,
                          itemBuilder: (context, index) =>
                              _buildMessageBubble(_messages[_messages.length - 1 - index]),
                        ),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            color: Colors.white,
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: 'Type your message...',
                      border: InputBorder.none,
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                _isSending
                    ? const Padding(
                        padding: EdgeInsets.all(8.0),
                        child: SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                      )
                    : IconButton(
                        icon: const Icon(Icons.send, color: ChatPage.accentColor),
                        onPressed: _sendMessage,
                      ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
