import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:intl/intl.dart';



void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(
    ChangeNotifierProvider(
      create: (context) => FileSelectionModel(),
      child: MyApp(),
    ),
  );
}


class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartGist',
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => HomePage(),
        '/signup': (context) => SignUpPage(),
        '/dashboard': (context) => DashboardPage(),
        '/new_project': (context) => NewProjectPage(),
        '/download_pdf': (context) => DownloadPDFPage(),
      },
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool _isPasswordVisible = false;
  TextEditingController _emailController = TextEditingController();
  TextEditingController _passwordController = TextEditingController();
  FirebaseAuth _auth = FirebaseAuth.instance;
  String _emailErrorText = '';
  String _passwordErrorText = '';
  String _loginErrorText = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text('Welcome!', style: TextStyle(color: Colors.white)),
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: Container(
          alignment: Alignment.center,
          child: SingleChildScrollView(
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  Text(
                    'SmartGist',
                    style: TextStyle(
                      fontSize: 50,
                      fontWeight: FontWeight.bold,
                      color: Colors.indigo,
                    ),
                  ),
                  SizedBox(height: 20),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 20.0),
                    child: TextField(
                      controller: _emailController,
                      decoration: InputDecoration(
                        labelText: 'Username/Email',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                        errorText: _emailErrorText.isEmpty ? null : _emailErrorText,
                      ),
                    ),
                  ),
                  SizedBox(height: 10),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 20.0),
                    child: TextField(
                      controller: _passwordController,
                      obscureText: !_isPasswordVisible,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.lock),
                        suffixIcon: IconButton(
                          icon: Icon(_isPasswordVisible ? Icons.visibility : Icons.visibility_off),
                          onPressed: () {
                            setState(() {
                              _isPasswordVisible = !_isPasswordVisible;
                            });
                          },
                        ),
                        errorText: _passwordErrorText.isEmpty ? null : _passwordErrorText,
                      ),
                    ),
                  ),
                  SizedBox(height: 20),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20.0),
                    child: SizedBox(
                      child: ElevatedButton(
                        onPressed: () {
                          _handleLogin();
                        },
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Text('Login', style: TextStyle(fontSize: 18)),
                        ),
                        style: ElevatedButton.styleFrom(
                          foregroundColor: Colors.white,
                          backgroundColor: Colors.indigo,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(height: 10),
                  Text(
                    _loginErrorText,
                    style: TextStyle(color: Colors.red),
                  ),
                  SizedBox(height: 10),
                  Text.rich(
                    TextSpan(
                      text: "Don't have an account? ",
                      style: TextStyle(color: Colors.black, fontSize: 16),
                      children: <TextSpan>[
                        TextSpan(
                          text: 'Signup',
                          style: TextStyle(color: Colors.blue, fontSize: 16),
                          recognizer: TapGestureRecognizer()
                            ..onTap = () {
                              Navigator.pushNamed(context, '/signup');
                            },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _handleLogin() async {
    print('Login button pressed');
    setState(() {
      _emailErrorText = '';
      _passwordErrorText = '';
      _loginErrorText = '';
    });

    String email = _emailController.text.trim();
    String password = _passwordController.text.trim();

    if (email.isEmpty) {
      setState(() {
        _emailErrorText = 'Enter email';
      });
      return;
    }

    if (password.isEmpty) {
      setState(() {
        _passwordErrorText = 'Enter password';
      });
      return;
    }

    try {
      UserCredential userCredential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      print('Login successful');
      Navigator.pushNamed(context, '/dashboard');
    } on FirebaseAuthException catch (e) {
      print('Login failed: ${e.message}');
      if (e.code == 'user-not-found' || e.code == 'wrong-password') {
        setState(() {
          _loginErrorText = 'Invalid email/password';
        });
      } else if (e.code == 'invalid-credential') {
          setState(() {
            _loginErrorText = 'Invalid credentials';
          });
        }
      }
    }
}


class SignUpPage extends StatefulWidget {
  @override
  _SignUpPageState createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();
  String _errorMessage = '';
  bool _passwordVisible = false; // To toggle password visibility

  Future<void> _createAccount() async {
    setState(() {
      _errorMessage = ''; // Clear any existing error message
    });

    String email = _emailController.text.trim();
    String password = _passwordController.text;
    String confirmPassword = _confirmPasswordController.text;

    if (email.isEmpty || password.isEmpty || confirmPassword.isEmpty) {
      setState(() {
        _errorMessage = 'Please fill all fields';
      });
      return;
    }

    if (password != confirmPassword) {
      setState(() {
        _errorMessage = 'Passwords do not match';
      });
      return;
    }

    try {
      UserCredential userCredential =
          await FirebaseAuth.instance.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      print('User created: ${userCredential.user}');
      Navigator.pushNamed(context, '/dashboard'); // Navigate to the next screen upon successful sign-up
    } on FirebaseAuthException catch (e) {
      if (e.code == 'email-already-in-use') {
        setState(() {
          _errorMessage = 'Email already in use';
        });
      } else {
        print('Error: ${e.message}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text('SIGN UP', style: TextStyle(color: Colors.white)),
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                Text(
                  'SmartGist',
                  style: TextStyle(
                    fontSize: 50,
                    fontWeight: FontWeight.bold,
                    color: Colors.indigo,
                  ),
                ),
                SizedBox(height: 20),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20.0),
                  child: TextField(
                    controller: _emailController,
                    decoration: InputDecoration(
                      labelText: 'Username/Email',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.person),
                    ),
                  ),
                ),
                SizedBox(height: 10),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20.0),
                  child: TextField(
                    controller: _passwordController,
                    obscureText: !_passwordVisible,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.lock),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _passwordVisible
                              ? Icons.visibility
                              : Icons.visibility_off,
                        ),
                        onPressed: () {
                          setState(() {
                            _passwordVisible = !_passwordVisible;
                          });
                        },
                      ),
                    ),
                  ),
                ),
                SizedBox(height: 10),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20.0),
                  child: TextField(
                    controller: _confirmPasswordController,
                    obscureText: !_passwordVisible,
                    decoration: InputDecoration(
                      labelText: 'Confirm Password',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.lock),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _passwordVisible
                              ? Icons.visibility
                              : Icons.visibility_off,
                        ),
                        onPressed: () {
                          setState(() {
                            _passwordVisible = !_passwordVisible;
                          });
                        },
                      ),
                    ),
                  ),
                ),
                SizedBox(height: 20),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20.0),
                  child: SizedBox(
                    child: ElevatedButton(
                      onPressed: _createAccount,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Text('Create Account', style: TextStyle(fontSize: 18)),
                      ),
                      style: ElevatedButton.styleFrom(
                        foregroundColor: Colors.white,
                        backgroundColor: Colors.indigo,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                ),
                SizedBox(height: 10),
                Text(
                  _errorMessage,
                  style: TextStyle(color: Colors.red),
                ),
                SizedBox(height: 10),
                Text.rich(
                  TextSpan(
                    text: "Already have an account? ",
                    style: TextStyle(color: Colors.black, fontSize: 16),
                    children: <TextSpan>[
                      TextSpan(
                        text: 'Login',
                        style: TextStyle(color: Colors.blue, fontSize: 16),
                        recognizer: TapGestureRecognizer()
                          ..onTap = () {
                            Navigator.pushNamed(context, '/');
                          },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class FileSelectionModel extends ChangeNotifier {
  List<String> inputPageSelectedFiles = [];
  List<String> referenceMaterialPageSelectedFiles = [];
  String inputPageTextFieldValue = '';
  String _link = '';
 
  // Getter for input page text
  String get _inputPageTextFieldValue => inputPageTextFieldValue;

  // Getter for link
  String get link => _link;
  // Getter for input page selected files
  List<String> get _inputPageSelectedFiles => inputPageSelectedFiles;

  // Getter for reference material page selected files
  List<String> get _referenceMaterialPageSelectedFiles => referenceMaterialPageSelectedFiles;

  // Method to check if input page is empty
  bool get isInputPageEmpty => inputPageTextFieldValue.isEmpty && inputPageSelectedFiles.isEmpty;

  // Method to check if reference material page is empty
  bool get isReferencePageEmpty => referenceMaterialPageSelectedFiles.isEmpty && _link.isEmpty;


  void setInputPageTextFieldValue(String value) {
    inputPageTextFieldValue = value;
    notifyListeners();
  }

  void setInputPageSelectedFiles(List<String> files) {
    inputPageSelectedFiles = files;
    print('Input Page Selected Files Updated: $inputPageSelectedFiles');
    notifyListeners();
  }

  void setLink(String value) {
    _link = value;
    notifyListeners();
  }

  void clearState() {
    inputPageSelectedFiles = [];
    referenceMaterialPageSelectedFiles = [];
    _link = '';
    inputPageTextFieldValue = '';
    notifyListeners();
  }
 

  void setReferenceMaterialPageSelectedFiles(List<String> files) {
    referenceMaterialPageSelectedFiles = files;
    print('Reference Material Page Selected Files Updated: $referenceMaterialPageSelectedFiles');
    notifyListeners();
  }

  void removeReferenceMaterialPageSelectedFile(int index) {
    referenceMaterialPageSelectedFiles.removeAt(index);
    notifyListeners();
  }
}

class PdfHistory {
  final String pdfUrl;
  final String timestamp;
  final String userId;

  PdfHistory({required this.pdfUrl, required this.timestamp, required this.userId});

  Map<String, dynamic> toMap() {
    return {
      'pdfUrl': pdfUrl,
      'timestamp': timestamp,
      'userId': userId,
    };
  }

  static PdfHistory fromMap(Map<String, dynamic> map) {
    return PdfHistory(
      pdfUrl: map['pdfUrl'],
      timestamp: map['timestamp'],
      userId: map['userId'],
    );
  }
}

class PdfHistoryStorage {
  final SharedPreferences prefs;

  PdfHistoryStorage(this.prefs);

  Future<void> addPdfToHistory(PdfHistory pdfHistory) async {
    List<String> historyList = prefs.getStringList('pdfHistory_${pdfHistory.userId}') ?? [];
    historyList.add(jsonEncode(pdfHistory.toMap()));
    await prefs.setStringList('pdfHistory_${pdfHistory.userId}', historyList);
  }

  List<PdfHistory> getPdfHistory(String userId) {
    List<String> historyList = prefs.getStringList('pdfHistory_${userId}') ?? [];
    return historyList.map((item) => PdfHistory.fromMap(jsonDecode(item))).toList();
  }

  Future<void> clearPdfHistory(String userId) async {
    await prefs.remove('pdfHistory_${userId}');
  }
}


class DashboardPage extends StatefulWidget {
  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  List<PdfHistory> _pdfHistoryList = [];
  late PdfHistoryStorage _pdfHistoryStorage;
  User? _currentUser;

  @override
  void initState() {
    super.initState();
    _loadCurrentUser();
  }

  Future<void> _loadCurrentUser() async {
    _currentUser = _auth.currentUser;
    if (_currentUser != null) {
      final prefs = await SharedPreferences.getInstance();
      _pdfHistoryStorage = PdfHistoryStorage(prefs);
      _loadPdfHistory();
    }
  }

  Future<void> _loadPdfHistory() async {
    if (_currentUser != null) {
      setState(() {
        _pdfHistoryList = _pdfHistoryStorage.getPdfHistory(_currentUser!.uid);
      });
    }
  }

  Future<void> _clearPdfHistory() async {
    if (_currentUser != null) {
      await _pdfHistoryStorage.clearPdfHistory(_currentUser!.uid);
      _loadPdfHistory();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text('Dashboard', style: TextStyle(color: Colors.white)),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: Icon(Icons.logout, color: Colors.white),
            onPressed: () async {
              try {
                await _auth.signOut();
                Provider.of<FileSelectionModel>(context, listen: false).clearState();
                Navigator.pushReplacementNamed(context, '/');
              } catch (e) {
                print('Error logging out: $e');
              }
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(height: 40),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/new_project');
              },
              style: ElevatedButton.styleFrom(
                foregroundColor: Colors.white,
                backgroundColor: Colors.indigo,
                padding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text('+ New Project', style: TextStyle(fontSize: 18)),
            ),
            SizedBox(height: 20),
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'History',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.indigo,
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: _pdfHistoryList.length,
                itemBuilder: (context, index) {
                  final pdfHistory = _pdfHistoryList[index];
                  return ListTile(
                    title: Text('PDF generated on ${DateFormat.yMMMd().format(DateTime.parse(pdfHistory.timestamp))}'),
                    subtitle: Text(pdfHistory.pdfUrl),
                    onTap: () async {
                      final url = pdfHistory.pdfUrl;
                      if (await canLaunch(url)) {
                        await launch(url);
                      } else {
                        throw 'Could not launch $url';
                      }
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}



class NewProjectPage extends StatefulWidget {
  @override
  _NewProjectPageState createState() => _NewProjectPageState();
}

class _NewProjectPageState extends State<NewProjectPage> {
  bool _showError = false;
  Future<void> removeFile2(String fileName) async {
    print("hello");
  try {
    var response = await http.delete(
      Uri.parse('http://10.0.11.154:5000/removeinputfile'),
      headers: <String, String>{
        'Content-Type': 'application/json',
      },
      body: jsonEncode(<String, String>{
        'fileName': fileName,
      }),
    );
    if (response.statusCode == 200) {
      print('File removed successfully');
    } else {
      print('Failed to remove file: ${response.reasonPhrase}');
    }
  } catch (e) {
    print('Error removing file: $e');
  }
}
  Future<void> removeFile1(String fileName) async {
    print("hello");
  try {
    var response = await http.delete(
      Uri.parse('http://10.0.11.154:5000/removefile'),
      headers: <String, String>{
        'Content-Type': 'application/json',
      },
      body: jsonEncode(<String, String>{
        'fileName': fileName,
      }),
    );
    if (response.statusCode == 200) {
      print('File removed successfully');
    } else {
      print('Failed to remove file: ${response.reasonPhrase}');
    }
  } catch (e) {
    print('Error removing file: $e');
  }
}
  Future<void> uploadFile(File pdfFile) async {
  var request = http.MultipartRequest('POST', Uri.parse('http://10.0.11.154:5000/upload'));
  request.files.add(await http.MultipartFile.fromPath('pdf', pdfFile.path));

  try {
    var response = await request.send();
    if (response.statusCode == 200) {
      print('File uploaded successfully');
    } else {
      print('Failed to upload file: ${response.reasonPhrase}');
    }
  } catch (e) {
    print('Error uploading file: $e');
  }
 }
 Future<void> uploadrefFile(File pdfFile) async {
  var request = http.MultipartRequest('POST', Uri.parse('http://10.0.11.154:5000/uploadref'));
  request.files.add(await http.MultipartFile.fromPath('pdf', pdfFile.path));

  try {
    var response = await request.send();
    if (response.statusCode == 200) {
      print('File uploaded successfully');
    } else {
      print('Failed to upload file: ${response.reasonPhrase}');
    }
  } catch (e) {
    print('Error uploading file: $e');
  }
 }
  Future<void> generatePDF() async {
    try {
  final response = await http.post(
    Uri.parse('http://10.0.11.154:5000/generate_pdf'),
    headers: <String, String>{
      'Content-Type': 'application/json',
    },
    body: jsonEncode(<String, dynamic>{
      'data': 'example data',
    }),
   
  ).catchError((error) {
    print('Error making HTTP request: $error');
  });


      // Handle the response
      if (response.statusCode == 200) {
        print('Connected to Flask server');
        final Map<String, dynamic> responseData = jsonDecode(response.body);
        final String pdfUrl = responseData['pdf_url'];
        print('PDF URL: $pdfUrl');
      } else {
        // Handle error responses
        print('Failed to connect to Flask server');
        print('Error: ${response.statusCode}');
      }
    } catch (e) {
      // Handle exceptions
      print('Exception: $e');
     
    }
  }

  @override
  Widget build(BuildContext context) {
    final fileSelectionModel = Provider.of<FileSelectionModel>(context);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text(
          'New Project',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton(
              onPressed: () {
                // Handle input button press
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => InputPage()),
                );
              },
              style: ElevatedButton.styleFrom(
                foregroundColor: Colors.white, backgroundColor: Colors.indigo,
                padding: EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text('+ Input', style: TextStyle(fontSize: 18)),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Handle reference material button press
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => ReferenceMaterialPage()),
                );
              },
              style: ElevatedButton.styleFrom(
                foregroundColor: Colors.white, backgroundColor: Colors.indigo,
                padding: EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text('+ Reference Material', style: TextStyle(fontSize: 18)),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Check if input page is empty
                if (fileSelectionModel.isInputPageEmpty ||
                    fileSelectionModel.isReferencePageEmpty) {
                  setState(() {
                    _showError = true;
                  });
                } else {
                   // Clear error message
                  setState(() {
                    _showError = false;
                  });
                  // Handle generate PDF button press
                  generatePDF();
                  Navigator.pushNamed(context, '/download_pdf');
                }
              },
              style: ElevatedButton.styleFrom(
                foregroundColor: Colors.white, backgroundColor: Colors.indigo,
                padding: EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text('Generate PDF', style: TextStyle(fontSize: 18)),
            ),
            if (_showError)
              Padding(
                padding: EdgeInsets.only(top: 10),
                child: Text(
                  'Error: Input page/Reference page is empty',
                  style: TextStyle(
                    color: Colors.red,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}



class InputPage extends StatefulWidget {
  @override
  _InputPageState createState() => _InputPageState();
}

class _InputPageState extends State<InputPage> {
  final TextEditingController _topicController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _topicController.addListener(_updateTextFieldValue);
  }

  @override
  void dispose() {
    _topicController.dispose();
    super.dispose();
  }

  void _updateTextFieldValue() {
    String fieldValue = _topicController.text;

    // Update the value in the FileSelectionModel whenever text changes
    Provider.of<FileSelectionModel>(context, listen: false)
        .setInputPageTextFieldValue(fieldValue);
   
    // Call connectToBackendServer with the updated text value
    connectToBackendServer(fieldValue);
  }

  void connectToBackendServer(String textData) async {
    try {
      final response = await http.post(
        Uri.parse('http://10.0.11.154:5000/uploadtext'), // Replace with your endpoint
        headers: <String, String>{
          'Content-Type': 'application/json',
        },
        body: jsonEncode(<String, dynamic>{
          'textData': textData,
        }),
     
    );
      print(textData);
      // Handle the response
      if (response.statusCode == 200) {
        print('Connected to backend server');
        // Process the response here if needed
      } else {
        print('Failed to connect to backend server: ${response.statusCode}');
      }
    } catch (e) {
      print('Error connecting to backend server: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    // Retrieve the text value from the FileSelectionModel
    String textFieldValue =
        Provider.of<FileSelectionModel>(context).inputPageTextFieldValue;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text('Input', style: TextStyle(color: Colors.white)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _topicController,
              decoration: InputDecoration(labelText: 'Enter topics'),
              /*onChanged: (value) {
                Provider.of<FileSelectionModel>(context, listen: false).setInputPageTextFieldValue(value);
              },*/
            ),
            SizedBox(height: 20),
            Text(
              'OR',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 18,
                color: Colors.indigo,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => _pickPDF(context),
              style: ElevatedButton.styleFrom(
                foregroundColor: Colors.white,
                backgroundColor: Colors.indigo,
                padding: EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text('+ PDF', style: TextStyle(fontSize: 18)),
            ),
            SizedBox(height: 10),
            Consumer<FileSelectionModel>(
              builder: (context, fileSelectionModel, _) {
                if (fileSelectionModel.inputPageSelectedFiles.isNotEmpty) {
                  return Column(
                    children: [
                      Row(
                        children: [
                          Text(
                            'Selected File:',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.indigo,
                            ),
                          ),
                          SizedBox(width: 5),
                          Expanded(
                            child: Row(
                              children: [
                                Text(fileSelectionModel.inputPageSelectedFiles.first),
                                IconButton(
                                  icon: Icon(Icons.close),
                                  onPressed: () => _clearSelectedFile(context),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  );
                } else {
                  return Container(); // Placeholder if no file is selected
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}

  void _clearSelectedFile(BuildContext context) {
    Provider.of<FileSelectionModel>(context, listen: false).setInputPageSelectedFiles([]);
    _NewProjectPageState obj=_NewProjectPageState();
    obj.removeFile2('example.pdf');
  }

  Future<void> _pickPDF(BuildContext context) async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        // Update the selected files in FileSelectionModel
        Provider.of<FileSelectionModel>(context, listen: false)
            .setInputPageSelectedFiles(
          [result.files.first.name ?? 'Unknown File'],
        );
        PlatformFile file = result.files.first;
        File? _selectedFile =File(file.path!);
       _selectedFile = File(result.files.single.path ?? '');
       _NewProjectPageState other = _NewProjectPageState();
       
    if (_selectedFile != null) {
  await other.uploadFile(_selectedFile);
} else {
  // Handle the case when _selectedFile is null
  print('Selected file is null');
}
      }
    } catch (e) {
      print('Error picking file: $e');
    }
  }



class ReferenceMaterialPage extends StatefulWidget {
  @override
  _ReferenceMaterialPageState createState() => _ReferenceMaterialPageState();
}

class _ReferenceMaterialPageState extends State<ReferenceMaterialPage> {
  final TextEditingController _linkController = TextEditingController();

  @override
  void initState() {
    super.initState();
    final fileSelectionModel = Provider.of<FileSelectionModel>(context, listen: false);
    _linkController.text = fileSelectionModel.link;
    _linkController.addListener(_onLinkChanged);
  }

  @override
  void dispose() {
    _linkController.dispose();
    super.dispose();
  }

  void _onLinkChanged() {
    final fileSelectionModel = Provider.of<FileSelectionModel>(context, listen: false);
    fileSelectionModel.setLink(_linkController.text);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text(
          'Reference Material',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Consumer<FileSelectionModel>(
                builder: (context, fileSelectionModel, _) {
                  return TextField(
                    decoration: InputDecoration(
                      labelText: 'Link',
                      prefixIcon: Icon(Icons.link),
                    ),
                    controller: _linkController,
                  );
                },
              ),
              SizedBox(height: 20),
              Text(
                'OR',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.indigo,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => __pickPDF(context),
                style: ElevatedButton.styleFrom(
                  foregroundColor: Colors.white,
                  backgroundColor: Colors.indigo,
                  padding: EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: Text('+ PDF', style: TextStyle(fontSize: 18)),
              ),
              SizedBox(height: 10),
              Consumer<FileSelectionModel>(
                builder: (context, fileSelectionModel, _) {
                  if (fileSelectionModel.referenceMaterialPageSelectedFiles.isNotEmpty) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Files Selected:',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo,
                          ),
                        ),
                        SizedBox(height: 5),
                        ListView.builder(
                          shrinkWrap: true,
                          itemCount: fileSelectionModel.referenceMaterialPageSelectedFiles.length,
                          itemBuilder: (context, index) {
                            return ListTile(
                              title: Text(fileSelectionModel.referenceMaterialPageSelectedFiles[index]),
                              trailing: IconButton(
                                icon: Icon(Icons.clear),
                                onPressed: () => _removeFile(index, fileSelectionModel),
                              ),
                            );
                          },
                        ),
                      ],
                    );
                  } else {
                    return Container(); // Placeholder if no file is selected
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

  Future<void> __pickPDF(BuildContext context) async {
    try {
      FileSelectionModel fileSelectionModel =Provider.of<FileSelectionModel>(context,listen:false);
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {

        // Update the selected files in FileSelectionModel
        Provider.of<FileSelectionModel>(context, listen: false)
            .setInputPageSelectedFiles(
          [result.files.first.name ?? 'Unknown File'],
        );
        PlatformFile file = result.files.first;
        File? _selectedFile =File(file.path!);
       _selectedFile = File(result.files.single.path ?? '');
       _NewProjectPageState other = _NewProjectPageState();
      List<String> newFiles=result.files.map((file)=>file.name ?? 'Unknown File').toList();
      List<String> selectedFiles=[...fileSelectionModel.referenceMaterialPageSelectedFiles, ...newFiles];
       fileSelectionModel.setReferenceMaterialPageSelectedFiles(selectedFiles);
    if (_selectedFile != null) {
  await other.uploadrefFile(_selectedFile);
} else {
  // Handle the case when _selectedFile is null
  print('Selected file is null');
}
      }
    } catch (e) {
      print('Error picking file: $e');
    }
    }

  void _removeFile(int index, FileSelectionModel fileSelectionModel) {
    String fileName = fileSelectionModel.referenceMaterialPageSelectedFiles[index];
    fileSelectionModel.removeReferenceMaterialPageSelectedFile(index);
    _NewProjectPageState obj = _NewProjectPageState();
    obj.removeFile1(fileName);
  }

 

class DownloadPDFPage extends StatefulWidget {
  @override
  _DownloadPDFPageState createState() => _DownloadPDFPageState();
}

class _DownloadPDFPageState extends State<DownloadPDFPage> {
  @override
  void initState() {
    super.initState();
    requestStoragePermission();
  }

  Future<void> requestStoragePermission() async {
    if (await Permission.storage.request().isGranted) {
      // Permission is granted
    } else {
      //permission is not granted
    }
  }

  Future<void> downloadPDF(BuildContext context) async {
  final url = 'http://10.0.11.154:5000/download_pdf'; // Replace with your server's IP address
  final user = FirebaseAuth.instance.currentUser;

  if (user == null) {
    print('User is not logged in');
    return;
  }

  final userId = user.uid;

  try {
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      final bytes = response.bodyBytes;
      final directory = await getExternalStorageDirectory();

      if (directory != null) {
        final documentsPath = directory.path;
        final filePath = '$documentsPath/downloaded.pdf';
        final file = File(filePath);
        await file.writeAsBytes(bytes);

        final timestamp = DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.now());

        final prefs = await SharedPreferences.getInstance();
        final pdfHistoryStorage = PdfHistoryStorage(prefs);
        final pdfHistory = PdfHistory(pdfUrl: file.path, timestamp: timestamp, userId: userId);

        await pdfHistoryStorage.addPdfToHistory(pdfHistory);

        Navigator.pushNamed(context, '/dashboard');
      } else {
        print('Failed to get the documents directory');
      }
    } else {
      print('Failed to download PDF: ${response.statusCode}');
    }
  } catch (e) {
    print('Error downloading PDF: $e');
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.indigo,
        title: Text('Download PDF', style: TextStyle(color: Colors.white)),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: Icon(Icons.home, color: Colors.white),
            onPressed: () {
              Provider.of<FileSelectionModel>(context, listen: false).clearState();
              Navigator.pushNamed(context, '/dashboard');
            },
          ),
        ],
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: () async {
            await downloadPDF(context);
          },
          style: ElevatedButton.styleFrom(
            foregroundColor: Colors.white,
            backgroundColor: Colors.indigo,
            padding: EdgeInsets.symmetric(vertical: 20, horizontal: 40), // Adjust padding for increased size
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: Text('Download PDF', style: TextStyle(fontSize: 20)), // Adjust font size for increased size
        ),
      ),
    );
  }
}
