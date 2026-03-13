import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';

class JoinRequestsScreen extends StatefulWidget {
  const JoinRequestsScreen({super.key});

  @override
  State<JoinRequestsScreen> createState() => _JoinRequestsScreenState();
}

class _JoinRequestsScreenState extends State<JoinRequestsScreen> {
  final ApiService _apiService = ApiService();
  List<dynamic>? _requests;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  Future<void> _fetch() async {
    setState(() => _isLoading = true);
    try {
      final data = await _apiService.getJoinRequests();
      setState(() { _requests = data; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _handle(int id, bool approve) async {
    final success = await _apiService.processJoinRequest(id, approve);
    if (success) _fetch();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Join Requests')),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _requests?.length ?? 0,
            itemBuilder: (context, index) {
              final req = _requests![index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text(req['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('${req['request_type']} - ${req['status']}'),
                  trailing: req['status'] == 'PENDING' 
                    ? Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(icon: const Icon(LucideIcons.check, color: Colors.green), onPressed: () => _handle(req['id'], true)),
                          IconButton(icon: const Icon(LucideIcons.x, color: Colors.red), onPressed: () => _handle(req['id'], false)),
                        ],
                      )
                    : null,
                ),
              );
            },
          ),
    );
  }
}
