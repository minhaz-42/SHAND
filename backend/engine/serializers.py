"""
Django REST Framework serializers for SHAND models.
"""
from rest_framework import serializers
from .models import (
    AnalysisSession,
    Assumption,
    AssumptionDependency,
    RiskAssessment,
    AnalysisReport,
    AnalysisTag,
)


class AssumptionSerializer(serializers.ModelSerializer):
    """Serializer for Assumption model."""
    class Meta:
        model = Assumption
        fields = [
            'id',
            'assumption_text',
            'reasoning',
            'category',
            'risk_level',
            'confidence',
            'what_breaks',
            'source_evidence',
            'position_in_analysis',
            'llm_generated',
            'created_at'
        ]


class RiskAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for RiskAssessment model."""
    assumption_text = serializers.CharField(source='assumption.assumption_text', read_only=True)
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id',
            'assumption_text',
            'likelihood',
            'impact_if_false',
            'overall_risk_score',
            'mitigation_strategy',
            'testing_recommendation',
            'historical_accuracy',
            'created_at'
        ]


class AssumptionDependencySerializer(serializers.ModelSerializer):
    """Serializer for AssumptionDependency model."""
    source_text = serializers.CharField(source='source_assumption.assumption_text', read_only=True)
    target_text = serializers.CharField(source='target_assumption.assumption_text', read_only=True)
    
    class Meta:
        model = AssumptionDependency
        fields = [
            'id',
            'source_assumption',
            'source_text',
            'target_assumption',
            'target_text',
            'dependency_type',
            'strength',
            'explanation',
            'created_at'
        ]


class AnalysisReportSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisReport model."""
    class Meta:
        model = AnalysisReport
        fields = [
            'id',
            'session',
            'report_type',
            'report_format',
            'file_name',
            'file_path',
            'file_size_bytes',
            'created_at'
        ]


class AnalysisTagSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisTag model."""
    class Meta:
        model = AnalysisTag
        fields = ['id', 'name', 'description', 'color']


class AnalysisSessionSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisSession model."""
    assumptions = AssumptionSerializer(many=True, read_only=True)
    tags = AnalysisTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = AnalysisSession
        fields = [
            'id',
            'input_text',
            'input_text_length',
            'status',
            'analysis_type',
            'model_used',
            'total_assumptions',
            'high_risk_count',
            'medium_risk_count',
            'low_risk_count',
            'executive_summary',
            'processing_time_seconds',
            'created_at',
            'completed_at',
            'error_message',
            'assumptions',
            'tags'
        ]
        read_only_fields = [
            'id',
            'total_assumptions',
            'high_risk_count',
            'medium_risk_count',
            'low_risk_count',
            'created_at',
            'completed_at'
        ]


class AnalysisSessionDetailSerializer(AnalysisSessionSerializer):
    """Detailed serializer for AnalysisSession with all related data."""
    assumptions = AssumptionSerializer(many=True, read_only=True)
    dependencies = AssumptionDependencySerializer(many=True, read_only=True)
    reports = AnalysisReportSerializer(many=True, read_only=True)
    
    class Meta(AnalysisSessionSerializer.Meta):
        fields = AnalysisSessionSerializer.Meta.fields + [
            'dependencies',
            'reports'
        ]
