import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _checking = true;
  bool _loggingIn = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _checkExistingSession();
  }

  Future<void> _checkExistingSession() async {
    final creds = await AuthService.instance.getStoredCredentials();
    if (creds != null && mounted) {
      ApiService.setAccessToken(creds.accessToken);
      Navigator.pushReplacementNamed(context, '/scan');
      return;
    }
    if (mounted) {
      setState(() => _checking = false);
    }
  }

  Future<void> _login() async {
    setState(() {
      _loggingIn = true;
      _error = null;
    });
    try {
      final creds = await AuthService.instance.login();
      ApiService.setAccessToken(creds.accessToken);
      if (!mounted) return;
      Navigator.pushReplacementNamed(context, '/scan');
    } catch (e) {
      setState(() => _error = 'Login failed: $e');
    } finally {
      if (mounted) setState(() => _loggingIn = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Arimala Admin Login',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 16),
              if (_error != null)
                Card(
                  color: Colors.red.shade50,
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      children: [
                        const Icon(Icons.error, color: Colors.red),
                        const SizedBox(width: 8),
                        Expanded(child: Text(_error!)),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.lock_open),
                  label: Text(_loggingIn ? 'Signing in…' : 'Login with Auth0'),
                  onPressed: _loggingIn ? null : _login,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
