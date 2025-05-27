import 'package:ecohaven_app/auth/login_page.dart';
import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:convert';
import 'package:ecohaven_app/configport.dart';
import 'package:flutter/services.dart';

class SignupForm extends StatefulWidget {
  final String email;
  final String password;

  const SignupForm({super.key, required this.email, required this.password});

  @override
  _SignupFormState createState() => _SignupFormState();
}

class _SignupFormState extends State<SignupForm> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _firstNameController = TextEditingController();
  final TextEditingController _middleNameController = TextEditingController();
  final TextEditingController _lastNameController = TextEditingController();
  final TextEditingController _mobileNumberController = TextEditingController();
  final TextEditingController _houseNumberController = TextEditingController();
  final TextEditingController _streetController = TextEditingController();
  final TextEditingController _postalCodeController = TextEditingController();

  String? _selectedGender;
  String? _selectedMonth;
  String? _selectedDay;
  String? _selectedYear;
  File? _idImage;

  List<dynamic> provinceList = [];
  List<dynamic> cityList = [];
  List<dynamic> barangayList = [];

  String? selectedProvinceCode;
  String? selectedCityCode;
  String? selectedBarangayCode;

  @override
  void initState() {
    super.initState();
    _fetchProvinces();
  }

  Future<void> _fetchProvinces() async {
    final response = await http.get(Uri.parse('https://psgc.gitlab.io/api/provinces'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        provinceList = data;
      });
    }
  }

  Future<void> _fetchCities(String provinceCode) async {
    final response = await http.get(Uri.parse('https://psgc.gitlab.io/api/provinces/$provinceCode/municipalities'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        cityList = data;
        selectedCityCode = null;
        barangayList = [];
        selectedBarangayCode = null;
      });
    }
  }

  Future<void> _fetchBarangays(String cityCode) async {
    final response = await http.get(Uri.parse('https://psgc.gitlab.io/api/municipalities/$cityCode/barangays'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        barangayList = data;
        selectedBarangayCode = null;
      });
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    final uri = Uri.parse("${Config.baseUrl}/registerbuyer");
    final request = http.MultipartRequest("POST", uri);

    request.fields['email1'] = widget.email;
    request.fields['password'] = widget.password;
    request.fields['fname'] = _firstNameController.text;
    request.fields['Mname'] = _middleNameController.text;
    request.fields['Lname'] = _lastNameController.text;
    request.fields['number'] = _mobileNumberController.text;
    request.fields['gender'] = _selectedGender ?? "";
    request.fields['year'] = _selectedYear ?? "";
    request.fields['month'] = _selectedMonth ?? "";
    request.fields['day'] = _selectedDay ?? "";
    request.fields['houseNo'] = _houseNumberController.text;
    request.fields['street'] = _streetController.text;
    request.fields['Province'] = selectedProvinceCode ?? "";
    request.fields['city'] = selectedCityCode ?? "";
    request.fields['barangay'] = selectedBarangayCode ?? "";
    request.fields['postal'] = _postalCodeController.text;

    if (_idImage != null) {
      request.files.add(await http.MultipartFile.fromPath(
        'valid_id',
        _idImage!.path,
        contentType: MediaType('image', 'jpeg'),
      ));
    }

    try {
    final streamedResponse = await request.send();

    // Check if response is a redirect (302)
    if (streamedResponse.statusCode == 302) {
      final redirectUrl = streamedResponse.headers['location'];
      if (redirectUrl != null) {
        final uri = Uri.parse(redirectUrl);
        final errorMessage = uri.queryParameters['error'] ?? "Registered successfully. Waiting for Admin approval!"; //default registration message if error = null

        // Navigate to LoginPage and pass success or error message
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => LoginPage(errorMessage: errorMessage)),
        );
        return;
      }
    }
    // Handle other status codes if needed
    else {
      final responseBody = await streamedResponse.stream.bytesToString();
      //Show error message
      String errorMsg = "Registration failed.";
      try {
        final data = json.decode(responseBody);
        if (data['message'] != null) errorMsg = data['message'];
      } catch (_) {}
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => LoginPage(errorMessage: errorMsg)),
      );
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Network error. Please try again.')),
    );
  }
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label, {
    String? Function(String?)? validator,
    TextInputType keyboardType = TextInputType.text,
    List<TextInputFormatter>? inputFormatters,
    bool required = true,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        inputFormatters: inputFormatters,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: validator ??
            (required
                ? (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter $label';
                    }
                    return null;
                  }
                : null),
      ),
    );
  }

  Widget _buildDropdownField<T>({
    required String label,
    required T? selectedValue,
    required List<DropdownMenuItem<T>> items,
    required void Function(T?) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: DropdownButtonFormField<T>(
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        value: selectedValue,
        items: items,
        onChanged: onChanged,
        validator: (value) {
          if (value == null || (value is String && value.isEmpty)) {
            return 'Please select $label';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildImageUploadField() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Upload 1 valid ID:"),
          Row(
            children: [
              ElevatedButton(
                onPressed: _pickImage,
                child: const Text("Choose File"),
              ),
              const SizedBox(width: 10),
              _idImage != null
                  ? const Text("File Selected")
                  : const Text("No file chosen"),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _pickImage() async {
    final pickedFile = await ImagePicker().pickImage(
      source: ImageSource.gallery,
    );
    if (pickedFile != null) {
      setState(() {
        _idImage = File(pickedFile.path);
      });
    }
  }

  Widget _buildDateDropdown() {
    return Row(
      children: [
        Expanded(
          child: _buildDropdownField(
            label: "Month",
            selectedValue: _selectedMonth,
            items: List.generate(12, (i) => "${i + 1}")
                .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                .toList(),
            onChanged: (val) => setState(() => _selectedMonth = val),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildDropdownField(
            label: "Day",
            selectedValue: _selectedDay,
            items: List.generate(31, (i) => "${i + 1}")
                .map((d) => DropdownMenuItem(value: d, child: Text(d)))
                .toList(),
            onChanged: (val) => setState(() => _selectedDay = val),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildDropdownField(
            label: "Year",
            selectedValue: _selectedYear,
            items: List.generate(100, (i) => "${2025 - i}")
                .map((y) => DropdownMenuItem(value: y, child: Text(y)))
                .toList(),
            onChanged: (val) => setState(() => _selectedYear = val),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Sign Up Form", style: TextStyle(color: Color(0xFF133056), fontWeight: FontWeight.bold)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              _buildTextField(_firstNameController, "First Name"),
              _buildTextField(_middleNameController, "Middle Name"),
              _buildTextField(_lastNameController, "Last Name"),
              _buildDropdownField(
                label: "Gender",
                selectedValue: _selectedGender,
                items: ["Male", "Female", "Prefer not to say"]
                    .map((g) => DropdownMenuItem(value: g, child: Text(g)))
                    .toList(),
                onChanged: (val) => setState(() => _selectedGender = val),
              ),
              _buildDateDropdown(),
              _buildTextField(
                _mobileNumberController,
                "Mobile Number",
                keyboardType: TextInputType.phone,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(11),
                ],
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter Mobile Number';
                  }
                  if (!RegExp(r'^09\d{9}$').hasMatch(value)) {
                    return 'Mobile Number must be 11 digits and start with 09';
                  }
                  return null;
                },
              ),
              _buildImageUploadField(),
              const SizedBox(height: 10),
              _buildTextField(
                _houseNumberController,
                "House Number",
                required: false,
              ),
              _buildTextField(_streetController, "Street"),
              _buildDropdownField(
                label: "Province",
                selectedValue: selectedProvinceCode,
                items: provinceList.map<DropdownMenuItem<String>>((p) {
                  return DropdownMenuItem(
                    value: p['code'],
                    child: Text(p['name']),
                  );
                }).toList(),
                onChanged: (val) {
                  setState(() {
                    selectedProvinceCode = val;
                    _fetchCities(val!);
                  });
                },
              ),
              _buildDropdownField(
                label: "City/Municipality",
                selectedValue: selectedCityCode,
                items: cityList.map<DropdownMenuItem<String>>((c) {
                  return DropdownMenuItem(
                    value: c['code'],
                    child: Text(c['name']),
                  );
                }).toList(),
                onChanged: (val) {
                  setState(() {
                    selectedCityCode = val;
                    _fetchBarangays(val!);
                  });
                },
              ),
              _buildDropdownField(
                label: "Barangay",
                selectedValue: selectedBarangayCode,
                items: barangayList.map<DropdownMenuItem<String>>((b) {
                  return DropdownMenuItem(
                    value: b['code'],
                    child: Text(b['name']),
                  );
                }).toList(),
                onChanged: (val) => setState(() => selectedBarangayCode = val),
              ),
              _buildTextField(
                _postalCodeController,
                "Postal Code",
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(10),
                ],
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter Postal Code';
                  }
                  if (!RegExp(r'^\d+$').hasMatch(value)) {
                    return 'Postal Code must be numbers only';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _submitForm,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF133056),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: const Text("Submit", style: TextStyle(color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
