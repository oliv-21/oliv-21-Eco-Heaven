import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:ecohaven_app/configport.dart';

class EditProfilePage extends StatefulWidget {
  final Map<String, dynamic> profileData;
  final int buyer_id;

  const EditProfilePage({
    super.key,
    required this.profileData,
    required this.buyer_id,
  });

  @override
  _EditProfilePageState createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  final _formKey = GlobalKey<FormState>();
  File? _imageFile;
  final ImagePicker _picker = ImagePicker();
  bool _isSaving = false;

  late final Map<String, TextEditingController> _controllers = {
    'Fname': TextEditingController(text: widget.profileData['Fname'] ?? ''),
    'Mname': TextEditingController(text: widget.profileData['Mname'] ?? ''),
    'Lname': TextEditingController(text: widget.profileData['Lname'] ?? ''),
    'email': TextEditingController(text: widget.profileData['email'] ?? ''),
    'mobile_number': TextEditingController(text: widget.profileData['contact_num'] ?? ''),
    'birthday': TextEditingController(text: widget.profileData['birthday'] ?? ''),
    'gender': TextEditingController(text: widget.profileData['gender'] ?? ''),
    'houseNo': TextEditingController(text: widget.profileData['houseNo'] ?? ''),
    'street': TextEditingController(text: widget.profileData['street'] ?? ''),
    'barangay': TextEditingController(text: widget.profileData['barangay'] ?? ''),
    'city': TextEditingController(text: widget.profileData['city'] ?? ''),
    'Province': TextEditingController(text: widget.profileData['Province'] ?? ''),
    'postal_code': TextEditingController(text: widget.profileData['postal_code'] ?? ''),
  };

  @override
  void dispose() {
    _controllers.values.forEach((c) => c.dispose());
    super.dispose();
  }

  Future<void> _pickImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _imageFile = File(pickedFile.path);
      });
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    String? newProfilePic;
    try {
      // 1. Update text fields
      final response = await http.post(
        Uri.parse('${Config.baseUrl}/buyer_dashboard/update_profile'),
        body: {
          'buyer_id': widget.buyer_id.toString(),
          ..._controllers.map((k, v) => MapEntry(k, v.text)),
        },
      );

      // 2. Upload image if changed
      if (_imageFile != null) {
        var request = http.MultipartRequest(
          'POST',
          Uri.parse('${Config.baseUrl}/update-profile-imagemobile'),
        );
        request.fields['buyer_id'] = widget.buyer_id.toString();
        request.files.add(
          await http.MultipartFile.fromPath(
            'image',
            _imageFile!.path,
          ),
        );
        var imgResponse = await request.send();
        if (imgResponse.statusCode == 200) {
          newProfilePic = _imageFile!.path.split('/').last;
        }
      }

      if (response.statusCode == 200) {
        final updatedProfile = {
          ...widget.profileData,
          ..._controllers.map((k, v) => MapEntry(k, v.text)),
          if (newProfilePic != null) 'profile_pic': newProfilePic,
        };
        Navigator.pop(context, updatedProfile); // Return updated data
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: ${response.body}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isSaving = false);
    }
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(top: 20, bottom: 10),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).primaryColor,
        ),
      ),
    );
  }

  Widget _buildTextField(String label, String fieldKey,
      {TextInputType keyboardType = TextInputType.text}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: TextFormField(
        controller: _controllers[fieldKey],
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          filled: true,
          fillColor: Colors.grey[100],
        ),
        validator: (value) =>
            value == null || value.isEmpty ? 'Please enter $label' : null,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Profile'),
        centerTitle: true,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 15),
            child: _isSaving
                ? const CircularProgressIndicator()
                : IconButton(
                    icon: const Icon(Icons.check, size: 30),
                    onPressed: _saveProfile,
                  ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Profile Picture Section
              Center(
                child: Stack(
                  children: [
                    CircleAvatar(
                      radius: 60,
                      backgroundImage: _imageFile != null
                          ? FileImage(_imageFile!)
                          : (widget.profileData['profile_pic'] != null &&
                                  widget.profileData['profile_pic'].toString().isNotEmpty
                              ? NetworkImage(
                                  '${Config.baseUrl}/assets/upload/${widget.profileData['profile_pic']}')
                              : const AssetImage('assets/default_profile.png')) as ImageProvider,
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.blue,
                          shape: BoxShape.circle,
                        ),
                        child: IconButton(
                          icon: Icon(Icons.camera_alt, color: Colors.white),
                          onPressed: _pickImage,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Personal Information
              _buildSectionHeader('Personal Information'),
              _buildTextField('First Name', 'Fname'),
              _buildTextField('Middle Name', 'Mname'),
              _buildTextField('Last Name', 'Lname'),
              _buildTextField('Gender', 'gender'),
              _buildTextField('Birth Date', 'birthday',
                  keyboardType: TextInputType.datetime),

              // Contact Information
              _buildSectionHeader('Contact Information'),
              _buildTextField('Email', 'email',
                  keyboardType: TextInputType.emailAddress),
              _buildTextField('Contact Number', 'mobile_number',
                  keyboardType: TextInputType.phone),

              // Address Information
              _buildSectionHeader('Address'),
              _buildTextField('House No', 'houseNo'),
              _buildTextField('Street', 'street'),
              _buildTextField('Barangay', 'barangay'),
              _buildTextField('City', 'city'),
              _buildTextField('Province', 'Province'),
              _buildTextField('Postal Code', 'postal_code',
                  keyboardType: TextInputType.number),

              const SizedBox(height: 30),

              // CHANGE PASSWORD BUTTON
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.lock_reset),
                  label: const Text('Change Password'),
                  onPressed: () async {
                    final result = await showDialog(
                      context: context,
                      builder: (ctx) => ChangePasswordDialog(buyerId: widget.buyer_id),
                    );
                    if (result == true) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Password changed successfully!')),
                      );
                    }
                  },
                ),
              ),
              const SizedBox(height: 16),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _saveProfile,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: _isSaving
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text('SAVE CHANGES'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Change Password Dialog Widget
class ChangePasswordDialog extends StatefulWidget {
  final int buyerId;
  const ChangePasswordDialog({super.key, required this.buyerId});

  @override
  State<ChangePasswordDialog> createState() => _ChangePasswordDialogState();
}

class _ChangePasswordDialogState extends State<ChangePasswordDialog> {
  final _formKey = GlobalKey<FormState>();
  final _oldPassController = TextEditingController();
  final _newPassController = TextEditingController();
  final _confirmPassController = TextEditingController();
  bool _isSubmitting = false;
  String? _error;

  @override
  void dispose() {
    _oldPassController.dispose();
    _newPassController.dispose();
    _confirmPassController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _isSubmitting = true;
      _error = null;
    });

    try {
      final response = await http.post(
        Uri.parse('${Config.baseUrl}/buyer_dashboard/change_password'),
        body: {
          'buyer_id': widget.buyerId.toString(),
          'old_password': _oldPassController.text,
          'new_password': _newPassController.text,
        },
      );
      if (response.statusCode == 200) {
        Navigator.of(context).pop(true);
      } else {
        setState(() {
          _error = 'Failed to change password: ${response.body}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error: $e';
      });
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Change Password'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),
            TextFormField(
              controller: _oldPassController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Current Password'),
              validator: (val) =>
                  val == null || val.isEmpty ? 'Enter current password' : null,
            ),
            TextFormField(
              controller: _newPassController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'New Password'),
              validator: (val) =>
                  val == null || val.length < 6 ? 'Minimum 6 characters' : null,
            ),
            TextFormField(
              controller: _confirmPassController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Confirm New Password'),
              validator: (val) =>
                  val != _newPassController.text ? 'Passwords do not match' : null,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isSubmitting ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isSubmitting ? null : _submit,
          child: _isSubmitting
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : const Text('Change'),
        ),
      ],
    );
  }
}
