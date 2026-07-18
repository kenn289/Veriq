"""Analysis and Healing Routes — failure analysis, self-healing, and codebase analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from veriq.api.dependencies.auth import get_current_user
from veriq.api.dependencies.db import get_session
from veriq.infrastructure.db.models import UserModel
from veriq.infrastructure.analysis import (
    FailureAnalyzer,
    FailureAnalysis,
    FailureSeverity,
    RootCauseType,
    CodebaseAnalyzer,
    CodebaseAnalysis,
)
from veriq.infrastructure.healing import (
    LocatorHealer,
    HealingResult,
    FlakyTestDetector,
)

router = APIRouter(prefix="/analysis", tags=["analysis", "healing"])


# ====== Failure Analysis Endpoints ======


class FailureAnalysisRequest(BaseModel):
    """Request for failure analysis."""
    test_name: str
    error_message: str
    stack_trace: str | None = None
    screenshot: str | None = None
    dom_snapshot: str | None = None


class FailureAnalysisResponse(BaseModel):
    """Response with failure analysis."""
    test_name: str
    severity: str
    root_cause_type: str
    root_cause_description: str
    recommendations: list[str]
    confidence_score: float
    affected_features: list[str]


@router.post("/analyze-failure", response_model=FailureAnalysisResponse)
def analyze_failure(
    request: FailureAnalysisRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> FailureAnalysisResponse:
    """Description: Analyze a test failure and get root cause analysis.
    
    Parameters:
        request: Failure analysis request with error details
        session: Database session
        current_user: Authenticated user
        
    Returns:
        FailureAnalysisResponse: Detailed failure analysis
        
    Usage Example:
        POST /api/v1/analysis/analyze-failure
        {
            "test_name": "test_login",
            "error_message": "Timeout waiting for element with selector '.login-btn'",
            "stack_trace": "..."
        }
    """
    analyzer = FailureAnalyzer()
    
    analysis = analyzer.analyze_failure(
        test_name=request.test_name,
        error_message=request.error_message,
        stack_trace=request.stack_trace,
        screenshot=request.screenshot,
        dom_snapshot=request.dom_snapshot,
    )
    
    return FailureAnalysisResponse(
        test_name=analysis.test_name,
        severity=analysis.severity.value,
        root_cause_type=analysis.root_cause_type.value,
        root_cause_description=analysis.root_cause_description,
        recommendations=analysis.recommendations,
        confidence_score=analysis.confidence_score,
        affected_features=analysis.affected_features,
    )


# ====== Locator Healing Endpoints ======


class HealLocatorRequest(BaseModel):
    """Request to heal a broken locator."""
    broken_locator: str
    dom_snapshot: str | None = None
    previous_locators: list[str] | None = None


class HealingStrategyResponse(BaseModel):
    """A healing strategy."""
    strategy_type: str
    suggested_locator: str
    confidence_score: float
    reasoning: str


class HealLocatorResponse(BaseModel):
    """Response with healing strategies."""
    broken_locator: str
    strategies: list[HealingStrategyResponse]
    best_strategy: HealingStrategyResponse | None


@router.post("/heal-locator", response_model=HealLocatorResponse)
def heal_locator(
    request: HealLocatorRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> HealLocatorResponse:
    """Description: Heal a broken locator using multiple strategies.
    
    Parameters:
        request: Locator healing request
        session: Database session
        current_user: Authenticated user
        
    Returns:
        HealLocatorResponse: Healing strategies and recommendations
        
    Usage Example:
        POST /api/v1/analysis/heal-locator
        {
            "broken_locator": "//*[@id='old-login-button']",
            "previous_locators": ["//*[@id='login-btn']"],
            "dom_snapshot": "..."
        }
    """
    healer = LocatorHealer()
    
    result = healer.heal_locator(
        broken_locator=request.broken_locator,
        dom_snapshot=request.dom_snapshot,
        previous_locators=request.previous_locators,
    )
    
    return HealLocatorResponse(
        broken_locator=result.broken_locator,
        strategies=[
            HealingStrategyResponse(
                strategy_type=s.strategy_type,
                suggested_locator=s.suggested_locator,
                confidence_score=s.confidence_score,
                reasoning=s.reasoning,
            )
            for s in result.strategies
        ],
        best_strategy=(
            HealingStrategyResponse(
                strategy_type=result.best_strategy.strategy_type,
                suggested_locator=result.best_strategy.suggested_locator,
                confidence_score=result.best_strategy.confidence_score,
                reasoning=result.best_strategy.reasoning,
            )
            if result.best_strategy
            else None
        ),
    )


# ====== Flakiness Detection Endpoints ======


class DetectFlakinessRequest(BaseModel):
    """Request to detect flaky tests."""
    test_results: list[dict]
    pass_threshold: float = 0.8


class FlakyTestResponse(BaseModel):
    """Information about a flaky test."""
    test_name: str
    pass_rate: float
    runs: int
    failures: int
    flakiness_score: float
    recommendation: str


class DetectFlakinessResponse(BaseModel):
    """Response with flaky test detection."""
    flaky_tests: list[FlakyTestResponse]


@router.post("/detect-flakiness", response_model=DetectFlakinessResponse)
def detect_flakiness(
    request: DetectFlakinessRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> DetectFlakinessResponse:
    """Description: Detect flaky tests from historical results.
    
    Parameters:
        request: Test results history
        session: Database session
        current_user: Authenticated user
        
    Returns:
        DetectFlakinessResponse: List of detected flaky tests
    """
    detector = FlakyTestDetector()
    
    flaky_tests = detector.detect_flakiness(
        test_results=request.test_results,
        pass_threshold=request.pass_threshold,
    )
    
    return DetectFlakinessResponse(
        flaky_tests=[
            FlakyTestResponse(
                test_name=t["test_name"],
                pass_rate=t["pass_rate"],
                runs=t["runs"],
                failures=t["failures"],
                flakiness_score=t["flakiness_score"],
                recommendation=t["recommendation"],
            )
            for t in flaky_tests
        ]
    )


# ====== Codebase Analysis Endpoints ======


class CodeFileInput(BaseModel):
    """A code file for analysis."""
    name: str
    content: str


class AnalyzeCodebaseRequest(BaseModel):
    """Request to analyze codebase."""
    code_files: list[CodeFileInput]


class TestPatternResponse(BaseModel):
    """A test pattern."""
    name: str
    description: str
    count: int
    frequency: float


class AnalyzeCodebaseResponse(BaseModel):
    """Response with codebase analysis."""
    language: str
    framework: str
    total_tests: int
    test_patterns: list[TestPatternResponse]
    locator_strategies: dict
    assertion_patterns: dict
    setup_teardown_patterns: list[str]
    common_helpers: list[str]
    recommendations: list[str]


@router.post("/analyze-codebase", response_model=AnalyzeCodebaseResponse)
def analyze_codebase(
    request: AnalyzeCodebaseRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> AnalyzeCodebaseResponse:
    """Description: Analyze existing test codebase to extract patterns.
    
    Parameters:
        request: Code files to analyze
        session: Database session
        current_user: Authenticated user
        
    Returns:
        AnalyzeCodebaseResponse: Codebase analysis and recommendations
        
    Usage Example:
        POST /api/v1/analysis/analyze-codebase
        {
            "code_files": [
                {
                    "name": "test_login.py",
                    "content": "def test_user_login(): ..."
                }
            ]
        }
    """
    analyzer = CodebaseAnalyzer()
    
    analysis = analyzer.analyze_codebase(
        code_files=[{"name": f.name, "content": f.content} for f in request.code_files]
    )
    
    return AnalyzeCodebaseResponse(
        language=analysis.language,
        framework=analysis.framework,
        total_tests=analysis.total_tests,
        test_patterns=[
            TestPatternResponse(
                name=p.name,
                description=p.description,
                count=p.count,
                frequency=p.frequency,
            )
            for p in analysis.test_patterns
        ],
        locator_strategies=analysis.locator_strategies,
        assertion_patterns=analysis.assertion_patterns,
        setup_teardown_patterns=analysis.setup_teardown_patterns,
        common_helpers=analysis.common_helpers,
        recommendations=analysis.recommendations,
    )
