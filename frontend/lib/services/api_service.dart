import 'dart:convert';
import 'package:http/http.dart' as http;

/// Simple exception wrapper for API errors
class ApiException implements Exception {
  final int? statusCode;
  final String message;
  ApiException(this.message, {this.statusCode});
  @override
  String toString() => 'ApiException(statusCode: $statusCode, message: $message)';
}

class EventDto {
  final String id;
  final String name;
  final DateTime startsAt;
  final DateTime? endsAt;
  final String? location;

  EventDto({
    required this.id,
    required this.name,
    required this.startsAt,
    this.endsAt,
    this.location,
  });

  factory EventDto.fromJson(Map<String, dynamic> json) => EventDto(
        id: json['id'] as String,
        name: json['name'] as String,
        startsAt: DateTime.parse(json['starts_at'] as String),
        endsAt: json['ends_at'] != null ? DateTime.parse(json['ends_at'] as String) : null,
        location: json['location'] as String?,
      );
}

class GuestDetailIn {
  final String? name;
  final String? contact;
  final String? notes;

  GuestDetailIn({this.name, this.contact, this.notes});

  Map<String, dynamic> toJson() => {
        'name': name,
        'contact': contact,
        'notes': notes,
      }..removeWhere((_, v) => v == null || (v is String && v.isEmpty));
}

class ScanResponse {
  final bool isValid;
  final String? validationReason;
  final int guests;
  final String kind;
  final String? membershipType;
  final String? memberName;

  ScanResponse({
    required this.isValid,
    required this.guests,
    required this.kind,
    this.validationReason,
    this.membershipType,
    this.memberName,
  });

  factory ScanResponse.fromJson(Map<String, dynamic> json) => ScanResponse(
        isValid: json['is_valid'] as bool? ?? false,
        validationReason: json['validation_reason'] as String?,
        guests: json['guests'] as int? ?? 0,
        kind: json['kind'] as String? ?? 'membership_pass',
        membershipType: json['membership_type'] as String?,
        memberName: json['member_name'] as String?,
      );
}

class ApiService {
  /// Override with --dart-define=API_BASE_URL=https://your-api.com/api/v1 when building
  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  static http.Client _client = http.Client();
  static String? _accessToken;

  /// Optional: set bearer token for authenticated calls
  static void setAccessToken(String? token) {
    _accessToken = token;
  }

  static Map<String, String> _headers({Map<String, String>? extra}) {
    final headers = <String, String>{...?(extra ?? {})};
    if (_accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    return headers;
  }

// in ApiService
  static Future<Map<String, dynamic>> fetchEventStats({required String eventId}) async {
    final uri = Uri.parse('$_baseUrl/dashboard/events/$eventId/stats');
    final res = await _client.get(uri, headers: _headers());
    if (res.statusCode != 200) {
      String message = 'Failed to load dashboard';
      try {
        final body = json.decode(res.body);
        if (body is Map && body['detail'] != null) message = body['detail'].toString();
      } catch (_) {}
      throw ApiException(message, statusCode: res.statusCode);
    }
    return json.decode(res.body) as Map<String, dynamic>;
  }


  /// GET /api/v1/events?active_only=true
  static Future<List<EventDto>> fetchActiveEvents() async {
    final uri = Uri.parse('$_baseUrl/events?active_only=true');
    final res = await _client.get(uri, headers: _headers());
    if (res.statusCode != 200) {
      throw ApiException('Failed to load events', statusCode: res.statusCode);
    }
    final data = json.decode(res.body) as List<dynamic>;
    return data.map((e) => EventDto.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// POST /api/v1/scan/
  static Future<ScanResponse> submitScan({
    required String eventId,
    required String passId,
    String? passSerial,
    String? memberId,
    String scannedBy = 'unknown',
    String mode = 'in',
    String kind = 'membership_pass',
    int guests = 0,
    List<GuestDetailIn>? guestDetails,
  }) async {
    final uri = Uri.parse('$_baseUrl/scan/');
    final payload = {
      'event_id': eventId,
      'member_id': memberId,
      'pass_id': passId,
      'pass_serial': passSerial,
      'mode': mode,
      'kind': kind,
      'guests': guests,
      'scanned_by': scannedBy,
      if (guestDetails != null && guestDetails.isNotEmpty)
        'guest_details': guestDetails.map((g) => g.toJson()).toList(),
    }..removeWhere((_, v) => v == null);

    final res = await _client.post(
      uri,
      headers: _headers(extra: {'Content-Type': 'application/json'}),
      body: json.encode(payload),
    );

    if (res.statusCode != 200) {
      String message = 'Scan failed';
      try {
        final body = json.decode(res.body);
        if (body is Map && body['detail'] != null) {
          message = body['detail'].toString();
        }
      } catch (_) {
        // keep generic message
      }
      throw ApiException(message, statusCode: res.statusCode);
    }

    final body = json.decode(res.body) as Map<String, dynamic>;
    return ScanResponse.fromJson(body);
  }
}
