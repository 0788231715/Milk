import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';

class AddResourceScreen extends StatefulWidget {
  final String resourceType; // 'Site', 'Supplier', 'Buyer', 'Worker'
  final Map<String, dynamic>? initialData;

  const AddResourceScreen(
      {super.key, required this.resourceType, this.initialData});

  @override
  State<AddResourceScreen> createState() => _AddResourceScreenState();
}

class _AddResourceScreenState extends State<AddResourceScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _apiService = ApiService();
  final Map<String, dynamic> _formData = {};
  bool _isLoading = false;

  List<dynamic> _users = [];
  List<dynamic> _sites = [];

  @override
  void initState() {
    super.initState();
    if (widget.initialData != null) {
      _formData.addAll(widget.initialData!);
    }
    _fetchDependencies();
  }

  Future<void> _fetchDependencies() async {
    try {
      if (widget.resourceType != 'Site') {
        final users = await _apiService.getUsers();
        setState(() => _users = users);
      }
      if (widget.resourceType == 'Supplier') {
        final sites = await _apiService.getSites();
        setState(() => _sites = sites);
      }
    } catch (e) {
      debugPrint('Error fetching dependencies: $e');
    }
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();

    setState(() => _isLoading = true);
    bool success = false;

    try {
      switch (widget.resourceType) {
        case 'Site':
          success = await _apiService.createSite(_formData);
          break;
        case 'Supplier':
          success = await _apiService.createSupplier(_formData);
          break;
        case 'Buyer':
          success = await _apiService.createBuyer(_formData);
          break;
        case 'Worker':
          success = await _apiService.createWorker(_formData);
          break;
      }

      if (success && mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('${widget.resourceType} added successfully')));
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Failed to add resource. Check data.')));
      }
    } catch (e) {
      if (mounted)
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Add ${widget.resourceType}')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  if (widget.resourceType == 'Site') ...[
                    _buildTextField('name', 'Site Name', LucideIcons.mapPin),
                    const SizedBox(height: 16),
                    _buildTextField(
                        'location', 'Location', LucideIcons.navigation),
                  ],
                  if (widget.resourceType != 'Site') ...[
                    _buildDropdownField(
                        'user', 'Link User Account', _users, 'username'),
                    const SizedBox(height: 16),
                    _buildTextField('name', 'Full Name', LucideIcons.user),
                    const SizedBox(height: 16),
                    _buildTextField(
                        'contact', 'Contact Number', LucideIcons.phone),
                  ],
                  if (widget.resourceType == 'Supplier') ...[
                    const SizedBox(height: 16),
                    if (widget.initialData?['site'] != null)
                      Text(
                          'Assigning to Site ID: ${widget.initialData!['site']}',
                          style: const TextStyle(fontWeight: FontWeight.bold))
                    else
                      _buildDropdownField(
                          'site', 'Assign to Site', _sites, 'name'),
                  ],
                  if (widget.resourceType == 'Worker') ...[
                    const SizedBox(height: 16),
                    _buildTextField('role', 'Role (e.g. Driver, Clerk)',
                        LucideIcons.briefcase),
                    const SizedBox(height: 16),
                    _buildTextField(
                        'base_pay', 'Base Monthly Pay', LucideIcons.banknote,
                        isNumber: true),
                  ],
                  const SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: _submit,
                    style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16)),
                    child: const Text('Save Resource'),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildTextField(String key, String label, IconData icon,
      {bool isNumber = false}) {
    return TextFormField(
      initialValue: _formData[key]?.toString(),
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, size: 20),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
      keyboardType: isNumber ? TextInputType.number : TextInputType.text,
      validator: (value) => value == null || value.isEmpty ? 'Required' : null,
      onSaved: (value) =>
          _formData[key] = isNumber ? double.tryParse(value ?? '0') : value,
    );
  }

  Widget _buildDropdownField(
      String key, String label, List<dynamic> items, String displayKey) {
    return DropdownButtonFormField<int>(
      initialValue: _formData[key],
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
      items: items.map((item) {
        return DropdownMenuItem<int>(
          value: item['id'],
          child: Text(item[displayKey] ?? 'Unknown'),
        );
      }).toList(),
      onChanged: (value) => setState(() => _formData[key] = value),
      validator: (value) => value == null ? 'Required' : null,
    );
  }
}
