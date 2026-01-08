"""
Database models for SHAND - Assumption analysis and tracking system.

Stores analysis history, detected assumptions, risk assessments, and relationships.
"""
from django.db import models
from django.utils import timezone
import json


class AnalysisSession(models.Model):
    """
    Represents a single analysis session/run.
    """
    SESSION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    # ...existing code...
    total_claims = models.PositiveIntegerField(default=0, help_text="Total claims parsed from LLM output")
    hallucination_count = models.PositiveIntegerField(default=0, help_text="Total hallucination signals detected")
    hallucination_rate = models.FloatField(default=0.0, help_text="hallucination_rate = (unsupported + assumption + contradiction + schema_failures) / total_claims")
    
    id = models.AutoField(primary_key=True)
    input_text = models.TextField(help_text="Original text analyzed")
    input_text_length = models.IntegerField(default=0, help_text="Word count of input")
    
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='pending')
    
    # Analysis metadata
    analysis_type = models.CharField(
        max_length=50, 
        default='llm_local',
        choices=[
            ('llm_local', 'Local LLM (Ollama)'),
            ('llm_enhanced', 'Claude Enhanced'),
            ('rule_based', 'Rule-Based'),
        ]
    )
    model_used = models.CharField(max_length=100, default='neural-chat:7b')
    
    medium_risk_count = models.IntegerField(default=0)
    low_risk_count = models.IntegerField(default=0)
    
    # Executive summary
    executive_summary = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    processing_time_seconds = models.FloatField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = "engine"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['analysis_type']),
        ]
    
    def __str__(self):
        return f"Analysis {self.id} - {self.status} ({self.total_assumptions} assumptions)"



class Assumption(models.Model):
    """
    An individual assumption detected in analysis.
    """
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    CATEGORY_CHOICES = [
        ('behavioral', 'Behavioral'),
        ('causal', 'Causal Relationship'),
        ('economic', 'Economic'),
        ('factual', 'Factual'),
        ('technical', 'Technical'),
        ('temporal', 'Temporal'),
        ('contextual', 'Contextual'),
        ('ethical', 'Ethical'),
        ('other', 'Other'),
    ]
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='assumptions')
    # Core assumption data
    assumption_text = models.TextField(help_text="The actual assumption statement")
    reasoning = models.TextField(help_text="Why this is considered an assumption")
    # Classification
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='medium')
    confidence = models.FloatField(default=0.5, help_text="LLM confidence 0.0-1.0")
    # Impact analysis
    what_breaks = models.TextField(help_text="What fails if this assumption is false")
    source_evidence = models.TextField(blank=True, help_text="Quote from text supporting this assumption")
    # Tracking
    position_in_analysis = models.IntegerField(help_text="Order detected in analysis (1-based)")
    llm_generated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = "engine"
        ordering = ['position_in_analysis']
        indexes = [
            models.Index(fields=['session', 'position_in_analysis']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['category']),
        ]
    def __str__(self):
        return f"Assumption {self.position_in_analysis} - {self.risk_level.upper()}"

class HallucinationEvent(models.Model):
    """
    Tracks hallucination signals for claims in a session.
    """
    EVENT_TYPES = [
        ("unsupported", "Unsupported Claim"),
        ("assumption", "Assumption Leakage"),
        ("contradiction", "Internal Contradiction"),
        ("schema", "Schema/Validation Failure"),
        ("user_flag", "User-Flagged Issue"),
    ]
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name="hallucination_events")
    claim_id = models.CharField(max_length=64)
    event_type = models.CharField(max_length=16, choices=EVENT_TYPES)
    claim_text = models.TextField()
    confidence_level = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.event_type} | {self.claim_id} | {self.confidence_level}"


class AssumptionDependency(models.Model):
    """
    Tracks relationships between assumptions.
    E.g., Assumption A depends on Assumption B being true.
    """
    DEPENDENCY_TYPE_CHOICES = [
        ('depends_on', 'Depends On'),
        ('contradicts', 'Contradicts'),
        ('reinforces', 'Reinforces'),
        ('related_to', 'Related To'),
    ]
    
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='dependencies')
    source_assumption = models.ForeignKey(Assumption, on_delete=models.CASCADE, related_name='depends_on_assumptions')
    target_assumption = models.ForeignKey(Assumption, on_delete=models.CASCADE, related_name='depended_by_assumptions')
    
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPE_CHOICES, default='depends_on')
    strength = models.FloatField(default=0.5, help_text="Strength of relationship 0.0-1.0")
    explanation = models.TextField(blank=True, help_text="Why these assumptions are related")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "engine"
        unique_together = [['source_assumption', 'target_assumption']]
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['dependency_type']),
        ]
    
    def __str__(self):
        return f"{self.source_assumption.assumption_text[:30]} {self.dependency_type} {self.target_assumption.assumption_text[:30]}"


class RiskAssessment(models.Model):
    """
    Detailed risk analysis for an assumption.
    """
    assumption = models.OneToOneField(Assumption, on_delete=models.CASCADE, related_name='risk_assessment')
    
    # Risk scoring
    likelihood = models.FloatField(default=0.5, help_text="Likelihood of being incorrect (0.0-1.0)")
    impact_if_false = models.FloatField(default=0.5, help_text="Impact if assumption is false (0.0-1.0)")
    overall_risk_score = models.FloatField(default=0.5, help_text="Overall risk (likelihood * impact)")
    
    # Mitigation
    mitigation_strategy = models.TextField(blank=True, help_text="How to validate or mitigate risk")
    testing_recommendation = models.TextField(blank=True, help_text="How to test this assumption")
    
    # Related information
    similar_assumptions = models.TextField(blank=True, help_text="JSON list of similar assumptions from history")
    historical_accuracy = models.FloatField(blank=True, null=True, help_text="Historical accuracy rate if tracked")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = "engine"
    
    def __str__(self):
        return f"Risk Assessment - {self.overall_risk_score:.2f}"


class AnalysisReport(models.Model):
    """
    Generated reports/exports from analysis sessions.
    """
    REPORT_FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
    ]
    
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='reports')
    
    report_type = models.CharField(max_length=50, default='summary')
    report_format = models.CharField(max_length=20, choices=REPORT_FORMAT_CHOICES, default='json')
    
    # Report content
    content = models.TextField(help_text="Serialized report content")
    
    # File storage (optional)
    file_name = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size_bytes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "engine"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report_type.upper()} Report - {self.report_format}"


class AnalysisTag(models.Model):
    """
    Tags for organizing and categorizing analyses.
    """
    session = models.ManyToManyField(AnalysisSession, related_name='tags')
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color for UI display")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "engine"
    
    def __str__(self):
        return self.name


class AssumptionRecord(models.Model):
    """Legacy model - kept for backward compatibility."""
    text = models.TextField()
    type = models.CharField(max_length=50)
    risk = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "engine"