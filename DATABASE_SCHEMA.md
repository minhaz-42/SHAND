# SHAND Database Schema Documentation

## Overview

SHAND uses a relational PostgreSQL/SQLite database to store analysis history, detected assumptions, risk assessments, and relationships between assumptions.

## Database Models

### 1. AnalysisSession
**Purpose**: Represents a single analysis run

**Fields**:
- `id` (AutoField): Primary key
- `input_text` (TextField): Original text analyzed
- `input_text_length` (IntegerField): Word count
- `status` (CharField): pending, processing, completed, failed
- `analysis_type` (CharField): llm_local, llm_enhanced, rule_based
- `model_used` (CharField): Name of model used (e.g., "neural-chat:7b")
- `total_assumptions` (IntegerField): Count of detected assumptions
- `high_risk_count`, `medium_risk_count`, `low_risk_count` (IntegerField): Risk distribution
- `executive_summary` (TextField): Generated summary
- `created_at` (DateTimeField): When analysis was created
- `completed_at` (DateTimeField): When analysis finished
- `processing_time_seconds` (FloatField): Duration of analysis
- `error_message` (TextField): Error details if failed

**Relationships**:
- Has many: Assumption, AssumptionDependency, AnalysisReport, AnalysisTag

**Indexes**:
- created_at
- status
- analysis_type

---

### 2. Assumption
**Purpose**: Individual assumption detected in analysis

**Fields**:
- `id` (AutoField): Primary key
- `session` (ForeignKey): Link to AnalysisSession
- `assumption_text` (TextField): The assumption statement
- `reasoning` (TextField): Why this is an assumption
- `category` (CharField): behavioral, causal, economic, factual, technical, temporal, contextual, ethical
- `risk_level` (CharField): low, medium, high, critical
- `confidence` (FloatField): 0.0-1.0 confidence score
- `what_breaks` (TextField): Consequences if assumption is false
- `source_evidence` (TextField): Supporting quote from text
- `position_in_analysis` (IntegerField): Detection order (1-based)
- `llm_generated` (BooleanField): Whether from LLM vs rule-based
- `created_at` (DateTimeField): When detected

**Relationships**:
- session → AnalysisSession
- Has one: RiskAssessment
- Referenced by: AssumptionDependency (as source_assumption, target_assumption)

**Indexes**:
- (session, position_in_analysis)
- risk_level
- category

---

### 3. AssumptionDependency
**Purpose**: Tracks relationships between assumptions

**Fields**:
- `id` (AutoField): Primary key
- `session` (ForeignKey): Link to AnalysisSession
- `source_assumption` (ForeignKey): Assumption that depends on something
- `target_assumption` (ForeignKey): The assumption depended upon
- `dependency_type` (CharField): depends_on, contradicts, reinforces, related_to
- `strength` (FloatField): 0.0-1.0 relationship strength
- `explanation` (TextField): Why these are related
- `created_at` (DateTimeField): When created

**Constraints**:
- Unique together: (source_assumption, target_assumption)

**Indexes**:
- session
- dependency_type

---

### 4. RiskAssessment
**Purpose**: Detailed risk analysis for each assumption

**Fields**:
- `id` (AutoField): Primary key
- `assumption` (OneToOneField): Link to Assumption
- `likelihood` (FloatField): 0.0-1.0 probability of being incorrect
- `impact_if_false` (FloatField): 0.0-1.0 impact severity
- `overall_risk_score` (FloatField): likelihood × impact
- `mitigation_strategy` (TextField): How to validate/mitigate
- `testing_recommendation` (TextField): How to test
- `similar_assumptions` (TextField): JSON list of related assumptions
- `historical_accuracy` (FloatField): Historical accuracy rate if tracked
- `created_at` (DateTimeField): When created
- `updated_at` (DateTimeField): Last update

**Relationships**:
- assumption → Assumption (one-to-one)

---

### 5. AnalysisReport
**Purpose**: Generated reports/exports from analysis

**Fields**:
- `id` (AutoField): Primary key
- `session` (ForeignKey): Link to AnalysisSession
- `report_type` (CharField): summary, detailed, risk_analysis, etc.
- `report_format` (CharField): json, pdf, html, markdown
- `content` (TextField): Serialized report content
- `file_name` (CharField): Output filename if exported
- `file_path` (CharField): Storage path
- `file_size_bytes` (IntegerField): Report size
- `created_at` (DateTimeField): When generated

**Relationships**:
- session → AnalysisSession

---

### 6. AnalysisTag
**Purpose**: Organize and categorize analyses

**Fields**:
- `id` (AutoField): Primary key
- `name` (CharField): Tag name (unique)
- `description` (TextField): Tag description
- `color` (CharField): Hex color for UI (#3B82F6)
- `created_at` (DateTimeField): When created

**Relationships**:
- Many-to-many: AnalysisSession

---

## Schema Diagram

```
AnalysisSession (1)
    ├── (1:N) Assumption
    │         └── (1:1) RiskAssessment
    │         └── (N:M) AssumptionDependency
    ├── (1:N) AnalysisReport
    ├── (N:M) AnalysisTag
    └── (1:N) AssumptionDependency
```

---

## Usage Examples

### Save Analysis Results
```python
from engine.db_utils import save_analysis_session

session = save_analysis_session(
    input_text="Policy will reduce inequality by 30%",
    assumptions=[
        {
            'text': 'Linear causation between policy and outcome',
            'reason': 'Assumes direct causation',
            'type': 'Causal',
            'risk': 'High',
            'confidence': 0.85,
            'what_breaks': 'Policy may fail to achieve goal',
        }
    ],
    analysis_type='llm_local',
    model_used='neural-chat:7b',
    executive_summary='3 major assumptions detected',
    processing_time=45.2
)
```

### Query Analysis History
```python
from engine.db_utils import get_analysis_history

history = get_analysis_history(limit=10)
# Returns last 10 analyses with summaries
```

### Get Risk Report
```python
from engine.db_utils import get_risk_report

report = get_risk_report(session_id=42)
# Returns sorted list of risks with mitigation strategies
```

### Access from Django Shell
```bash
python manage.py shell
```

```python
from engine.models import AnalysisSession, Assumption

# Get all sessions
sessions = AnalysisSession.objects.all()

# Get high-risk assumptions
high_risk = Assumption.objects.filter(risk_level='high')

# Get assumptions from specific session
session = AnalysisSession.objects.get(id=1)
assumptions = session.assumptions.all()

# Get with relationships
session = AnalysisSession.objects.prefetch_related(
    'assumptions',
    'dependencies',
    'reports'
).get(id=1)
```

---

## Database Optimization

### Indexes
- AnalysisSession: created_at, status, analysis_type
- Assumption: (session, position), risk_level, category
- AssumptionDependency: session, dependency_type
- RiskAssessment: assumption (implicit via FK)

### Query Optimization
```python
# Use select_related for ForeignKeys
AnalysisSession.objects.select_related('model_used')

# Use prefetch_related for reverse relations
AnalysisSession.objects.prefetch_related('assumptions', 'dependencies')

# Use values_list for specific fields
Assumption.objects.filter(risk_level='high').values_list('assumption_text', flat=True)
```

---

## Migrations

### Create Migration
```bash
python manage.py makemigrations
```

### Apply Migration
```bash
python manage.py migrate
```

### Check Migration Status
```bash
python manage.py showmigrations
```

---

## Admin Interface

Access Django admin at `/admin/` after creating superuser:

```bash
python manage.py createsuperuser
```

**Available Admin Models**:
- Analysis Sessions
- Assumptions
- Assumption Dependencies
- Risk Assessments
- Analysis Reports
- Analysis Tags

---

## API Endpoints (to be implemented)

- `GET /api/analyses/` - List all analyses
- `POST /api/analyses/` - Create new analysis (stored in DB)
- `GET /api/analyses/{id}/` - Get analysis details
- `GET /api/analyses/{id}/risks/` - Get risk report
- `GET /api/assumptions/` - List all assumptions
- `GET /api/assumptions/?risk_level=high` - Filter assumptions
- `GET /api/reports/` - List reports
- `GET /api/reports/{id}/` - Download report

---

## Data Retention

Currently all data is retained indefinitely. To implement retention policies:

```python
from django.utils import timezone
from datetime import timedelta
from engine.models import AnalysisSession

# Delete analyses older than 90 days
old_date = timezone.now() - timedelta(days=90)
AnalysisSession.objects.filter(created_at__lt=old_date).delete()
```

---

## Backup & Export

### Export Entire Session
```python
from engine.serializers import AnalysisSessionDetailSerializer

session = AnalysisSession.objects.get(id=1)
serializer = AnalysisSessionDetailSerializer(session)
import json
print(json.dumps(serializer.data, indent=2))
```

### Database Backup
```bash
# SQLite
cp backend/db.sqlite3 backup_$(date +%Y%m%d).sqlite3

# PostgreSQL
pg_dump shand > backup_$(date +%Y%m%d).sql
```

---

## Performance Considerations

- Average analysis: ~45s processing time
- Database: ~1KB per assumption stored
- Typical session: 3-7 assumptions = ~5-10KB
- Annual storage (1000 analyses): ~5-10MB

---

## Future Enhancements

1. **User Accounts**: Add User model for multi-tenant support
2. **Full-Text Search**: Search assumptions by content
3. **Analytics**: Aggregate statistics dashboard
4. **Webhooks**: Notify on high-risk assumptions
5. **Versioning**: Track changes to assumptions
6. **Batch Processing**: Queue for multiple analyses
7. **Export Formats**: PDF, Excel, Word reports
