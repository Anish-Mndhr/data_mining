"""
Scoring algorithms for plant prioritization.

Implements multi-criteria scoring functions for:
- Ethnobotanical validation
- Antimicrobial efficacy
- Safety profile
- Research feasibility
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from .models import PlantData, PathogenData, CategoryScore
from .config import (
    CATEGORY_WEIGHTS,
    ETHNOBOTANICAL_WEIGHTS,
    ANTIMICROBIAL_WEIGHTS,
    SAFETY_WEIGHTS,
    FEASIBILITY_WEIGHTS,
    MIC_THRESHOLDS,
    MBC_MIC_RATIO_THRESHOLDS,
    ICF_THRESHOLDS,
    WHO_PRIORITY_PATHOGENS,
    AMR_INDICATORS,
    PATHOGEN_WEIGHTS,
    UNIT_CONVERSIONS,
)


def parse_numeric_value(value_str: Optional[str]) -> Optional[float]:
    """
    Parse numeric value from string with units.
    
    Examples:
        "125 μg/mL" -> 125.0
        "0.5-1.0 mg/mL" -> 0.75 (average)
        "62.5 μg/mL" -> 62.5
    
    Args:
        value_str: String containing numeric value with optional units
        
    Returns:
        Parsed numeric value or None if parsing fails
    """
    if not value_str or value_str == "None reported" or value_str == "null":
        return None
    
    try:
        # Remove extra whitespace
        value_str = value_str.strip()
        
        # Handle ranges (e.g., "0.5-1.0", "125-250")
        range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', value_str)
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            numeric_value = (min_val + max_val) / 2  # Use average of range
        else:
            # Extract first numeric value
            number_match = re.search(r'(\d+\.?\d*)', value_str)
            if not number_match:
                return None
            numeric_value = float(number_match.group(1))
        
        # Extract and apply unit conversion
        unit_conversion = 1.0
        for unit, conversion in UNIT_CONVERSIONS.items():
            if unit in value_str:
                unit_conversion = conversion
                break
        
        return numeric_value * unit_conversion
        
    except (ValueError, AttributeError):
        return None


def is_who_priority_pathogen(pathogen_name: str) -> bool:
    """Check if pathogen is on WHO priority list."""
    pathogen_lower = pathogen_name.lower()
    for who_pathogen in WHO_PRIORITY_PATHOGENS:
        if who_pathogen.lower() in pathogen_lower:
            return True
    return False


def is_amr_strain(pathogen_name: str) -> bool:
    """Check if pathogen name indicates AMR strain."""
    pathogen_lower = pathogen_name.lower()
    for indicator in AMR_INDICATORS:
        if indicator.lower() in pathogen_lower:
            return True
    return False


def calculate_ethnobotanical_score(plant: PlantData) -> CategoryScore:
    """
    Calculate ethnobotanical validation score.
    
    Criteria:
    - ICF (Informant Consensus Factor): 0-1 value
    - Traditional usage breadth: number of uses mentioned
    - Cultural consensus: presence of traditional knowledge
    
    Args:
        plant: PlantData object
        
    Returns:
        CategoryScore with weighted ethnobotanical score
    """
    details = {}
    sub_scores = {}
    justifications = []
    
    # 1. ICF Score (50% weight)
    icf_score = 0.0
    if plant.cultural_consensus_icf is not None:
        icf_score = plant.cultural_consensus_icf
        details["icf_value"] = icf_score
        
        # Categorize ICF
        if icf_score >= ICF_THRESHOLDS["excellent"]:
            details["icf_category"] = "excellent"
            justifications.append(f"Excellent traditional consensus (ICF={icf_score:.2f})")
        elif icf_score >= ICF_THRESHOLDS["good"]:
            details["icf_category"] = "good"
            justifications.append(f"Good traditional consensus (ICF={icf_score:.2f})")
        elif icf_score >= ICF_THRESHOLDS["moderate"]:
            details["icf_category"] = "moderate"
            justifications.append(f"Moderate traditional consensus (ICF={icf_score:.2f})")
        else:
            details["icf_category"] = "weak"
            justifications.append(f"Weak traditional consensus (ICF={icf_score:.2f})")
    else:
        justifications.append("No ICF data available")
    
    sub_scores["icf"] = icf_score
    
    # 2. Traditional usage breadth (30% weight)
    usage_score = 0.0
    if plant.traditional_usage:
        # Count number of uses (split by common delimiters)
        uses = re.split(r'[,;.]', plant.traditional_usage)
        use_count = len([u for u in uses if u.strip()])
        
        # Normalize: 1-3 uses=0.3, 4-6=0.6, 7+=1.0
        if use_count >= 7:
            usage_score = 1.0
            justifications.append(f"Extensive traditional uses ({use_count} uses)")
        elif use_count >= 4:
            usage_score = 0.6
            justifications.append(f"Multiple traditional uses ({use_count} uses)")
        elif use_count >= 1:
            usage_score = 0.3
            justifications.append(f"Limited traditional uses ({use_count} uses)")
        
        details["traditional_use_count"] = use_count
    else:
        justifications.append("No traditional usage data")
    
    sub_scores["traditional_usage"] = usage_score
    
    # 3. Cultural validation (20% weight)
    cultural_score = 0.0
    cultural_indicators = 0
    
    if plant.location_found_nepal:
        cultural_indicators += 1
        details["found_in_nepal"] = True
    if plant.local_name:
        cultural_indicators += 1
        details["has_local_name"] = True
    if plant.preparation_method or plant.preparation_solvent:
        cultural_indicators += 1
        details["traditional_preparation"] = True
    
    cultural_score = min(cultural_indicators / 3.0, 1.0)
    sub_scores["cultural_validation"] = cultural_score
    
    if cultural_indicators > 0:
        justifications.append(f"Cultural validation: {cultural_indicators}/3 indicators")
    
    # Calculate weighted score
    weighted_score = (
        sub_scores["icf"] * ETHNOBOTANICAL_WEIGHTS["icf_score"] +
        sub_scores["traditional_usage"] * ETHNOBOTANICAL_WEIGHTS["traditional_usage_breadth"] +
        sub_scores["cultural_validation"] * ETHNOBOTANICAL_WEIGHTS["cultural_consensus"]
    )
    
    details["sub_scores"] = sub_scores
    
    return CategoryScore(
        category="ethnobotanical",
        score=weighted_score,
        weight=CATEGORY_WEIGHTS["ethnobotanical"],
        weighted_score=weighted_score * CATEGORY_WEIGHTS["ethnobotanical"],
        details=details,
        justification=" | ".join(justifications) if justifications else "Insufficient data"
    )


def calculate_antimicrobial_score(plant: PlantData) -> CategoryScore:
    """
    Calculate antimicrobial efficacy score.
    
    Criteria:
    - MIC potency: lower MIC = higher score
    - Pathogen spectrum: more pathogens tested = higher score
    - MBC/MIC ratio: closer to 1 = bactericidal
    - AMR effectiveness: activity against resistant strains
    
    Args:
        plant: PlantData object
        
    Returns:
        CategoryScore with weighted antimicrobial score
    """
    details = {}
    sub_scores = {}
    justifications = []
    
    # Parse MIC/MBC values from pathogen data
    mic_values = []
    mbc_values = []
    pathogen_names = []
    who_priority_count = 0
    amr_strain_count = 0
    
    for pathogen in plant.pathogen_data:
        pathogen_names.append(pathogen.pathogen)
        
        # Parse MIC
        mic_val = parse_numeric_value(pathogen.mic)
        if mic_val is not None:
            pathogen.mic_value = mic_val
            
            # Apply pathogen weight multiplier
            weight = PATHOGEN_WEIGHTS["standard"]
            if is_who_priority_pathogen(pathogen.pathogen):
                weight = PATHOGEN_WEIGHTS["who_priority"]
                who_priority_count += 1
            if is_amr_strain(pathogen.pathogen):
                weight = PATHOGEN_WEIGHTS["amr_strain"]
                amr_strain_count += 1
            
            # Weight the MIC value
            mic_values.append((mic_val, weight))
        
        # Parse MBC
        mbc_val = parse_numeric_value(pathogen.mbc)
        if mbc_val is not None:
            pathogen.mbc_value = mbc_val
            mbc_values.append(mbc_val)
    
    # Also check strain_data
    for strain in plant.strain_data:
        mic_val = parse_numeric_value(strain.mic)
        if mic_val is not None:
            strain.mic_value = mic_val
            
            weight = PATHOGEN_WEIGHTS["standard"]
            if is_who_priority_pathogen(strain.strain):
                weight = PATHOGEN_WEIGHTS["who_priority"]
                who_priority_count += 1
            if is_amr_strain(strain.strain):
                weight = PATHOGEN_WEIGHTS["amr_strain"]
                amr_strain_count += 1
            
            mic_values.append((mic_val, weight))
            pathogen_names.append(strain.strain)
        
        mbc_val = parse_numeric_value(strain.mbc)
        if mbc_val is not None:
            strain.mbc_value = mbc_val
            mbc_values.append(mbc_val)
    
    details["pathogen_count"] = len(pathogen_names)
    details["mic_count"] = len(mic_values)
    details["mbc_count"] = len(mbc_values)
    details["who_priority_pathogens"] = who_priority_count
    details["amr_strain_count"] = amr_strain_count
    
    # 1. MIC Potency Score (40% weight)
    mic_score = 0.0
    if mic_values:
        # Calculate weighted average MIC
        total_weight = sum(w for _, w in mic_values)
        weighted_avg_mic = sum(val * w for val, w in mic_values) / total_weight
        
        details["average_mic"] = round(weighted_avg_mic, 2)
        details["min_mic"] = round(min(val for val, _ in mic_values), 2)
        
        # Score based on MIC thresholds (lower is better)
        if weighted_avg_mic <= MIC_THRESHOLDS["excellent"]:
            mic_score = 1.0
            justifications.append(f"Excellent potency (avg MIC: {weighted_avg_mic:.1f} μg/mL)")
        elif weighted_avg_mic <= MIC_THRESHOLDS["good"]:
            mic_score = 0.8
            justifications.append(f"Good potency (avg MIC: {weighted_avg_mic:.1f} μg/mL)")
        elif weighted_avg_mic <= MIC_THRESHOLDS["moderate"]:
            mic_score = 0.6
            justifications.append(f"Moderate potency (avg MIC: {weighted_avg_mic:.1f} μg/mL)")
        elif weighted_avg_mic <= MIC_THRESHOLDS["weak"]:
            mic_score = 0.3
            justifications.append(f"Weak potency (avg MIC: {weighted_avg_mic:.1f} μg/mL)")
        else:
            mic_score = 0.1
            justifications.append(f"Poor potency (avg MIC: {weighted_avg_mic:.1f} μg/mL)")
    else:
        justifications.append("No MIC data available")
    
    sub_scores["mic_potency"] = mic_score
    
    # 2. Pathogen Spectrum Score (30% weight)
    spectrum_score = 0.0
    if pathogen_names:
        unique_pathogens = len(set(pathogen_names))
        details["unique_pathogens"] = unique_pathogens
        
        # Normalize: 1-2 pathogens=0.3, 3-4=0.6, 5+=1.0
        if unique_pathogens >= 5:
            spectrum_score = 1.0
            justifications.append(f"Broad spectrum activity ({unique_pathogens} pathogens)")
        elif unique_pathogens >= 3:
            spectrum_score = 0.6
            justifications.append(f"Moderate spectrum ({unique_pathogens} pathogens)")
        else:
            spectrum_score = 0.3
            justifications.append(f"Narrow spectrum ({unique_pathogens} pathogens)")
    else:
        justifications.append("No pathogen data")
    
    sub_scores["pathogen_spectrum"] = spectrum_score
    
    # 3. MBC/MIC Ratio Score (20% weight)
    ratio_score = 0.0
    if mic_values and mbc_values and len(mic_values) == len(mbc_values):
        # Calculate average ratio
        ratios = []
        for i in range(min(len(mic_values), len(mbc_values))):
            mic_val = mic_values[i][0]
            mbc_val = mbc_values[i]
            if mic_val > 0:
                ratios.append(mbc_val / mic_val)
        
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            details["mbc_mic_ratio"] = round(avg_ratio, 2)
            
            if avg_ratio <= MBC_MIC_RATIO_THRESHOLDS["bactericidal"]:
                ratio_score = 1.0
                justifications.append(f"Bactericidal activity (MBC/MIC: {avg_ratio:.1f})")
            else:
                ratio_score = 0.5
                justifications.append(f"Bacteriostatic activity (MBC/MIC: {avg_ratio:.1f})")
    
    sub_scores["mbc_mic_ratio"] = ratio_score
    
    # 4. AMR Effectiveness (10% weight)
    amr_score = 0.0
    if who_priority_count > 0 or amr_strain_count > 0:
        # Score based on count
        total_amr = who_priority_count + amr_strain_count
        amr_score = min(total_amr / 3.0, 1.0)  # Cap at 1.0
        
        justifications.append(f"Active against {total_amr} priority/AMR strains")
    
    sub_scores["amr_effectiveness"] = amr_score
    
    # Calculate weighted score
    weighted_score = (
        sub_scores["mic_potency"] * ANTIMICROBIAL_WEIGHTS["mic_potency"] +
        sub_scores["pathogen_spectrum"] * ANTIMICROBIAL_WEIGHTS["pathogen_spectrum"] +
        sub_scores["mbc_mic_ratio"] * ANTIMICROBIAL_WEIGHTS["mbc_ratio"] +
        sub_scores["amr_effectiveness"] * ANTIMICROBIAL_WEIGHTS["amr_effectiveness"]
    )
    
    details["sub_scores"] = sub_scores
    
    return CategoryScore(
        category="antimicrobial_efficacy",
        score=weighted_score,
        weight=CATEGORY_WEIGHTS["antimicrobial_efficacy"],
        weighted_score=weighted_score * CATEGORY_WEIGHTS["antimicrobial_efficacy"],
        details=details,
        justification=" | ".join(justifications) if justifications else "Insufficient data"
    )


def calculate_safety_score(plant: PlantData) -> CategoryScore:
    """
    Calculate safety profile score.
    
    Criteria:
    - Toxicity profile: known safety data
    - Preparation safety: traditional vs. harsh solvents
    - Adverse effects: reported side effects
    
    Note: In absence of specific toxicity data, we use proxy indicators.
    
    Args:
        plant: PlantData object
        
    Returns:
        CategoryScore with weighted safety score
    """
    details = {}
    sub_scores = {}
    justifications = []
    
    # 1. Toxicity Profile (50% weight)
    # Default to moderate (0.5) in absence of data
    toxicity_score = 0.5
    details["has_toxicity_data"] = False
    
    # Check for toxicity mentions in text fields
    toxicity_keywords = {
        "safe": 1.0,
        "non-toxic": 1.0,
        "edible": 0.9,
        "food": 0.9,
        "toxic": 0.2,
        "poison": 0.1,
        "caution": 0.4,
    }
    
    search_text = " ".join(filter(None, [
        plant.traditional_usage or "",
        plant.antibacterial_properties or "",
        plant.preparation_method or "",
    ])).lower()
    
    for keyword, score in toxicity_keywords.items():
        if keyword in search_text:
            toxicity_score = score
            details["has_toxicity_data"] = True
            justifications.append(f"Safety indicator: '{keyword}' mentioned")
            break
    
    if not details["has_toxicity_data"]:
        justifications.append("No specific toxicity data (assumed moderate safety)")
    
    sub_scores["toxicity_profile"] = toxicity_score
    
    # 2. Preparation Safety (30% weight)
    prep_score = 0.5  # Default
    
    if plant.preparation_solvent or plant.extraction_solvent:
        solvents = " ".join(filter(None, [
            plant.preparation_solvent or "",
            plant.extraction_solvent or "",
        ])).lower()
        
        details["solvents"] = solvents
        
        # Safe solvents
        if any(s in solvents for s in ["water", "aqueous", "decoction", "infusion"]):
            prep_score = 1.0
            justifications.append("Safe aqueous preparation")
        # Moderate solvents
        elif any(s in solvents for s in ["ethanol", "alcohol", "methanol"]):
            prep_score = 0.7
            justifications.append("Alcohol-based extraction (moderate safety)")
        # Harsh solvents
        elif any(s in solvents for s in ["chloroform", "hexane", "acetone", "dmso"]):
            prep_score = 0.4
            justifications.append("Harsh solvent extraction (requires processing)")
        else:
            justifications.append("Unspecified preparation method")
    else:
        justifications.append("No preparation data")
    
    sub_scores["preparation_safety"] = prep_score
    
    # 3. Adverse Effects (20% weight)
    # Default to moderate (0.6) in absence of data
    adverse_score = 0.6
    details["has_adverse_data"] = False
    
    # Look for mentions of side effects
    if "side effect" in search_text or "adverse" in search_text:
        adverse_score = 0.3
        details["has_adverse_data"] = True
        justifications.append("Adverse effects reported")
    elif "safe" in search_text or "well-tolerated" in search_text:
        adverse_score = 1.0
        details["has_adverse_data"] = True
        justifications.append("Well-tolerated")
    
    sub_scores["adverse_effects"] = adverse_score
    
    # Calculate weighted score
    weighted_score = (
        sub_scores["toxicity_profile"] * SAFETY_WEIGHTS["toxicity_profile"] +
        sub_scores["preparation_safety"] * SAFETY_WEIGHTS["preparation_safety"] +
        sub_scores["adverse_effects"] * SAFETY_WEIGHTS["adverse_effects"]
    )
    
    details["sub_scores"] = sub_scores
    
    return CategoryScore(
        category="safety",
        score=weighted_score,
        weight=CATEGORY_WEIGHTS["safety"],
        weighted_score=weighted_score * CATEGORY_WEIGHTS["safety"],
        details=details,
        justification=" | ".join(justifications) if justifications else "Limited safety data"
    )


def calculate_feasibility_score(plant: PlantData) -> CategoryScore:
    """
    Calculate research feasibility score.
    
    Criteria:
    - Geographic availability: found in Nepal
    - Parts accessibility: ease of collecting
    - Cultivation potential: can be cultivated
    - Seasonality: year-round availability
    
    Args:
        plant: PlantData object
        
    Returns:
        CategoryScore with weighted feasibility score
    """
    details = {}
    sub_scores = {}
    justifications = []
    
    # 1. Geographic Availability (40% weight)
    geo_score = 0.0
    
    if plant.location_found_nepal:
        locations = plant.location_found_nepal.lower()
        
        # Count number of districts/locations mentioned
        location_count = len(re.findall(r'district|municipality|village', locations))
        details["location_mentions"] = location_count
        
        if location_count >= 3:
            geo_score = 1.0
            justifications.append(f"Widely distributed in Nepal ({location_count}+ locations)")
        elif location_count >= 1:
            geo_score = 0.7
            justifications.append(f"Found in multiple Nepal locations ({location_count})")
        else:
            geo_score = 0.5
            justifications.append("Found in Nepal")
        
        details["found_in_nepal"] = True
    else:
        justifications.append("Nepal distribution unknown")
        geo_score = 0.3  # May still be available
    
    sub_scores["geographic_availability"] = geo_score
    
    # 2. Parts Accessibility (30% weight)
    parts_score = 0.0
    
    parts_text = " ".join(filter(None, [
        plant.parts_used or "",
        plant.parts_with_amr or "",
    ])).lower()
    
    if parts_text:
        details["parts"] = parts_text
        
        # Easy to collect parts
        if any(p in parts_text for p in ["leaf", "leaves", "stem", "bark", "flower"]):
            parts_score = 1.0
            justifications.append("Easily accessible plant parts")
        # Moderate parts
        elif any(p in parts_text for p in ["root", "rhizome", "tuber", "seed"]):
            parts_score = 0.6
            justifications.append("Moderately accessible parts (root/rhizome)")
        # Whole plant
        elif "whole" in parts_text:
            parts_score = 0.4
            justifications.append("Requires whole plant")
        else:
            parts_score = 0.5
            justifications.append("Plant parts specified")
    else:
        parts_score = 0.5
        justifications.append("Parts not specified")
    
    sub_scores["parts_accessibility"] = parts_score
    
    # 3. Cultivation Potential (20% weight)
    cultivation_score = 0.5  # Default moderate
    
    if plant.growth_form:
        growth = plant.growth_form.lower()
        details["growth_form"] = growth
        
        # Easy to cultivate
        if any(g in growth for g in ["herb", "annual", "perennial"]):
            cultivation_score = 0.9
            justifications.append("Cultivation-friendly growth form")
        # Moderate
        elif any(g in growth for g in ["shrub", "subshrub"]):
            cultivation_score = 0.6
            justifications.append("Moderate cultivation requirements")
        # Difficult
        elif "tree" in growth:
            cultivation_score = 0.3
            justifications.append("Tree form (slow growth)")
    
    sub_scores["cultivation_potential"] = cultivation_score
    
    # 4. Seasonality (10% weight)
    # Default to moderate (0.6) - assume most plants have some seasonal variation
    seasonality_score = 0.6
    
    if plant.altitude_range_found:
        # Plants with wide altitude range may be more available
        altitude_text = plant.altitude_range_found.lower()
        if "–" in altitude_text or "-" in altitude_text:
            seasonality_score = 0.7
            justifications.append("Wide altitude range (better availability)")
    
    sub_scores["seasonality"] = seasonality_score
    
    # Calculate weighted score
    weighted_score = (
        sub_scores["geographic_availability"] * FEASIBILITY_WEIGHTS["geographic_availability"] +
        sub_scores["parts_accessibility"] * FEASIBILITY_WEIGHTS["parts_accessibility"] +
        sub_scores["cultivation_potential"] * FEASIBILITY_WEIGHTS["cultivation_potential"] +
        sub_scores["seasonality"] * FEASIBILITY_WEIGHTS["seasonality"]
    )
    
    details["sub_scores"] = sub_scores
    
    return CategoryScore(
        category="feasibility",
        score=weighted_score,
        weight=CATEGORY_WEIGHTS["feasibility"],
        weighted_score=weighted_score * CATEGORY_WEIGHTS["feasibility"],
        details=details,
        justification=" | ".join(justifications) if justifications else "Limited feasibility data"
    )


def calculate_composite_score(plant: PlantData) -> Tuple[float, Dict[str, CategoryScore]]:
    """
    Calculate composite prioritization score for a plant.
    
    Combines all category scores with their respective weights.
    
    Args:
        plant: PlantData object
        
    Returns:
        Tuple of (total_score, category_scores_dict)
    """
    # Calculate individual category scores
    ethnobotanical = calculate_ethnobotanical_score(plant)
    antimicrobial = calculate_antimicrobial_score(plant)
    safety = calculate_safety_score(plant)
    feasibility = calculate_feasibility_score(plant)
    
    # Calculate total weighted score
    total_score = (
        ethnobotanical.weighted_score +
        antimicrobial.weighted_score +
        safety.weighted_score +
        feasibility.weighted_score
    )
    
    category_scores = {
        "ethnobotanical": ethnobotanical,
        "antimicrobial": antimicrobial,
        "safety": safety,
        "feasibility": feasibility,
    }
    
    return total_score, category_scores
