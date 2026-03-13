import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';
import 'dart:async';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiService _apiService = ApiService();
  List<dynamic> _users = [];
  dynamic _selectedUser;
  List<dynamic> _messages = [];
  final TextEditingController _messageController = TextEditingController();
  Timer? _timer;
  bool _isLoadingUsers = true;
  int? _currentUserId;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
    _timer = Timer.periodic(const Duration(seconds: 3), (timer) {
      if (_selectedUser != null) {
        _loadMessages();
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    try {
      final users = await _apiService.getUsers();
      final profile = await _apiService.getDashboardData(); // To get current user info
      // In a real app, we'd have a dedicated 'me' endpoint or better profile data
      // For now, we'll try to find our ID from the users list based on name if needed
      // but the API messages returns IDs we can compare with.
      
      setState(() {
        _users = users;
        _isLoadingUsers = false;
      });
    } catch (e) {
      setState(() => _isLoadingUsers = false);
    }
  }

  Future<void> _loadMessages() async {
    if (_selectedUser == null) return;
    try {
      final allMessages = await _apiService.getMessages();
      final filteredMessages = allMessages.where((m) =>
        (m['sender'] == _selectedUser['id']) || (m['receiver'] == _selectedUser['id'])
      ).toList();

      if (mounted) {
        setState(() {
          _messages = filteredMessages;
        });
        
        // Mark as read if there are unread messages from the other person
        final hasUnread = filteredMessages.any((m) => m['sender'] == _selectedUser['id'] && m['is_read'] == false);
        if (hasUnread) {
          await _apiService.markMessagesAsRead(_selectedUser['id']);
        }
      }
    } catch (e) {
      print('Error loading messages: $e');
    }
  }

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty || _selectedUser == null) return;

    final success = await _apiService.sendMessage(_selectedUser['id'], text);
    if (success) {
      _messageController.clear();
      _loadMessages();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: Text(_selectedUser == null ? 'Messages' : _selectedUser['username']),
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        leading: _selectedUser != null 
          ? IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: () => setState(() => _selectedUser = null),
            )
          : null,
      ),
      body: _selectedUser == null ? _buildUserList() : _buildChatWindow(),
    );
  }

  Widget _buildUserList() {
    if (_isLoadingUsers) return const Center(child: CircularProgressIndicator());
    
    return ListView.builder(
      itemCount: _users.length,
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) {
        final user = _users[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.blue.shade100,
              child: Text(user['username'][0].toUpperCase()),
            ),
            title: Text(user['username'], style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(user['role']),
            onTap: () {
              setState(() {
                _selectedUser = user;
                _messages = [];
              });
              _loadMessages();
            },
          ),
        );
      },
    );
  }

  Widget _buildChatWindow() {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            reverse: false,
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length,
            itemBuilder: (context, index) {
              final msg = _messages[index];
              final isMe = msg['sender_username'] != _selectedUser['username'];
              
              return Align(
                alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: isMe ? const Color(0xFF2563EB) : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(16),
                      topRight: const Radius.circular(16),
                      bottomLeft: isMe ? const Radius.circular(16) : Radius.zero,
                      bottomRight: isMe ? Radius.zero : const Radius.circular(16),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 5,
                        offset: const Offset(0, 2),
                      )
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                    children: [
                      Text(
                        msg['content'],
                        style: TextStyle(
                          color: isMe ? Colors.white : Colors.black87,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _formatTime(msg['timestamp']),
                        style: TextStyle(
                          color: isMe ? Colors.white70 : Colors.black38,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        _buildMessageInput(),
      ],
    );
  }

  Widget _buildMessageInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Colors.grey.shade200)),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: 'Type your message...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: const Color(0xFFF1F5F9),
                contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _sendMessage,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: const BoxDecoration(
                color: Color(0xFF2563EB),
                shape: BoxShape.circle,
              ),
              child: const Icon(LucideIcons.send, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(String timestamp) {
    final dt = DateTime.parse(timestamp);
    return "${dt.hour}:${dt.minute.toString().padLeft(2, '0')}";
  }
}
