import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'screens/dashboard_screen.dart';
import 'screens/sites_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/transactions_screen.dart';
import 'screens/list_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/training_screen.dart';
import 'screens/join_requests_screen.dart';
import 'screens/landing_screen.dart';
import 'services/api_service.dart';

void main() {
  runApp(const MilkFlowApp());
}

class MilkFlowApp extends StatelessWidget {
  const MilkFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MilkFlow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        primaryColor: const Color(0xFF2563EB),
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2563EB)),
        textTheme: GoogleFonts.plusJakartaSansTextTheme(),
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
      ),
      home: const LandingScreen(), // Start at Landing Page like Web
    );
  }
}

class MainShell extends StatefulWidget {
  final int initialIndex;
  const MainShell({super.key, this.initialIndex = 0});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _userProfile;
  bool _isProfileLoaded = false;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final profile = await _apiService.getUserProfile();
      setState(() {
        _userProfile = profile;
        _isProfileLoaded = true;
      });
    } catch (e) {
      print('Error loading profile: $e');
      setState(() => _isProfileLoaded = true);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isProfileLoaded)
      return const Scaffold(body: Center(child: CircularProgressIndicator()));

    final role = _userProfile?['role'] ?? 'WORKER';
    final isAdmin = role == 'SUPER_ADMIN' || role == 'MANAGER';

    // Screens and items that are actually available to THIS user
    final List<Widget> visibleScreens = [
      if (isAdmin) const DashboardScreen(),
      if (!isAdmin) const ProfileScreen(), // Index 0 for clients
      if (isAdmin) const SitesScreen(), // Index 1 for admins
      if (isAdmin) const ProfileScreen(), // Index 2 for admins
      const ChatScreen(), // Index 1 for clients, Index 3 for admins
    ];

    final List<BottomNavigationBarItem> navItems = [
      if (isAdmin)
        const BottomNavigationBarItem(
            icon: Icon(LucideIcons.layoutDashboard), label: 'Admin'),
      if (!isAdmin)
        const BottomNavigationBarItem(
            icon: Icon(LucideIcons.user), label: 'My Data'),
      if (isAdmin)
        const BottomNavigationBarItem(
            icon: Icon(LucideIcons.mapPin), label: 'Sites'),
      if (isAdmin)
        const BottomNavigationBarItem(
            icon: Icon(LucideIcons.user), label: 'Profile'),
      const BottomNavigationBarItem(
          icon: Icon(LucideIcons.messageSquare), label: 'Chat'),
    ];

    // Safety: ensure index doesn't go out of bounds
    int safeIndex = _currentIndex;
    if (safeIndex >= visibleScreens.length) safeIndex = 0;

    return Scaffold(
      appBar: AppBar(
        title: Text(isAdmin ? 'Admin Portal' : 'Client Portal',
            style: const TextStyle(
                fontWeight: FontWeight.w900, letterSpacing: -0.5)),
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: const Color(0xFF1E293B),
        actions: [
          IconButton(
            icon: const Icon(LucideIcons.bell, size: 20),
            onPressed: () => Navigator.push(context,
                MaterialPageRoute(builder: (_) => const NotificationsScreen())),
          ),
          const SizedBox(width: 8),
        ],
      ),
      drawer: _buildDrawer(role, isAdmin),
      body: visibleScreens[safeIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10)
        ]),
        child: BottomNavigationBar(
          currentIndex: safeIndex,
          onTap: (index) => setState(() => _currentIndex = index),
          selectedItemColor: const Color(0xFF2563EB),
          unselectedItemColor: const Color(0xFF94A3B8),
          showUnselectedLabels: true,
          elevation: 0,
          backgroundColor: Colors.white,
          type: BottomNavigationBarType.fixed,
          items: navItems,
        ),
      ),
    );
  }

  Widget _buildDrawer(String role, bool isAdmin) {
    return Drawer(
      backgroundColor: Colors.white,
      child: Column(
        children: [
          UserAccountsDrawerHeader(
            decoration: const BoxDecoration(color: Color(0xFF2563EB)),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Text(_userProfile?['username']?[0]?.toUpperCase() ?? 'U',
                  style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2563EB))),
            ),
            accountName: Text(_userProfile?['username'] ?? 'User',
                style: const TextStyle(fontWeight: FontWeight.bold)),
            accountEmail: Text(_userProfile?['email'] ?? ''),
          ),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                if (isAdmin)
                  _buildDrawerItem(
                      LucideIcons.layoutDashboard, 'Admin Home', 0),
                if (!isAdmin)
                  _buildDrawerItem(LucideIcons.user, 'My Profile', 0),
                _buildDrawerItem(LucideIcons.mapPin, 'Collection Sites', 1),
                if (isAdmin) ...[
                  const Divider(indent: 20, endIndent: 20),
                  _buildDrawerItem(LucideIcons.users, 'Suppliers', -1,
                      isLink: true,
                      screen: ListScreen(
                          title: 'Suppliers',
                          fetchFunction: _apiService.getSuppliers)),
                  _buildDrawerItem(LucideIcons.shoppingBag, 'Buyers', -1,
                      isLink: true,
                      screen: ListScreen(
                          title: 'Buyers',
                          fetchFunction: _apiService.getBuyers)),
                  _buildDrawerItem(LucideIcons.list, 'Transactions', -1,
                      isLink: true, screen: const TransactionsScreen()),
                ],
                const Divider(indent: 20, endIndent: 20),
                _buildDrawerItem(LucideIcons.messageSquare, 'Internal Chat', -1,
                    isLink: true, screen: const ChatScreen()),
                _buildDrawerItem(LucideIcons.bookOpen, 'Training Center', -1,
                    isLink: true, screen: const TrainingScreen()),
                if (role == 'SUPER_ADMIN')
                  _buildDrawerItem(LucideIcons.userCheck, 'Join Requests', -1,
                      isLink: true, screen: const JoinRequestsScreen()),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: ListTile(
              leading: const Icon(LucideIcons.logOut, color: Colors.red),
              title: const Text('Logout',
                  style: TextStyle(
                      color: Colors.red, fontWeight: FontWeight.bold)),
              onTap: () => Navigator.pushReplacement(context,
                  MaterialPageRoute(builder: (_) => const LandingScreen())),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(IconData icon, String title, int index,
      {bool isLink = false, Widget? screen}) {
    bool isSelected = _currentIndex == index;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: ListTile(
        leading: Icon(icon,
            color:
                isSelected ? const Color(0xFF2563EB) : const Color(0xFF64748B)),
        title: Text(title,
            style: TextStyle(
              color: isSelected
                  ? const Color(0xFF2563EB)
                  : const Color(0xFF1E293B),
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            )),
        selected: isSelected,
        onTap: () {
          Navigator.pop(context);
          if (isLink && screen != null) {
            Navigator.push(context, MaterialPageRoute(builder: (_) => screen));
          } else {
            setState(() => _currentIndex = index);
          }
        },
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        selectedTileColor: const Color(0xFF2563EB).withOpacity(0.1),
      ),
    );
  }
}
