"""
Configuration file for the prioritization algorithm.

Defines scoring weights, thresholds, and criteria for plant prioritization.
"""

# ============================================================================
# SCORING WEIGHTS
# ============================================================================

# Main category weights (must sum to 1.0)
CATEGORY_WEIGHTS = {
    "ethnobotanical": 0.30,  # Traditional knowledge validation
    "antimicrobial_efficacy": 0.40,  # Pharmacological potency
    "safety": 0.20,  # Toxicity and safety profile
    "feasibility": 0.10,  # Research accessibility
}

# Sub-criteria weights within each category
ETHNOBOTANICAL_WEIGHTS = {
    "icf_score": 0.50,  # Informant Consensus Factor (0-1)
    "traditional_usage_breadth": 0.30,  # Number of ailments treated
    "cultural_consensus": 0.20,  # Community validation
}

ANTIMICROBIAL_WEIGHTS = {
    "mic_potency": 0.40,  # MIC values (lower is better)
    "pathogen_spectrum": 0.30,  # Number of pathogens tested
    "mbc_ratio": 0.20,  # MBC/MIC ratio (closer to 1 is better)
    "amr_effectiveness": 0.10,  # Effectiveness against resistant strains
}

SAFETY_WEIGHTS = {
    "toxicity_profile": 0.50,  # Known toxicity data
    "preparation_safety": 0.30,  # Safety of traditional preparation
    "adverse_effects": 0.20,  # Reported side effects
}

FEASIBILITY_WEIGHTS = {
    "geographic_availability": 0.40,  # Found in Nepal
    "parts_accessibility": 0.30,  # Ease of collecting plant parts
    "cultivation_potential": 0.20,  # Can be cultivated
    "seasonality": 0.10,  # Year-round availability
}

# ============================================================================
# PRIORITY THRESHOLDS
# ============================================================================

# Composite score thresholds for priority classification
PRIORITY_THRESHOLDS = {
    "high": 0.70,  # Score >= 0.70
    "medium": 0.50,  # 0.50 <= Score < 0.70
    "low": 0.0,  # Score < 0.50
}

# ============================================================================
# MIC/MBC INTERPRETATION
# ============================================================================

# MIC thresholds (μg/mL) - lower values indicate higher potency
MIC_THRESHOLDS = {
    "excellent": 100,  # MIC <= 100 μg/mL
    "good": 500,  # 100 < MIC <= 500 μg/mL
    "moderate": 1000,  # 500 < MIC <= 1000 μg/mL
    "weak": 5000,  # 1000 < MIC <= 5000 μg/mL
    "poor": float('inf'),  # MIC > 5000 μg/mL
}

# MBC/MIC ratio thresholds (closer to 1 means bactericidal, higher means bacteriostatic)
MBC_MIC_RATIO_THRESHOLDS = {
    "bactericidal": 4,  # Ratio <= 4 (bactericidal activity)
    "bacteriostatic": float('inf'),  # Ratio > 4 (bacteriostatic only)
}

# ============================================================================
# PATHOGEN PRIORITIZATION
# ============================================================================

# WHO Priority Pathogens (bonus scoring for these)
WHO_PRIORITY_PATHOGENS = [
    "Acinetobacter baumannii",
    "Pseudomonas aeruginosa",
    "Enterobacteriaceae",
    "Staphylococcus aureus",  # MRSA
    "Klebsiella pneumoniae",
    "Escherichia coli",
]

# AMR strain indicators (bonus for resistant strains)
AMR_INDICATORS = [
    "MRSA", "MDR", "multidrug-resistant", "resistant",
    "carbapenem-resistant", "ESBL", "VRE", "VRSA"
]

# Pathogen weight multipliers
PATHOGEN_WEIGHTS = {
    "who_priority": 1.5,  # 50% bonus for WHO priority pathogens
    "amr_strain": 1.3,  # 30% bonus for AMR strains
    "standard": 1.0,
}

# ============================================================================
# ICF (INFORMANT CONSENSUS FACTOR) INTERPRETATION
# ============================================================================

ICF_THRESHOLDS = {
    "excellent": 0.80,  # ICF >= 0.80 (strong consensus)
    "good": 0.60,  # 0.60 <= ICF < 0.80
    "moderate": 0.40,  # 0.40 <= ICF < 0.60
    "weak": 0.20,  # 0.20 <= ICF < 0.40
    "poor": 0.0,  # ICF < 0.20
}

# ============================================================================
# DATA NORMALIZATION
# ============================================================================

# Unit conversion factors to μg/mL
UNIT_CONVERSIONS = {
    "μg/mL": 1.0,
    "µg/mL": 1.0,
    "mg/mL": 1000.0,
    "g/L": 1000.0,
    "mg/L": 1.0,
    "μg/L": 0.001,
    "µg/L": 0.001,
}

# Missing data handling
MISSING_DATA_DEFAULTS = {
    "icf": 0.0,  # No consensus if not reported
    "mic": None,  # Don't score if MIC not available
    "mbc": None,  # Don't score if MBC not available
    "toxicity": 0.5,  # Assume moderate safety if not reported
}

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

# Report generation settings
REPORT_SETTINGS = {
    "max_plants_display": 50,  # Maximum plants to show in reports
    "decimal_places": 3,  # Decimal precision for scores
    "include_justification": True,  # Include scoring explanations
    "generate_charts": True,  # Generate visualization charts
}

# Export formats
EXPORT_FORMATS = ["json", "csv", "html", "markdown"]

# ============================================================================
# VALIDATION RULES
# ============================================================================

# Minimum data requirements for scoring
MINIMUM_REQUIREMENTS = {
    "scientific_name": True,  # Must have scientific name
    "min_pathogens": 1,  # At least 1 pathogen tested
    "min_mic_values": 1,  # At least 1 MIC value
}
