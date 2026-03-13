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
  List<dynamic> _contacts = [];
  dynamic _selectedUser;
  List<dynamic> _messages = [];
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  Timer? _pollingTimer;
  bool _isLoadingContacts = true;
  int? _myId;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
    // Start polling for messages if a user is selected
    _pollingTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
      if (_selectedUser != null) {
        _loadMessages(silent: true);
      } else {
        _loadContacts(silent: true);
      }
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    try {
      final profile = await _apiService.getUserProfile();
      _myId = profile['id'];
      await _loadContacts();
    } catch (e) {
      setState(() => _isLoadingContacts = false);
    }
  }

  Future<void> _loadContacts({bool silent = false}) async {
    try {
      final contacts = await _apiService.getUsers();
      if (mounted) {
        setState(() {
          _contacts = contacts;
          _isLoadingContacts = false;
        });
      }
    } catch (e) {
      if (!silent) setState(() => _isLoadingContacts = false);
    }
  }

  Future<void> _loadMessages({bool silent = false}) async {
    if (_selectedUser == null) return;
    try {
      final allMessages = await _apiService.getMessages();
      final filtered = allMessages.where((m) =>
        (m['sender'] == _selectedUser['id'] && m['receiver'] == _myId) ||
        (m['sender'] == _myId && m['receiver'] == _selectedUser['id'])
      ).toList();

      if (mounted) {
        setState(() {
          _messages = filtered;
        });
        
        // Mark as read if needed
        final hasUnread = filtered.any((m) => m['sender'] == _selectedUser['id'] && m['is_read'] == false);
        if (hasUnread) {
          await _apiService.markMessagesAsRead(_selectedUser['id']);
          _loadContacts(silent: true); // Update unread badges in background
        }

        if (!silent) _scrollToBottom();
      }
    } catch (e) {
      print('Msg Load Error: $e');
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
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
      backgroundColor: Colors.white,
      appBar: _buildAppBar(),
      body: _selectedUser == null ? _buildContactsList() : _buildChatBody(),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.white,
      foregroundColor: const Color(0xFF1E293B),
      title: _selectedUser == null 
        ? const Text('Internal Chat', style: TextStyle(fontWeight: FontWeight.bold))
        : Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: Colors.blue.shade100,
                child: Text(_selectedUser['username'][0].toUpperCase(), style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(_selectedUser['username'], style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  Text(_selectedUser['role'], style: const TextStyle(fontSize: 10, color: Colors.blue)),
                ],
              )
            ],
          ),
      leading: _selectedUser != null 
        ? IconButton(icon: const Icon(Icons.arrow_back_ios_new, size: 20), onPressed: () => setState(() => _selectedUser = null))
        : null,
    );
  }

  Widget _buildContactsList() {
    if (_isLoadingContacts) return const Center(child: CircularProgressIndicator());
    if (_contacts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(LucideIcons.messageSquare, size: 64, color: Colors.grey.shade200),
            const SizedBox(height: 16),
            const Text('No contacts available', style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return ListView.separated(
      itemCount: _contacts.length,
      padding: const EdgeInsets.all(16),
      separatorBuilder: (context, index) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final user = _contacts[index];
        final int unread = user['unread_count'] ?? 0;

        return Container(
          decoration: BoxDecoration(
            color: const Color(0xFFF8FAFC),
            borderRadius: BorderRadius.circular(20),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            leading: CircleAvatar(
              radius: 24,
              backgroundColor: Colors.blue.shade600,
              child: Text(user['username'][0].toUpperCase(), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
            title: Text(user['username'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            subtitle: Text(user['role'], style: const TextStyle(fontSize: 12, color: Colors.grey)),
            trailing: unread > 0 
              ? Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(12)),
                  child: Text('$unread', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                )
              : const Icon(LucideIcons.chevronRight, size: 16, color: Colors.grey),
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

  Widget _buildChatBody() {
    return Column(
      children: [
        Expanded(
          child: Container(
            color: const Color(0xFFF1F5F9).withOpacity(0.5),
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(20),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final bool isMe = msg['sender'] == _myId;
                
                return Align(
                  alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                    decoration: BoxDecoration(
                      color: isMe ? const Color(0xFF2563EB) : Colors.white,
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(20),
                        topRight: const Radius.circular(20),
                        bottomLeft: isMe ? const Radius.circular(20) : Radius.zero,
                        bottomRight: isMe ? Radius.zero : const Radius.circular(20),
                      ),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4))
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                      children: [
                        Text(
                          msg['content'],
                          style: TextStyle(color: isMe ? Colors.white : const Color(0xFF1E293B), fontSize: 14, fontWeight: FontWeight.w500),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _formatTime(msg['timestamp']),
                          style: TextStyle(color: isMe ? Colors.white60 : Colors.black26, fontSize: 9, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ),
        _buildMessageInput(),
      ],
    );
  }

  Widget _buildMessageInput() {
    return Container(
      padding: EdgeInsets.fromLTRB(16, 16, 16, MediaQuery.of(context).padding.bottom + 16),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Color(0xFFF1F5F9))),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              onSubmitted: (_) => _sendMessage(),
              decoration: InputDecoration(
                hintText: 'Write a message...',
                hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 14),
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _sendMessage,
            child: Container(
              width: 48, height: 48,
              decoration: const BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
              child: const Icon(LucideIcons.send, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(String timestamp) {
    try {
      final dt = DateTime.parse(timestamp).toLocal();
      return "${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}";
    } catch (e) { return ""; }
  }
}
