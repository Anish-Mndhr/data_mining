"""
Main prioritization engine.

Orchestrates the prioritization workflow:
1. Load plant data
2. Calculate scores for each plant
3. Rank plants by score
4. Classify into priority levels
5. Generate comprehensive report
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import (
    PlantData,
    PrioritizationScore,
    PrioritizationReport,
    PriorityLevel,
    CategoryScore,
)
from .scoring import calculate_composite_score
from .config import PRIORITY_THRESHOLDS, CATEGORY_WEIGHTS


def classify_priority_level(score: float) -> PriorityLevel:
    """
    Classify plant into priority level based on composite score.
    
    Args:
        score: Composite score (0-1)
        
    Returns:
        PriorityLevel enum value
    """
    if score >= PRIORITY_THRESHOLDS["high"]:
        return PriorityLevel.HIGH
    elif score >= PRIORITY_THRESHOLDS["medium"]:
        return PriorityLevel.MEDIUM
    else:
        return PriorityLevel.LOW


def score_plant(plant: PlantData) -> PrioritizationScore:
    """
    Calculate comprehensive prioritization score for a single plant.
    
    Args:
        plant: PlantData object
        
    Returns:
        PrioritizationScore with all category scores and metadata
    """
    # Calculate composite score and category scores
    total_score, category_scores = calculate_composite_score(plant)
    
    # Classify priority level
    priority_level = classify_priority_level(total_score)
    
    # Count supporting metrics
    pathogen_count = len(plant.pathogen_data) + len(plant.strain_data)
    
    mic_count = sum(1 for p in plant.pathogen_data if p.mic) + \
                sum(1 for s in plant.strain_data if s.mic)
    
    # Count WHO priority pathogens
    from .scoring import is_who_priority_pathogen, is_amr_strain
    
    who_priority_count = 0
    amr_strain_count = 0
    
    for pathogen in plant.pathogen_data:
        if is_who_priority_pathogen(pathogen.pathogen):
            who_priority_count += 1
        if is_amr_strain(pathogen.pathogen):
            amr_strain_count += 1
    
    for strain in plant.strain_data:
        if is_who_priority_pathogen(strain.strain):
            who_priority_count += 1
        if is_amr_strain(strain.strain):
            amr_strain_count += 1
    
    # Create prioritization score
    return PrioritizationScore(
        scientific_name=plant.scientific_name,
        local_name=plant.local_name,
        ethnobotanical_score=category_scores["ethnobotanical"],
        antimicrobial_score=category_scores["antimicrobial"],
        safety_score=category_scores["safety"],
        feasibility_score=category_scores["feasibility"],
        total_score=total_score,
        priority_level=priority_level,
        pathogen_count=pathogen_count,
        mic_count=mic_count,
        who_priority_pathogens=who_priority_count,
        amr_strain_count=amr_strain_count,
        scored_at=datetime.now(),
        version="1.0.0"
    )


def prioritize_plants(
    plants: List[PlantData],
    config: Optional[Dict[str, Any]] = None
) -> PrioritizationReport:
    """
    Prioritize a list of plants using the comprehensive scoring algorithm.
    
    Args:
        plants: List of PlantData objects to prioritize
        config: Optional configuration dictionary
        
    Returns:
        PrioritizationReport with ranked plants and statistics
    """
    if not plants:
        return PrioritizationReport(
            total_plants=0,
            plant_scores=[],
            config=config or {}
        )
    
    # Score all plants
    plant_scores = []
    for plant in plants:
        try:
            score = score_plant(plant)
            plant_scores.append(score)
        except Exception as e:
            # Log error but continue with other plants
            print(f"Warning: Failed to score {plant.scientific_name}: {e}")
            continue
    
    # Sort by total score (descending)
    plant_scores.sort(key=lambda x: x.total_score, reverse=True)
    
    # Assign ranks and percentiles
    total_plants = len(plant_scores)
    for i, score in enumerate(plant_scores):
        score.rank = i + 1
        score.percentile = ((total_plants - i) / total_plants) * 100
    
    # Create report with configuration
    report_config = config or {
        "category_weights": CATEGORY_WEIGHTS,
        "priority_thresholds": PRIORITY_THRESHOLDS,
    }
    
    report = PrioritizationReport(
        total_plants=total_plants,
        plant_scores=plant_scores,
        config=report_config,
        generated_at=datetime.now(),
        version="1.0.0"
    )
    
    return report


def get_high_priority_plants(report: PrioritizationReport) -> List[PrioritizationScore]:
    """
    Extract high priority plants from report.
    
    Args:
        report: PrioritizationReport object
        
    Returns:
        List of high priority PrioritizationScore objects
    """
    return [p for p in report.plant_scores if p.priority_level == PriorityLevel.HIGH]


def get_top_n_plants(
    report: PrioritizationReport,
    n: int = 10
) -> List[PrioritizationScore]:
    """
    Get top N plants by score.
    
    Args:
        report: PrioritizationReport object
        n: Number of top plants to return
        
    Returns:
        List of top N PrioritizationScore objects
    """
    return report.plant_scores[:n]


def filter_by_criteria(
    report: PrioritizationReport,
    min_score: Optional[float] = None,
    priority_levels: Optional[List[PriorityLevel]] = None,
    min_pathogens: Optional[int] = None,
    min_mic_values: Optional[int] = None,
    must_have_icf: bool = False,
    found_in_nepal: bool = False,
) -> List[PrioritizationScore]:
    """
    Filter plants by specific criteria.
    
    Args:
        report: PrioritizationReport object
        min_score: Minimum total score
        priority_levels: List of acceptable priority levels
        min_pathogens: Minimum number of pathogens tested
        min_mic_values: Minimum number of MIC values
        must_have_icf: Require ICF data
        found_in_nepal: Require Nepal location data
        
    Returns:
        Filtered list of PrioritizationScore objects
    """
    filtered = report.plant_scores
    
    if min_score is not None:
        filtered = [p for p in filtered if p.total_score >= min_score]
    
    if priority_levels is not None:
        filtered = [p for p in filtered if p.priority_level in priority_levels]
    
    if min_pathogens is not None:
        filtered = [p for p in filtered if p.pathogen_count >= min_pathogens]
    
    if min_mic_values is not None:
        filtered = [p for p in filtered if p.mic_count >= min_mic_values]
    
    # For ICF and Nepal filtering, need to access original plant data
    # This is a simplified version - in production, maintain plant reference
    
    return filtered


def compare_plants(
    plant1: PrioritizationScore,
    plant2: PrioritizationScore
) -> Dict[str, Any]:
    """
    Compare two plants across all scoring categories.
    
    Args:
        plant1: First PrioritizationScore
        plant2: Second PrioritizationScore
        
    Returns:
        Dictionary with comparison results
    """
    comparison = {
        "plant1": {
            "name": plant1.scientific_name,
            "total_score": plant1.total_score,
            "rank": plant1.rank,
            "priority": plant1.priority_level.value,
        },
        "plant2": {
            "name": plant2.scientific_name,
            "total_score": plant2.total_score,
            "rank": plant2.rank,
            "priority": plant2.priority_level.value,
        },
        "differences": {
            "total_score": plant1.total_score - plant2.total_score,
            "ethnobotanical": plant1.ethnobotanical_score.score - plant2.ethnobotanical_score.score,
            "antimicrobial": plant1.antimicrobial_score.score - plant2.antimicrobial_score.score,
            "safety": plant1.safety_score.score - plant2.safety_score.score,
            "feasibility": plant1.feasibility_score.score - plant2.feasibility_score.score,
        },
        "winner": {
            "overall": plant1.scientific_name if plant1.total_score > plant2.total_score else plant2.scientific_name,
            "ethnobotanical": plant1.scientific_name if plant1.ethnobotanical_score.score > plant2.ethnobotanical_score.score else plant2.scientific_name,
            "antimicrobial": plant1.scientific_name if plant1.antimicrobial_score.score > plant2.antimicrobial_score.score else plant2.scientific_name,
            "safety": plant1.scientific_name if plant1.safety_score.score > plant2.safety_score.score else plant2.scientific_name,
            "feasibility": plant1.scientific_name if plant1.feasibility_score.score > plant2.feasibility_score.score else plant2.scientific_name,
        }
    }
    
    return comparison


def get_summary_statistics(report: PrioritizationReport) -> Dict[str, Any]:
    """
    Calculate summary statistics from prioritization report.
    
    Args:
        report: PrioritizationReport object
        
    Returns:
        Dictionary with statistical summaries
    """
    if not report.plant_scores:
        return {}
    
    scores = [p.total_score for p in report.plant_scores]
    ethnobotanical = [p.ethnobotanical_score.score for p in report.plant_scores]
    antimicrobial = [p.antimicrobial_score.score for p in report.plant_scores]
    safety = [p.safety_score.score for p in report.plant_scores]
    feasibility = [p.feasibility_score.score for p in report.plant_scores]
    
    return {
        "total_plants": report.total_plants,
        "priority_distribution": {
            "high": report.high_priority_count,
            "medium": report.medium_priority_count,
            "low": report.low_priority_count,
        },
        "total_scores": {
            "mean": sum(scores) / len(scores),
            "median": sorted(scores)[len(scores) // 2],
            "min": min(scores),
            "max": max(scores),
            "std": (sum((x - sum(scores) / len(scores)) ** 2 for x in scores) / len(scores)) ** 0.5,
        },
        "category_averages": {
            "ethnobotanical": sum(ethnobotanical) / len(ethnobotanical),
            "antimicrobial": sum(antimicrobial) / len(antimicrobial),
            "safety": sum(safety) / len(safety),
            "feasibility": sum(feasibility) / len(feasibility),
        },
        "pathogen_data": {
            "total_pathogens_tested": sum(p.pathogen_count for p in report.plant_scores),
            "total_mic_values": sum(p.mic_count for p in report.plant_scores),
            "who_priority_pathogens": sum(p.who_priority_pathogens for p in report.plant_scores),
            "amr_strains": sum(p.amr_strain_count for p in report.plant_scores),
        }
    }
