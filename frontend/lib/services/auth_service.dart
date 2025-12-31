import 'package:auth0_flutter/auth0_flutter.dart';

/// Thin wrapper around Auth0 for login/logout and token storage.
class AuthService {
  AuthService._internal();
  static final AuthService instance = AuthService._internal();

  static const String domain = String.fromEnvironment('AUTH0_DOMAIN', defaultValue: 'YOUR_DOMAIN.auth0.com');
  static const String clientId = String.fromEnvironment('AUTH0_CLIENT_ID', defaultValue: 'YOUR_CLIENT_ID');
  static const String scheme = String.fromEnvironment('AUTH0_SCHEME', defaultValue: 'com.arimala.app');

  Auth0 get _auth0 => Auth0(domain, clientId);
  CredentialsManager get _credentialsManager => _auth0.credentialsManager;

  Future<Credentials?> getStoredCredentials() async {
    try {
      return await _credentialsManager.credentials();
    } catch (_) {
      return null;
    }
  }

  Future<Credentials> login() async {
    final credentials = await _auth0.webAuthentication(scheme: scheme).login();
    await _credentialsManager.storeCredentials(credentials);
    return credentials;
  }

  Future<void> logout() async {
    await _auth0.webAuthentication(scheme: scheme).logout();
    await _credentialsManager.clearCredentials();
  }
}
