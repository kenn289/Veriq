"""Advanced Analysis Routes — PR analysis, maintenance, and coverage intelligence."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from veriq.api.dependencies.auth import get_current_user
from veriq.api.dependencies.db import get_session
from veriq.infrastructure.db.models import UserModel
from veriq.infrastructure.ai.agents import (
    PRAgent,
    MaintenanceAgent,
    CoverageIntelligence,
)

router = APIRouter(prefix="/advanced-analysis", tags=["advanced-analysis"])


# ====== PR Analysis Endpoints ======


class AnalyzePRRequest(BaseModel):
    """Request to analyze a pull request."""
    pr_number: int
    title: str
    diff: str
    base_branch: str = "main"


class FileChangeResponse(BaseModel):
    """A changed file in PR."""
    path: str
    change_type: str
    additions: int
    deletions: int
    risk_level: str
    affected_functions: list[str]


class AnalyzePRResponse(BaseModel):
    """Response with PR analysis."""
    pr_number: int
    title: str
    overall_risk_level: str
    files_changed: int
    total_changes: int
    affected_features: list[str]
    file_changes: list[FileChangeResponse]
    test_recommendations: list[str]
    coverage_gaps: list[str]
    breaking_changes: list[str]
    impact_summary: str


@router.post("/analyze-pr", response_model=AnalyzePRResponse)
def analyze_pr(
    request: AnalyzePRRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> AnalyzePRResponse:
    """Description: Analyze a pull request for testing requirements.
    
    Parameters:
        request: PR analysis request with diff and metadata
        session: Database session
        current_user: Authenticated user
        
    Returns:
        AnalyzePRResponse: Complete PR analysis with test recommendations
        
    Usage Example:
        POST /api/v1/advanced-analysis/analyze-pr
        {
            "pr_number": 123,
            "title": "Add login feature",
            "diff": "...",
            "base_branch": "main"
        }
    """
    agent = PRAgent()
    
    analysis = agent.analyze_pr(
        pr_number=request.pr_number,
        title=request.title,
        diff=request.diff,
        base_branch=request.base_branch,
    )
    
    return AnalyzePRResponse(
        pr_number=analysis.pr_number,
        title=analysis.title,
        overall_risk_level=analysis.overall_risk_level.value,
        files_changed=analysis.files_changed,
        total_changes=analysis.total_changes,
        affected_features=analysis.affected_features,
        file_changes=[
            FileChangeResponse(
                path=fc.path,
                change_type=fc.change_type.value,
                additions=fc.additions,
                deletions=fc.deletions,
                risk_level=fc.risk_level.value,
                affected_functions=fc.affected_functions,
            )
            for fc in analysis.file_changes
        ],
        test_recommendations=analysis.test_recommendations,
        coverage_gaps=analysis.coverage_gaps,
        breaking_changes=analysis.breaking_changes,
        impact_summary=analysis.impact_summary,
    )


# ====== Maintenance Analysis Endpoints ======


class AnalyzeTestsRequest(BaseModel):
    """Request to analyze tests for maintenance issues."""
    tests: list[dict]
    code: str


class MaintenanceIssueResponse(BaseModel):
    """A maintenance issue."""
    issue_type: str
    test_name: str
    severity: str
    description: str
    suggested_fix: str
    auto_fixable: bool


class AnalyzeTestsResponse(BaseModel):
    """Response with maintenance analysis."""
    total_tests: int
    issues_found: int
    issues: list[MaintenanceIssueResponse]
    auto_fixable_count: int
    refactoring_opportunities: list[str]
    estimated_fix_time_hours: float


@router.post("/analyze-test-maintenance", response_model=AnalyzeTestsResponse)
def analyze_test_maintenance(
    request: AnalyzeTestsRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> AnalyzeTestsResponse:
    """Description: Analyze test suite for maintenance issues.
    
    Parameters:
        request: Test suite analysis request
        session: Database session
        current_user: Authenticated user
        
    Returns:
        AnalyzeTestsResponse: Maintenance analysis with fix recommendations
        
    Usage Example:
        POST /api/v1/advanced-analysis/analyze-test-maintenance
        {
            "tests": [...],
            "code": "..."
        }
    """
    agent = MaintenanceAgent()
    
    report = agent.analyze_tests({
        "tests": request.tests,
        "code": request.code,
    })
    
    return AnalyzeTestsResponse(
        total_tests=report.total_tests,
        issues_found=report.issues_found,
        issues=[
            MaintenanceIssueResponse(
                issue_type=i.issue_type.value,
                test_name=i.test_name,
                severity=i.severity,
                description=i.description,
                suggested_fix=i.suggested_fix,
                auto_fixable=i.auto_fixable,
            )
            for i in report.issues
        ],
        auto_fixable_count=report.auto_fixable_count,
        refactoring_opportunities=report.refactoring_opportunities,
        estimated_fix_time_hours=report.estimated_fix_time_hours,
    )


# ====== Coverage Intelligence Endpoints ======


class RequirementInput(BaseModel):
    """A requirement for coverage analysis."""
    id: str
    description: str


class TestCaseInput(BaseModel):
    """A test case for coverage analysis."""
    name: str
    description: str | None = None
    scenario: str | None = None
    lines: int = 0
    duration_seconds: float = 0


class AnalyzeCoverageRequest(BaseModel):
    """Request to analyze test coverage."""
    requirements: list[RequirementInput]
    test_cases: list[TestCaseInput]


class CoverageGapResponse(BaseModel):
    """A coverage gap."""
    requirement_id: str
    requirement_description: str
    coverage_percentage: float
    tested_scenarios: list[str]
    untested_scenarios: list[str]
    risk_level: str
    priority: int


class AnalyzeCoverageResponse(BaseModel):
    """Response with coverage analysis."""
    total_requirements: int
    total_coverage_percentage: float
    fully_covered_count: int
    partially_covered_count: int
    uncovered_count: int
    coverage_gaps: list[CoverageGapResponse]
    critical_gaps: list[CoverageGapResponse]
    recommendations: list[str]
    risk_areas: list[str]


@router.post("/analyze-coverage", response_model=AnalyzeCoverageResponse)
def analyze_coverage(
    request: AnalyzeCoverageRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> AnalyzeCoverageResponse:
    """Description: Analyze test coverage against requirements.
    
    Parameters:
        request: Coverage analysis request with requirements and tests
        session: Database session
        current_user: Authenticated user
        
    Returns:
        AnalyzeCoverageResponse: Coverage analysis with gaps and recommendations
        
    Usage Example:
        POST /api/v1/advanced-analysis/analyze-coverage
        {
            "requirements": [
                {"id": "REQ-1", "description": "Users can log in"}
            ],
            "test_cases": [
                {"name": "test_login", "description": "..."}
            ]
        }
    """
    intelligence = CoverageIntelligence()
    
    analysis = intelligence.analyze_coverage(
        requirements=[{"id": r.id, "description": r.description} for r in request.requirements],
        test_cases=[
            {
                "name": t.name,
                "description": t.description or "",
                "scenario": t.scenario or "",
                "lines": t.lines,
                "duration_seconds": t.duration_seconds,
            }
            for t in request.test_cases
        ],
    )
    
    return AnalyzeCoverageResponse(
        total_requirements=analysis.total_requirements,
        total_coverage_percentage=analysis.total_coverage_percentage,
        fully_covered_count=analysis.fully_covered_count,
        partially_covered_count=analysis.partially_covered_count,
        uncovered_count=analysis.uncovered_count,
        coverage_gaps=[
            CoverageGapResponse(
                requirement_id=g.requirement_id,
                requirement_description=g.requirement_description,
                coverage_percentage=g.coverage_percentage,
                tested_scenarios=g.tested_scenarios,
                untested_scenarios=g.untested_scenarios,
                risk_level=g.risk_level,
                priority=g.priority,
            )
            for g in analysis.coverage_gaps
        ],
        critical_gaps=[
            CoverageGapResponse(
                requirement_id=g.requirement_id,
                requirement_description=g.requirement_description,
                coverage_percentage=g.coverage_percentage,
                tested_scenarios=g.tested_scenarios,
                untested_scenarios=g.untested_scenarios,
                risk_level=g.risk_level,
                priority=g.priority,
            )
            for g in analysis.critical_gaps
        ],
        recommendations=analysis.recommendations,
        risk_areas=analysis.risk_areas,
    )
