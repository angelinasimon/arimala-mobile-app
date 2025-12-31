import 'package:flutter/material.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';
import '../services/api_service.dart';

class ScanScreen extends StatefulWidget {
  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  QRViewController? controller;
  bool _isProcessing = false;
  List<EventDto> _events = [];
  String? _selectedEventId;
  String _scannedBy = 'unknown';
  bool _isMembership = true; // toggle between membership and event ticket

  @override
  void initState() {
    super.initState();
    _loadEvents();
  }

  Future<void> _loadEvents() async {
    try {
      final events = await ApiService.fetchActiveEvents();
      setState(() {
        _events = events;
        if (events.isNotEmpty) {
          _selectedEventId = events.first.id;
        }
      });
    } catch (e) {
      _showError('Failed to load events: $e');
    }
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  void _onQRViewCreated(QRViewController ctrl) {
    controller = ctrl;
    ctrl.scannedDataStream.listen((scanData) async {
      if (_isProcessing) return;
      final code = scanData.code;
      if (code == null) return;

      if (_selectedEventId == null) {
        _showError('Select an event before scanning.');
        return;
      }

      setState(() => _isProcessing = true);
      controller?.pauseCamera();

      try {
        final kind = _isMembership ? 'membership_pass' : 'event_ticket';

        int guests = 0;
        if (_isMembership) {
          final guestResult = await _promptGuestCount();
          if (guestResult == null) {
            controller?.resumeCamera();
            setState(() => _isProcessing = false);
            return;
          }
          guests = guestResult;
        }

        final response = await ApiService.submitScan(
          eventId: _selectedEventId!,
          passId: code, // QR encodes the PassKit pass_id
          passSerial: null, // leave null since QR is pass_id, not serial
          scannedBy: _scannedBy,
          guests: guests,
          kind: kind,
        );

        if (response.isValid) {
          final membershipLabel = response.membershipType ?? 'Ticket';
          _showSnackbar('Check-in success ($membershipLabel). Guests: ${response.guests}');
        } else {
          final reason = response.validationReason ?? 'Invalid pass';
          _showError(reason);
        }
      } on ApiException catch (e) {
        _showError(e.message);
      } catch (e) {
        _showError('Unexpected error: $e');
      } finally {
        controller?.resumeCamera();
        setState(() => _isProcessing = false);
      }
    });
  }

  Future<int?> _promptGuestCount() async {
    final controller = TextEditingController(text: '0');
    return showDialog<int>(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        title: const Text('Guests'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(hintText: 'Number of guests'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, null),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final raw = controller.text.trim();
              final parsed = int.tryParse(raw);
              if (parsed == null || parsed < 0) {
                _showError('Enter a valid guest count (0 or more).');
                return;
              }
              Navigator.pop(context, parsed);
            },
            child: const Text('Submit'),
          ),
        ],
      ),
    );
  }

  void _showSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  void _showError(String errorMessage) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Error'),
        content: Text(errorMessage),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Pass'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadEvents,
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                DropdownButtonFormField<String>(
                  value: _selectedEventId,
                  items: _events
                      .map((e) => DropdownMenuItem(
                            value: e.id,
                            child: Text(e.name),
                          ))
                      .toList(),
                  onChanged: (val) => setState(() => _selectedEventId = val),
                  decoration: const InputDecoration(
                    labelText: 'Active Event',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<bool>(
                  value: _isMembership,
                  items: const [
                    DropdownMenuItem(value: true, child: Text('Membership pass')),
                    DropdownMenuItem(value: false, child: Text('Event ticket')),
                  ],
                  onChanged: (val) => setState(() => _isMembership = val ?? true),
                  decoration: const InputDecoration(
                    labelText: 'Scan type',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  initialValue: _scannedBy,
                  decoration: const InputDecoration(
                    labelText: 'Scanned by (operator)',
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (val) => _scannedBy = val.trim().isEmpty ? 'unknown' : val.trim(),
                ),
              ],
            ),
          ),
          Expanded(
            child: QRView(
              key: qrKey,
              onQRViewCreated: _onQRViewCreated,
            ),
          ),
        ],
      ),
    );
  }
}
