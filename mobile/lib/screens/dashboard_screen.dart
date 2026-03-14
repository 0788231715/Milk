import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';
import 'chat_screen.dart';
import 'notifications_screen.dart';
import 'profile_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _data;
  Map<String, dynamic>? _userProfile;
  int _unreadNotifications = 0;
  int _unreadMessages = 0;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 1. Load Profile first to check role
      final profile = await _apiService.getUserProfile();
      _userProfile = profile;

      final role = profile['role'];
      if (role != 'SUPER_ADMIN' && role != 'MANAGER') {
        if (mounted) {
          Navigator.pushReplacement(context,
              MaterialPageRoute(builder: (_) => const ProfileScreen()));
        }
        return;
      }

      // 2. Load Dashboard Data
      final data = await _apiService.getDashboardData();

      // 3. Load Communication stats
      final notifications = await _apiService.getNotifications();
      final messages = await _apiService.getMessages();

      final unreadNotifs =
          notifications.where((n) => n['is_read'] == false).length;
      final unreadMsgs = messages.where((m) => m['is_read'] == false).length;

      if (mounted) {
        setState(() {
          _data = data;
          _unreadNotifications = unreadNotifs;
          _unreadMessages = unreadMsgs;
          _isLoading = false;
        });
      }
    } catch (e) {
      print('Dashboard Load Error: $e');
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().contains('Failed to load profile')
              ? 'Session expired or profile unavailable. Please login again.'
              : 'Error connecting to server. Please check your connection.';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading)
      return const Scaffold(body: Center(child: CircularProgressIndicator()));

    if (_errorMessage != null) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(LucideIcons.alertCircle,
                    color: Colors.red, size: 48),
                const SizedBox(height: 16),
                Text(_errorMessage!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red)),
                const SizedBox(height: 24),
                ElevatedButton(
                    onPressed: _loadData, child: const Text('Retry')),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: CustomScrollView(
          slivers: [
            _buildAppBar(),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildWelcomeHeader(),
                    const SizedBox(height: 24),
                    _buildMainStats(),
                    const SizedBox(height: 32),
                    _buildSectionHeader(
                        'Volume Insights', LucideIcons.barChart2),
                    const SizedBox(height: 16),
                    _buildVolumeGrid(),
                    const SizedBox(height: 32),
                    _buildSectionHeader('Financials', LucideIcons.trendingUp),
                    const SizedBox(height: 16),
                    _buildRevenueCards(),
                    const SizedBox(height: 32),
                    _buildSectionHeader(
                        'Site Performance', LucideIcons.factory),
                    const SizedBox(height: 16),
                    _buildSiteList(),
                    const SizedBox(height: 100),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      floating: true,
      backgroundColor: Colors.white,
      elevation: 0,
      title: const Text('MilkFlow Admin',
          style:
              TextStyle(color: Color(0xFF1E293B), fontWeight: FontWeight.bold)),
      actions: [
        _buildIconButton(
          icon: LucideIcons.bell,
          count: _unreadNotifications,
          onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const NotificationsScreen()))
              .then((_) => _loadData()),
        ),
        _buildIconButton(
          icon: LucideIcons.messageSquare,
          count: _unreadMessages,
          onTap: () => Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const ChatScreen()))
              .then((_) => _loadData()),
        ),
        const SizedBox(width: 8),
      ],
    );
  }

  Widget _buildWelcomeHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Hello, ${_userProfile?['username'] ?? 'User'}',
            style: TextStyle(color: Colors.grey.shade600, fontSize: 16)),
        const Text('Milk Business Portal',
            style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E293B))),
      ],
    );
  }

  Widget _buildMainStats() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
                colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)]),
            borderRadius: BorderRadius.circular(32),
            boxShadow: [
              BoxShadow(
                  color: const Color(0xFF2563EB).withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 10))
            ],
          ),
          child: Column(
            children: [
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Intake Today',
                      style: TextStyle(color: Colors.white70, fontSize: 14)),
                  Icon(LucideIcons.droplet, color: Colors.white, size: 20),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('${_data?['milk_today'] ?? 0}',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 40,
                          fontWeight: FontWeight.bold)),
                  const Padding(
                    padding: EdgeInsets.only(bottom: 8, left: 4),
                    child: Text('Liters',
                        style: TextStyle(color: Colors.white70, fontSize: 16)),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              const Divider(color: Colors.white24),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildSmallWhiteStat(
                      'Profit Today', 'RWF ${_data?['profit_today'] ?? 0}'),
                  _buildSmallWhiteStat(
                      'Loss', '${_data?['loss_today'] ?? 0} L'),
                ],
              )
            ],
          ),
        ),
        const SizedBox(height: 16),
        _buildRevenueCards(),
      ],
    );
  }

  Widget _buildSmallWhiteStat(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label,
            style: const TextStyle(color: Colors.white60, fontSize: 11)),
        Text(value,
            style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildVolumeGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      childAspectRatio: 1.6,
      children: [
        _buildStatCard('This Week', '${_data?['milk_week'] ?? 0} L',
            LucideIcons.calendar, Colors.blue),
        _buildStatCard('This Month', '${_data?['milk_month'] ?? 0} L',
            LucideIcons.layoutDashboard, Colors.indigo),
      ],
    );
  }

  Widget _buildStatCard(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFF1F5F9)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(height: 8),
          Text(value,
              style:
                  const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Text(title,
              style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
        ],
      ),
    );
  }

  Widget _buildRevenueCards() {
    final canSee = _data?['can_see_revenue'] == true;
    final revenue =
        canSee ? (_data?['revenue_today']?.toString() ?? '0') : "---";
    final profit = canSee ? (_data?['profit_today']?.toString() ?? '0') : "---";
    final monthRev =
        canSee ? (_data?['revenue_month']?.toString() ?? '0') : "---";

    return Column(
      children: [
        _buildLongRevenueCard('Daily Revenue', 'RWF $revenue', 'RWF $profit',
            'Profit', LucideIcons.coins, Colors.green),
        const SizedBox(height: 12),
        _buildLongRevenueCard('Monthly Revenue', 'RWF $monthRev', 'Active',
            'Status', LucideIcons.trendingUp, Colors.purple),
      ],
    );
  }

  Widget _buildLongRevenueCard(String title, String value, String subValue,
      String subTitle, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withOpacity(0.02),
              blurRadius: 15,
              offset: const Offset(0, 8))
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16)),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style:
                        TextStyle(color: Colors.grey.shade500, fontSize: 12)),
                Text(value,
                    style: const TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(subTitle,
                  style: TextStyle(color: Colors.grey.shade400, fontSize: 10)),
              Text(subValue,
                  style: TextStyle(
                      color: color, fontWeight: FontWeight.bold, fontSize: 14)),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 18, color: const Color(0xFF64748B)),
        const SizedBox(width: 8),
        Text(title,
            style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF475569))),
      ],
    );
  }

  Widget _buildSiteList() {
    final sites = _data?['site_stats'] as List? ?? [];
    return Column(
      children: sites
          .map((site) => Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFF1F5F9)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(16)),
                      child: const Icon(LucideIcons.factory,
                          color: Colors.blue, size: 20),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(site['name'],
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold, fontSize: 16)),
                          Text('${site['collected']} L Today',
                              style: TextStyle(
                                  color: Colors.blue.shade600,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500)),
                        ],
                      ),
                    ),
                    const Icon(LucideIcons.chevronRight,
                        color: Color(0xFFCBD5E1), size: 18),
                  ],
                ),
              ))
          .toList(),
    );
  }

  Widget _buildIconButton(
      {required IconData icon,
      required int count,
      required VoidCallback onTap}) {
    return Stack(
      children: [
        IconButton(
            icon: Icon(icon, size: 22, color: const Color(0xFF64748B)),
            onPressed: onTap),
        if (count > 0)
          Positioned(
            right: 8,
            top: 8,
            child: Container(
              padding: const EdgeInsets.all(2),
              decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.white, width: 2)),
              constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
              child: Text('$count',
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 8,
                      fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center),
            ),
          ),
      ],
    );
  }
}
