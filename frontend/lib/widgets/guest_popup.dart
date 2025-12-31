import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Result from the guest popup. `guests` is the number of additional people
/// accompanying the pass holder (the member is NOT included in this count).
class GuestPopupResult {
  final int guests;
  GuestPopupResult({required this.guests});
}

/// Shows a dialog to capture guest count for a membership scan.
/// Returns null if the user cancels.
/// Usage:
/// final res = await showGuestPopup(context, membershipLabel: 'Family', guestLimit: 6);
/// if (res != null) { submitScan(guests: res.guests); }
Future<GuestPopupResult?> showGuestPopup(
  BuildContext context, {
  String? membershipLabel,
  int? guestLimit,
}) {
  return showDialog<GuestPopupResult>(
    context: context,
    barrierDismissible: false,
    builder: (ctx) => _GuestPopupBody(
      membershipLabel: membershipLabel,
      guestLimit: guestLimit,
    ),
  );
}

class _GuestPopupBody extends StatefulWidget {
  final String? membershipLabel;
  final int? guestLimit;
  const _GuestPopupBody({this.membershipLabel, this.guestLimit});

  @override
  State<_GuestPopupBody> createState() => _GuestPopupBodyState();
}

class _GuestPopupBodyState extends State<_GuestPopupBody> {
  final TextEditingController _controller = TextEditingController(text: '0');
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submit() {
    final raw = _controller.text.trim();
    final parsed = int.tryParse(raw);
    if (parsed == null || parsed < 0) {
      setState(() => _error = 'Enter a valid number (0 or more).');
      return;
    }
    if (widget.guestLimit != null && parsed > widget.guestLimit!) {
      setState(() => _error = 'Maximum ${widget.guestLimit} guests allowed.');
      return;
    }
    Navigator.pop(context, GuestPopupResult(guests: parsed));
  }

  @override
  Widget build(BuildContext context) {
    final subtitle = widget.membershipLabel != null
        ? '${widget.membershipLabel} pass: guests do NOT include the pass holder.'
        : 'Guests do NOT include the pass holder.';
    return AlertDialog(
      title: const Text('Enter Guests'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(subtitle),
          if (widget.guestLimit != null)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text('Max guests: ${widget.guestLimit}', style: const TextStyle(fontSize: 12)),
            ),
          const SizedBox(height: 12),
          TextField(
            controller: _controller,
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: InputDecoration(
              labelText: 'Number of guests',
              errorText: _error,
              border: const OutlineInputBorder(),
            ),
            onSubmitted: (_) => _submit(),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, null),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _submit,
          child: const Text('Submit'),
        ),
      ],
    );
  }
}
