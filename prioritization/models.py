"""
Data models for the plant prioritization system.

Defines Pydantic models for plant data, pathogen data, scoring results,
and prioritization outputs with comprehensive validation.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority classification levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PathogenData(BaseModel):
    """Data for a single pathogen tested against a plant."""
    pathogen: str = Field(..., description="Pathogen name (e.g., 'Staphylococcus aureus')")
    mic: Optional[str] = Field(None, description="Minimum Inhibitory Concentration (with units)")
    mbc: Optional[str] = Field(None, description="Minimum Bactericidal Concentration (with units)")
    zoi: Optional[str] = Field(None, description="Zone of Inhibition (with units)")
    assay_type: Optional[str] = Field(None, description="Assay method used")
    extraction: Optional[str] = Field(None, description="Extraction solvent")
    preparation: Optional[str] = Field(None, description="Preparation method")
    source_url: Optional[str] = Field(None, description="Citation URL")
    
    # Parsed numeric values (populated during processing)
    mic_value: Optional[float] = Field(None, description="Parsed MIC value in μg/mL")
    mbc_value: Optional[float] = Field(None, description="Parsed MBC value in μg/mL")
    zoi_value: Optional[float] = Field(None, description="Parsed ZOI value in mm")
    
    @field_validator('pathogen')
    @classmethod
    def validate_pathogen(cls, v: str) -> str:
        """Ensure pathogen name is not empty."""
        if not v or not v.strip():
            raise ValueError("Pathogen name cannot be empty")
        return v.strip()


class StrainData(BaseModel):
    """Data for bacterial strain with MIC/MBC values."""
    strain: str = Field(..., description="Bacterial strain name")
    mic: Optional[str] = Field(None, description="MIC value with units")
    mbc: Optional[str] = Field(None, description="MBC value with units")
    
    # Parsed numeric values
    mic_value: Optional[float] = Field(None, description="Parsed MIC value in μg/mL")
    mbc_value: Optional[float] = Field(None, description="Parsed MBC value in μg/mL")


class PlantData(BaseModel):
    """Comprehensive plant data for prioritization."""
    
    # Basic identification
    scientific_name: str = Field(..., description="Scientific name of the plant")
    local_name: Optional[str] = Field(None, description="Local/common name")
    family: Optional[str] = Field(None, description="Plant family")
    genus: Optional[str] = Field(None, description="Plant genus")
    
    # Ethnobotanical data
    traditional_usage: Optional[str] = Field(None, description="Traditional medicinal uses")
    cultural_consensus_icf: Optional[float] = Field(None, ge=0, le=1, description="ICF value (0-1)")
    location_found_nepal: Optional[str] = Field(None, description="Locations in Nepal")
    growth_form: Optional[str] = Field(None, description="Growth form (herb, shrub, tree)")
    altitude_range_found: Optional[str] = Field(None, description="Altitude range")
    
    # Preparation and extraction
    preparation_solvent: Optional[str] = Field(None, description="Preparation solvent")
    preparation_method: Optional[str] = Field(None, description="Preparation method")
    extraction_solvent: Optional[str] = Field(None, description="Extraction solvent")
    compound_class: Optional[str] = Field(None, description="Active compound classes")
    parts_with_amr: Optional[str] = Field(None, description="Plant parts with AMR activity")
    parts_used: Optional[str] = Field(None, description="Parts traditionally used")
    
    # Antimicrobial data
    pathogen_data: List[PathogenData] = Field(default_factory=list, description="Pathogen test results")
    strain_data: List[StrainData] = Field(default_factory=list, description="Strain-specific data")
    antibacterial_properties: Optional[str] = Field(None, description="General antibacterial properties")
    amr_properties: Optional[str] = Field(None, description="AMR-specific properties")
    
    # Research metadata
    research_paper_title: Optional[str] = Field(None, description="Research paper title")
    authors: Optional[str] = Field(None, description="Authors")
    journal_info: Optional[str] = Field(None, description="Journal and publication info")
    url: Optional[str] = Field(None, description="Research URL")
    
    # Database fields
    sn: Optional[int] = Field(None, description="Serial number in database")
    
    @field_validator('scientific_name')
    @classmethod
    def validate_scientific_name(cls, v: str) -> str:
        """Ensure scientific name is not empty."""
        if not v or not v.strip():
            raise ValueError("Scientific name cannot be empty")
        return v.strip()
    
    @field_validator('cultural_consensus_icf')
    @classmethod
    def validate_icf(cls, v: Optional[float]) -> Optional[float]:
        """Validate ICF is between 0 and 1."""
        if v is not None and (v < 0 or v > 1):
            raise ValueError("ICF must be between 0 and 1")
        return v


class CategoryScore(BaseModel):
    """Score for a single category."""
    category: str = Field(..., description="Category name")
    score: float = Field(..., ge=0, le=1, description="Category score (0-1)")
    weight: float = Field(..., ge=0, le=1, description="Category weight")
    weighted_score: float = Field(..., description="Score * weight")
    details: Dict[str, Any] = Field(default_factory=dict, description="Sub-scores and details")
    justification: str = Field(default="", description="Explanation for the score")


class PrioritizationScore(BaseModel):
    """Complete prioritization scoring for a plant."""
    
    # Plant identification
    scientific_name: str = Field(..., description="Plant scientific name")
    local_name: Optional[str] = Field(None, description="Local name")
    
    # Category scores
    ethnobotanical_score: CategoryScore = Field(..., description="Ethnobotanical validation score")
    antimicrobial_score: CategoryScore = Field(..., description="Antimicrobial efficacy score")
    safety_score: CategoryScore = Field(..., description="Safety profile score")
    feasibility_score: CategoryScore = Field(..., description="Research feasibility score")
    
    # Composite score
    total_score: float = Field(..., ge=0, le=1, description="Total weighted score (0-1)")
    priority_level: PriorityLevel = Field(..., description="Priority classification")
    
    # Ranking
    rank: Optional[int] = Field(None, description="Rank among all plants")
    percentile: Optional[float] = Field(None, ge=0, le=100, description="Percentile ranking")
    
    # Supporting data
    pathogen_count: int = Field(default=0, description="Number of pathogens tested")
    mic_count: int = Field(default=0, description="Number of MIC values available")
    who_priority_pathogens: int = Field(default=0, description="Count of WHO priority pathogens")
    amr_strain_count: int = Field(default=0, description="Count of AMR strains tested")
    
    # Metadata
    scored_at: datetime = Field(default_factory=datetime.now, description="Scoring timestamp")
    version: str = Field(default="1.0.0", description="Algorithm version")
    
    @property
    def category_scores(self) -> List[CategoryScore]:
        """Get all category scores as a list."""
        return [
            self.ethnobotanical_score,
            self.antimicrobial_score,
            self.safety_score,
            self.feasibility_score,
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "scientific_name": self.scientific_name,
            "local_name": self.local_name,
            "total_score": round(self.total_score, 3),
            "priority_level": self.priority_level.value,
            "rank": self.rank,
            "percentile": round(self.percentile, 1) if self.percentile else None,
            "ethnobotanical_score": round(self.ethnobotanical_score.score, 3),
            "antimicrobial_score": round(self.antimicrobial_score.score, 3),
            "safety_score": round(self.safety_score.score, 3),
            "feasibility_score": round(self.feasibility_score.score, 3),
            "pathogen_count": self.pathogen_count,
            "mic_count": self.mic_count,
            "who_priority_pathogens": self.who_priority_pathogens,
            "amr_strain_count": self.amr_strain_count,
        }


class PrioritizationReport(BaseModel):
    """Complete prioritization report for all plants."""
    
    # Report metadata
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation time")
    total_plants: int = Field(..., description="Total plants analyzed")
    version: str = Field(default="1.0.0", description="Algorithm version")
    
    # Results
    plant_scores: List[PrioritizationScore] = Field(..., description="All plant scores, ranked")
    
    # Summary statistics
    high_priority_count: int = Field(default=0, description="Count of high priority plants")
    medium_priority_count: int = Field(default=0, description="Count of medium priority plants")
    low_priority_count: int = Field(default=0, description="Count of low priority plants")
    
    average_score: float = Field(default=0.0, description="Average total score")
    median_score: float = Field(default=0.0, description="Median total score")
    
    # Configuration used
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration used for scoring")
    
    @model_validator(mode='after')
    def calculate_statistics(self):
        """Calculate summary statistics from plant scores."""
        if self.plant_scores:
            scores = [p.total_score for p in self.plant_scores]
            self.average_score = sum(scores) / len(scores)
            self.median_score = sorted(scores)[len(scores) // 2]
            
            self.high_priority_count = sum(1 for p in self.plant_scores if p.priority_level == PriorityLevel.HIGH)
            self.medium_priority_count = sum(1 for p in self.plant_scores if p.priority_level == PriorityLevel.MEDIUM)
            self.low_priority_count = sum(1 for p in self.plant_scores if p.priority_level == PriorityLevel.LOW)
        
        return self
    
    def get_high_priority_plants(self) -> List[PrioritizationScore]:
        """Get all high priority plants."""
        return [p for p in self.plant_scores if p.priority_level == PriorityLevel.HIGH]
    
    def get_top_n(self, n: int = 10) -> List[PrioritizationScore]:
        """Get top N plants by score."""
        return self.plant_scores[:n]
