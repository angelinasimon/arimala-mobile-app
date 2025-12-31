import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DashboardSummary {
  final int totalCheckIns; // number of passes scanned (mode=in)
  final int totalGuests;   // guests associated with those scans
  final List<MembershipStat> membershipStats;
  final List<ArrivalBucket> arrivals;

  DashboardSummary({
    required this.totalCheckIns,
    required this.totalGuests,
    required this.membershipStats,
    required this.arrivals,
  });

  factory DashboardSummary.fromJson(Map<String, dynamic> json) {
    final byType = json['by_membership_type'] as Map<String, dynamic>? ?? {};
    final stats = byType.entries.map((e) {
      final value = e.value as Map<String, dynamic>? ?? {};
      return MembershipStat(
        type: e.key,
        members: (value['members'] as int?) ?? 0,
        guests: (value['guests'] as int?) ?? 0,
      );
    }).toList()
      ..sort((a, b) => a.type.compareTo(b.type));

    final arrivalsJson = json['arrivals'] as List<dynamic>? ?? [];
    final arrivals = arrivalsJson
        .map((e) => ArrivalBucket.fromJson(e as Map<String, dynamic>))
        .toList()
      ..sort((a, b) => a.time.compareTo(b.time));

    return DashboardSummary(
      totalCheckIns: (json['total_check_ins'] as int?) ?? 0,
      totalGuests: (json['total_guests'] as int?) ?? 0,
      membershipStats: stats,
      arrivals: arrivals,
    );
  }
}

class MembershipStat {
  final String type;
  final int members;
  final int guests;
  MembershipStat({
    required this.type,
    required this.members,
    required this.guests,
  });
}

class ArrivalBucket {
  final DateTime time;
  final int checkIns;
  final int guests;

  ArrivalBucket({
    required this.time,
    required this.checkIns,
    required this.guests,
  });

  int get totalArrivals => checkIns + guests;

  factory ArrivalBucket.fromJson(Map<String, dynamic> json) => ArrivalBucket(
        time: DateTime.parse(json['time'] as String),
        checkIns: (json['check_ins'] as int?) ?? 0,
        guests: (json['guests'] as int?) ?? 0,
      );
}

class AnalyticsScreen extends StatefulWidget {
  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  bool _loadingEvents = true;
  bool _loadingSummary = false;
  String? _error;
  List<EventDto> _events = [];
  String? _selectedEventId;
  DashboardSummary? _summary;

  @override
  void initState() {
    super.initState();
    _loadEvents();
  }

  Future<void> _loadEvents() async {
    setState(() {
      _loadingEvents = true;
      _error = null;
    });
    try {
      final events = await ApiService.fetchActiveEvents();
      setState(() {
        _events = events;
        _selectedEventId = events.isNotEmpty ? events.first.id : null;
      });
      if (_selectedEventId != null) {
        await _loadSummary();
      }
    } catch (e) {
      setState(() {
        _error = 'Failed to load events: $e';
      });
    } finally {
      setState(() {
        _loadingEvents = false;
      });
    }
  }

  Future<void> _loadSummary() async {
    if (_selectedEventId == null) return;
    setState(() {
      _loadingSummary = true;
      _error = null;
    });
    try {
      final data = await ApiService.fetchEventStats(eventId: _selectedEventId!);
      setState(() => _summary = DashboardSummary.fromJson(data));
    } catch (e) {
      setState(() {
        _error = 'Failed to load dashboard: $e';
        _summary = null;
      });
    } finally {
      setState(() => _loadingSummary = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalPeople = (_summary?.totalCheckIns ?? 0) + (_summary?.totalGuests ?? 0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analytics'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadingSummary ? null : _loadSummary,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: _loadingEvents
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _selectedEventId,
                          items: _events
                              .map((e) => DropdownMenuItem(
                                    value: e.id,
                                    child: Text(e.name),
                                  ))
                              .toList(),
                          onChanged: (val) async {
                            setState(() {
                              _selectedEventId = val;
                              _summary = null;
                            });
                            await _loadSummary();
                          },
                          decoration: const InputDecoration(
                            labelText: 'Event',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  if (_error != null)
                    Card(
                      color: Colors.red.shade50,
                      child: ListTile(
                        leading: const Icon(Icons.error, color: Colors.red),
                        title: Text(_error!),
                        trailing: TextButton(
                          onPressed: () {
                            if (_events.isEmpty) {
                              _loadEvents();
                            } else {
                              _loadSummary();
                            }
                          },
                          child: const Text('Retry'),
                        ),
                      ),
                    ),
                  if (_loadingSummary)
                    const Expanded(child: Center(child: CircularProgressIndicator()))
                  else if (_summary == null)
                    Expanded(
                      child: Center(
                        child: Text(
                          _selectedEventId == null
                              ? 'No active events found.'
                              : 'No data yet for this event.',
                        ),
                      ),
                    )
                  else
                    Expanded(
                      child: ListView(
                        children: [
                          _StatCard(
                            label: 'Total people (passes + guests)',
                            value: totalPeople.toString(),
                          ),
                          Row(
                            children: [
                              Expanded(
                                child: _StatCard(
                                  label: 'Passes scanned',
                                  value: _summary!.totalCheckIns.toString(),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _StatCard(
                                  label: 'Guests',
                                  value: _summary!.totalGuests.toString(),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          _ArrivalChart(arrivals: _summary!.arrivals),
                          const SizedBox(height: 12),
                          Text(
                            'By membership type',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          ..._summary!.membershipStats.map(
                            (stat) => Card(
                              child: ListTile(
                                title: Text(stat.type),
                                subtitle: Text('Members: ${stat.members}'),
                                trailing: Text('Guests: ${stat.guests}'),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  const _StatCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 4),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}

class _ArrivalChart extends StatelessWidget {
  final List<ArrivalBucket> arrivals;
  const _ArrivalChart({required this.arrivals});

  List<charts.Series<ArrivalBucket, DateTime>> _buildSeries() {
    return [
      charts.Series<ArrivalBucket, DateTime>(
        id: 'Arrivals',
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (ArrivalBucket point, _) => point.time,
        measureFn: (ArrivalBucket point, _) => point.totalArrivals,
        data: arrivals,
      )
    ];
  }

  @override
  Widget build(BuildContext context) {
    if (arrivals.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'No arrivals yet',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Arrivals over time',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 240,
              child: charts.TimeSeriesChart(
                _buildSeries(),
                animate: true,
                defaultRenderer: charts.LineRendererConfig(includePoints: true),
                dateTimeFactory: const charts.LocalDateTimeFactory(),
                primaryMeasureAxis: const charts.NumericAxisSpec(),
                domainAxis: const charts.DateTimeAxisSpec(),
                behaviors: [
                  charts.SeriesLegend(position: charts.BehaviorPosition.bottom),
                  charts.ChartTitle(
                    'Time',
                    behaviorPosition: charts.BehaviorPosition.bottom,
                    titleOutsideJustification: charts.OutsideJustification.middleDrawArea,
                  ),
                  charts.ChartTitle(
                    'People',
                    behaviorPosition: charts.BehaviorPosition.start,
                    titleOutsideJustification: charts.OutsideJustification.middleDrawArea,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
