import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/scan_screen.dart';
import 'screens/analytics_screen.dart';

void main() {
  runApp(MyApp()); // removed const
}

class MyApp extends StatelessWidget {
  // removed const and key for now
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Arimala Scanner',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: LoginScreen(), // no const
      routes: {
        '/scan': (context) => ScanScreen(),       // no const
        '/analytics': (context) => AnalyticsScreen(),
      },
    );
  }
}
