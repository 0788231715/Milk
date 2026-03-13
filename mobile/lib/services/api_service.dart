import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Use 10.0.2.2 for Android Emulator, localhost for iOS/Web
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000/api';
    // For Android emulator to reach host's localhost
    return 'http://10.0.2.2:8000/api';
  }

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();
    print('--- API DEBUG: Sending Token: ${token != null ? "YES (starts with ${token.substring(0, 5)}...)" : "NO (NULL)"}');
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // --- Auth ---
  Future<bool> login(String username, String password) async {
    print('--- API DEBUG: Attempting login for $username');
    final response = await http.post(
      Uri.parse('$baseUrl/token/'),
      body: json.encode({'username': username, 'password': password}),
      headers: {'Content-Type': 'application/json'},
    );

    print('--- API DEBUG: Login response status: ${response.statusCode}');
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', data['access']);
      await prefs.setString('refresh_token', data['refresh']);
      print('--- API DEBUG: Token saved successfully');
      return true;
    }
    return false;
  }

  Future<Map<String, dynamic>> getUserProfile() async {
    final response = await http.get(Uri.parse('$baseUrl/users/profile/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load profile');
  }

  // --- Dashboard ---
  Future<Map<String, dynamic>> getDashboardData() async {
    final response = await http.get(Uri.parse('$baseUrl/transactions/dashboard/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load dashboard');
  }

  // --- Sites ---
  Future<List<dynamic>> getSites() async {
    final response = await http.get(Uri.parse('$baseUrl/business/sites/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load sites');
  }

  Future<bool> createSite(Map<String, dynamic> data) async {
    final response = await http.post(Uri.parse('$baseUrl/business/sites/'), body: json.encode(data), headers: await _getHeaders());
    return response.statusCode == 201;
  }

  // --- Suppliers ---
  Future<List<dynamic>> getSuppliers() async {
    final response = await http.get(Uri.parse('$baseUrl/business/suppliers/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load suppliers');
  }

  Future<bool> createSupplier(Map<String, dynamic> data) async {
    final response = await http.post(Uri.parse('$baseUrl/business/suppliers/'), body: json.encode(data), headers: await _getHeaders());
    return response.statusCode == 201;
  }

  // --- Buyers ---
  Future<List<dynamic>> getBuyers() async {
    final response = await http.get(Uri.parse('$baseUrl/business/buyers/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load buyers');
  }

  Future<bool> createBuyer(Map<String, dynamic> data) async {
    final response = await http.post(Uri.parse('$baseUrl/business/buyers/'), body: json.encode(data), headers: await _getHeaders());
    return response.statusCode == 201;
  }

  // --- Workers ---
  Future<List<dynamic>> getWorkers() async {
    final response = await http.get(Uri.parse('$baseUrl/business/workers/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load workers');
  }

  Future<bool> createWorker(Map<String, dynamic> data) async {
    final response = await http.post(Uri.parse('$baseUrl/business/workers/'), body: json.encode(data), headers: await _getHeaders());
    return response.statusCode == 201;
  }

  // --- Users ---
  Future<List<dynamic>> getUsers() async {
    final response = await http.get(Uri.parse('$baseUrl/users/users/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load users');
  }

  // --- Training ---
  Future<List<dynamic>> getTrainingResources() async {
    final response = await http.get(Uri.parse('$baseUrl/training/resources/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load training resources');
  }

  Future<List<dynamic>> getMilkStandards() async {
    final response = await http.get(Uri.parse('$baseUrl/training/standards/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load milk standards');
  }

  Future<List<dynamic>> getSystemUpdates() async {
    final response = await http.get(Uri.parse('$baseUrl/training/updates/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load system updates');
  }

  // --- Join Requests ---
  Future<List<dynamic>> getJoinRequests() async {
    final response = await http.get(Uri.parse('$baseUrl/business/join-requests/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load join requests');
  }

  Future<bool> processJoinRequest(int id, bool approve) async {
    final action = approve ? 'approve' : 'reject';
    final response = await http.post(Uri.parse('$baseUrl/business/join-requests/$id/$action/'), headers: await _getHeaders());
    return response.statusCode == 200;
  }

  // --- Transactions ---
  Future<List<dynamic>> getSupplyRecords({int? siteId}) async {
    String url = '$baseUrl/transactions/supply/';
    if (siteId != null) url += '?site=$siteId';
    final response = await http.get(Uri.parse(url), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load supplies');
  }

  Future<List<dynamic>> getSaleRecords({int? siteId}) async {
    String url = '$baseUrl/transactions/sales/';
    if (siteId != null) url += '?site_source=$siteId';
    final response = await http.get(Uri.parse(url), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load sales');
  }


  // --- Communication ---
  Future<List<dynamic>> getNotifications() async {
    final response = await http.get(Uri.parse('$baseUrl/communication/notifications/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load notifications');
  }

  Future<List<dynamic>> getMessages() async {
    final response = await http.get(Uri.parse('$baseUrl/communication/messages/'), headers: await _getHeaders());
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load messages');
  }

  Future<bool> sendMessage(int? receiverId, String content) async {
    final response = await http.post(
      Uri.parse('$baseUrl/communication/messages/'),
      body: json.encode({'receiver': receiverId, 'content': content}),
      headers: await _getHeaders(),
    );
    return response.statusCode == 201;
  }

  Future<bool> markMessagesAsRead(int senderId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/communication/messages/mark_as_read/'),
      body: json.encode({'sender_id': senderId}),
      headers: await _getHeaders(),
    );
    return response.statusCode == 200;
  }
}
