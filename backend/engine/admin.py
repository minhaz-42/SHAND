"""
Django admin interface for SHAND models.
"""
from django.contrib import admin
from .models import (
    AnalysisSession,
    Assumption,
    AssumptionDependency,
    RiskAssessment,
    AnalysisReport,
    AnalysisTag,
)


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    """Admin interface for Analysis Sessions."""
    list_display = (
        'id',
        'status',
        'analysis_type',
        'total_assumptions',
        'high_risk_count',
        'created_at',
        'processing_time_display'
    )
    list_filter = ('status', 'analysis_type', 'created_at')
    search_fields = ('input_text', 'model_used')
    readonly_fields = ('created_at', 'completed_at', 'processing_time_seconds')
    
    fieldsets = (
        ('Input', {
            'fields': ('input_text', 'input_text_length')
        }),
        ('Analysis Configuration', {
            'fields': ('analysis_type', 'model_used', 'status')
        }),
        ('Results', {
            'fields': (
                'total_assumptions',
                'high_risk_count',
                'medium_risk_count',
                'low_risk_count',
                'executive_summary'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'completed_at', 'processing_time_seconds', 'error_message'),
            'classes': ('collapse',)
        })
    )
    
    def processing_time_display(self, obj):
        """Display processing time in human-readable format."""
        if obj.processing_time_seconds < 60:
            return f"{obj.processing_time_seconds:.1f}s"
        return f"{obj.processing_time_seconds / 60:.1f}m"
    processing_time_display.short_description = "Processing Time"


@admin.register(Assumption)
class AssumptionAdmin(admin.ModelAdmin):
    """Admin interface for Assumptions."""
    list_display = (
        'position_in_analysis',
        'risk_level',
        'category',
        'confidence_display',
        'session_link',
        'created_at'
    )
    list_filter = ('risk_level', 'category', 'confidence', 'created_at')
    search_fields = ('assumption_text', 'reasoning')
    readonly_fields = ('created_at', 'session')
    
    fieldsets = (
        ('Assumption Content', {
            'fields': ('session', 'assumption_text', 'reasoning', 'source_evidence')
        }),
        ('Classification', {
            'fields': ('category', 'risk_level', 'confidence', 'position_in_analysis')
        }),
        ('Impact Analysis', {
            'fields': ('what_breaks',)
        }),
        ('Metadata', {
            'fields': ('llm_generated', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def confidence_display(self, obj):
        """Display confidence as percentage."""
        return f"{obj.confidence * 100:.0f}%"
    confidence_display.short_description = "Confidence"
    
    def session_link(self, obj):
        """Link to the session."""
        return f"Session {obj.session.id}"
    session_link.short_description = "Session"


@admin.register(AssumptionDependency)
class AssumptionDependencyAdmin(admin.ModelAdmin):
    """Admin interface for Assumption Dependencies."""
    list_display = (
        'id',
        'source_assumption_preview',
        'dependency_type',
        'target_assumption_preview',
        'strength_display'
    )
    list_filter = ('dependency_type', 'strength')
    search_fields = ('source_assumption__assumption_text', 'target_assumption__assumption_text')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Relationship', {
            'fields': ('session', 'source_assumption', 'dependency_type', 'target_assumption')
        }),
        ('Details', {
            'fields': ('strength', 'explanation')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def source_assumption_preview(self, obj):
        """Preview of source assumption."""
        return obj.source_assumption.assumption_text[:50] + "..."
    source_assumption_preview.short_description = "From"
    
    def target_assumption_preview(self, obj):
        """Preview of target assumption."""
        return obj.target_assumption.assumption_text[:50] + "..."
    target_assumption_preview.short_description = "To"
    
    def strength_display(self, obj):
        """Display strength as percentage."""
        return f"{obj.strength * 100:.0f}%"
    strength_display.short_description = "Strength"


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    """Admin interface for Risk Assessments."""
    list_display = (
        'assumption_preview',
        'overall_risk_score_display',
        'likelihood_display',
        'impact_display'
    )
    list_filter = ('overall_risk_score', 'likelihood', 'impact_if_false')
    search_fields = ('assumption__assumption_text', 'mitigation_strategy')
    readonly_fields = ('created_at', 'updated_at', 'assumption')
    
    fieldsets = (
        ('Assumption', {
            'fields': ('assumption',)
        }),
        ('Risk Scores', {
            'fields': ('likelihood', 'impact_if_false', 'overall_risk_score')
        }),
        ('Mitigation', {
            'fields': ('mitigation_strategy', 'testing_recommendation')
        }),
        ('Historical Data', {
            'fields': ('similar_assumptions', 'historical_accuracy'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def assumption_preview(self, obj):
        """Preview of the assumption."""
        return obj.assumption.assumption_text[:50] + "..."
    assumption_preview.short_description = "Assumption"
    
    def overall_risk_score_display(self, obj):
        """Display overall risk score as percentage."""
        return f"{obj.overall_risk_score * 100:.0f}%"
    overall_risk_score_display.short_description = "Overall Risk"
    
    def likelihood_display(self, obj):
        """Display likelihood as percentage."""
        return f"{obj.likelihood * 100:.0f}%"
    likelihood_display.short_description = "Likelihood"
    
    def impact_display(self, obj):
        """Display impact as percentage."""
        return f"{obj.impact_if_false * 100:.0f}%"
    impact_display.short_description = "Impact"


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    """Admin interface for Analysis Reports."""
    list_display = (
        'id',
        'report_type',
        'report_format',
        'session_link',
        'file_size_display',
        'created_at'
    )
    list_filter = ('report_type', 'report_format', 'created_at')
    search_fields = ('file_name', 'content')
    readonly_fields = ('created_at', 'content')
    
    fieldsets = (
        ('Report Info', {
            'fields': ('session', 'report_type', 'report_format')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('File Storage', {
            'fields': ('file_name', 'file_path', 'file_size_bytes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def session_link(self, obj):
        """Link to the session."""
        return f"Session {obj.session.id}"
    session_link.short_description = "Session"
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        if obj.file_size_bytes < 1024:
            return f"{obj.file_size_bytes} B"
        elif obj.file_size_bytes < 1024 * 1024:
            return f"{obj.file_size_bytes / 1024:.1f} KB"
        return f"{obj.file_size_bytes / (1024 * 1024):.1f} MB"
    file_size_display.short_description = "File Size"


@admin.register(AnalysisTag)
class AnalysisTagAdmin(admin.ModelAdmin):
    """Admin interface for Analysis Tags."""
    list_display = ('name', 'session_count', 'color_display')
    search_fields = ('name', 'description')
    
    def session_count(self, obj):
        """Count sessions with this tag."""
        return obj.session.count()
    session_count.short_description = "Sessions"
    
    def color_display(self, obj):
        """Display tag color."""
        return f'<div style="background-color: {obj.color}; width: 50px; height: 20px; border-radius: 3px;"></div>'
    color_display.allow_tags = True
    color_display.short_description = "Color"
