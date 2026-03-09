"""
Data loading and normalization utilities.

Loads plant data from various sources:
- JSON files from Firecrawl extraction
- CSV files from database exports
- Direct API responses

Normalizes and validates data for prioritization.
"""

import json
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from .models import PlantData, PathogenData, StrainData


def load_from_json(file_path: Union[str, Path]) -> List[PlantData]:
    """
    Load plant data from JSON file.
    
    Supports:
    - Single plant object
    - Array of plant objects
    - Firecrawl extraction format
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of PlantData objects
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    plants = []
    
    # Handle different JSON formats
    if isinstance(data, dict):
        # Check if it's a Firecrawl response
        if 'data' in data:
            data = data['data']
        
        # Check if it's a single plant
        if 'scientific_name' in data or 'scientificName' in data:
            plants.append(_normalize_plant_dict(data))
        else:
            # Might be a dict of plants
            for key, value in data.items():
                if isinstance(value, dict):
                    plants.append(_normalize_plant_dict(value))
    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                plants.append(_normalize_plant_dict(item))
    
    return plants


def load_from_csv(file_path: Union[str, Path]) -> List[PlantData]:
    """
    Load plant data from CSV file.
    
    Expected columns (flexible naming):
    - scientific_name / scientificName
    - local_name / localName / commonName
    - traditional_usage / traditionalUsage
    - cultural_consensus_icf / icf
    - etc.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of PlantData objects
    """
    df = pd.read_csv(file_path)
    
    plants = []
    for _, row in df.iterrows():
        plant_dict = row.to_dict()
        plants.append(_normalize_plant_dict(plant_dict))
    
    return plants


def load_from_notebook_output(file_path: Union[str, Path]) -> List[PlantData]:
    """
    Load plant data from Jupyter notebook output (main.ipynb format).
    
    Parses the JSON output cells from the notebook.
    
    Args:
        file_path: Path to .ipynb file
        
    Returns:
        List of PlantData objects
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    plants = []
    
    # Extract data from notebook cells
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            outputs = cell.get('outputs', [])
            for output in outputs:
                if output.get('output_type') == 'stream':
                    # Try to parse text output as JSON
                    text = ''.join(output.get('text', []))
                    try:
                        data = json.loads(text)
                        if isinstance(data, dict) and 'data' in data:
                            plant_dict = data['data']
                            plants.append(_normalize_plant_dict(plant_dict))
                    except json.JSONDecodeError:
                        continue
    
    return plants


def _normalize_plant_dict(data: Dict[str, Any]) -> PlantData:
    """
    Normalize plant dictionary to PlantData model.
    
    Handles different naming conventions and field mappings.
    
    Args:
        data: Dictionary with plant data
        
    Returns:
        PlantData object
    """
    # Map field names (handle both snake_case and camelCase)
    normalized = {}
    
    # Basic fields
    normalized['scientific_name'] = (
        data.get('scientific_name') or 
        data.get('scientificName') or 
        data.get('name') or
        'Unknown'
    )
    
    normalized['local_name'] = (
        data.get('local_name') or
        data.get('localName') or
        data.get('commonName') or
        data.get('commonNameNepali')
    )
    
    normalized['family'] = (
        data.get('family') or
        data.get('family_citation', '').split(' in ')[0] if data.get('family_citation') else None
    )
    
    normalized['genus'] = data.get('genus')
    
    # Ethnobotanical data
    normalized['traditional_usage'] = (
        data.get('traditional_usage') or
        data.get('traditionalUsage')
    )
    
    normalized['cultural_consensus_icf'] = (
        data.get('cultural_consensus_icf') or
        data.get('culturalConsensusIcf') or
        data.get('icf')
    )
    
    normalized['location_found_nepal'] = (
        data.get('location_found_nepal') or
        data.get('locationFoundNepal') or
        data.get('districts') or
        data.get('studyLocations')
    )
    
    normalized['growth_form'] = data.get('growth_form') or data.get('growthForm')
    normalized['altitude_range_found'] = (
        data.get('altitude_range_found') or
        data.get('altitudeRangeFound')
    )
    
    # Preparation data
    normalized['preparation_solvent'] = (
        data.get('preparation_solvent') or
        data.get('preparationSolvent')
    )
    
    normalized['preparation_method'] = (
        data.get('preparation_method') or
        data.get('preparationMethod')
    )
    
    normalized['extraction_solvent'] = (
        data.get('extraction_solvent') or
        data.get('extractionSolvent')
    )
    
    normalized['compound_class'] = (
        data.get('compound_class') or
        data.get('compoundClass')
    )
    
    normalized['parts_with_amr'] = (
        data.get('parts_with_amr') or
        data.get('partsWithAmr')
    )
    
    normalized['parts_used'] = (
        data.get('parts_used') or
        data.get('partsUsed')
    )
    
    # Antimicrobial data
    normalized['antibacterial_properties'] = (
        data.get('antibacterial_properties') or
        data.get('antibacterialProperties')
    )
    
    normalized['amr_properties'] = (
        data.get('amr_properties') or
        data.get('amrProperties') or
        data.get('potentialAMR')
    )
    
    # Research metadata
    normalized['research_paper_title'] = (
        data.get('research_paper_title') or
        data.get('researchPaperTitle')
    )
    
    normalized['authors'] = data.get('authors')
    normalized['journal_info'] = data.get('journal_info') or data.get('journalInfo')
    normalized['url'] = data.get('url') or data.get('link')
    normalized['sn'] = data.get('sn')
    
    # Parse pathogen data
    pathogen_data = []
    if 'pathogen_data' in data:
        for pathogen in data['pathogen_data']:
            pathogen_data.append(PathogenData(**pathogen))
    elif 'pathogenData' in data:
        for pathogen in data['pathogenData']:
            pathogen_data.append(PathogenData(**pathogen))
    
    normalized['pathogen_data'] = pathogen_data
    
    # Parse strain data
    strain_data = []
    if 'strain_data' in data:
        for strain in data['strain_data']:
            strain_data.append(StrainData(**strain))
    elif 'strainData' in data:
        for strain in data['strainData']:
            # Handle both dict and pre-parsed StrainData
            if isinstance(strain, dict):
                strain_data.append(StrainData(**strain))
            else:
                strain_data.append(strain)
    
    normalized['strain_data'] = strain_data
    
    return PlantData(**normalized)


def load_plants(
    source: Union[str, Path, List[Dict]],
    source_type: Optional[str] = None
) -> List[PlantData]:
    """
    Load plant data from various sources.
    
    Auto-detects source type if not specified.
    
    Args:
        source: File path, directory, or list of dicts
        source_type: Optional type hint ('json', 'csv', 'notebook', 'dict')
        
    Returns:
        List of PlantData objects
    """
    # Handle list of dictionaries
    if isinstance(source, list):
        return [_normalize_plant_dict(d) for d in source]
    
    # Handle file paths
    path = Path(source)
    
    if not path.exists():
        raise FileNotFoundError(f"Source not found: {source}")
    
    # Auto-detect file type
    if source_type is None:
        if path.suffix == '.json':
            source_type = 'json'
        elif path.suffix == '.csv':
            source_type = 'csv'
        elif path.suffix == '.ipynb':
            source_type = 'notebook'
        else:
            raise ValueError(f"Cannot auto-detect type for {path.suffix}. Specify source_type.")
    
    # Load based on type
    if source_type == 'json':
        return load_from_json(path)
    elif source_type == 'csv':
        return load_from_csv(path)
    elif source_type == 'notebook':
        return load_from_notebook_output(path)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


def validate_plants(plants: List[PlantData], min_requirements: Optional[Dict] = None) -> List[PlantData]:
    """
    Validate and filter plants based on minimum requirements.
    
    Default requirements:
    - Must have scientific name
    - Must have at least 1 pathogen tested OR strain data
    
    Args:
        plants: List of PlantData objects
        min_requirements: Optional custom requirements dict
        
    Returns:
        Filtered list of valid PlantData objects
    """
    if min_requirements is None:
        min_requirements = {
            'min_pathogens': 1,
            'min_mic_values': 0,
        }
    
    valid_plants = []
    
    for plant in plants:
        # Check scientific name
        if not plant.scientific_name or plant.scientific_name == 'Unknown':
            continue
        
        # Check pathogen data
        total_pathogens = len(plant.pathogen_data) + len(plant.strain_data)
        if total_pathogens < min_requirements.get('min_pathogens', 1):
            continue
        
        # Check MIC values if required
        if min_requirements.get('min_mic_values', 0) > 0:
            mic_count = sum(1 for p in plant.pathogen_data if p.mic) + \
                       sum(1 for s in plant.strain_data if s.mic)
            if mic_count < min_requirements['min_mic_values']:
                continue
        
        valid_plants.append(plant)
    
    return valid_plants


def save_plants_to_json(plants: List[PlantData], output_path: Union[str, Path]):
    """
    Save plants to JSON file.
    
    Args:
        plants: List of PlantData objects
        output_path: Output file path
    """
    data = [plant.model_dump(exclude_none=True) for plant in plants]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def save_plants_to_csv(plants: List[PlantData], output_path: Union[str, Path]):
    """
    Save plants to CSV file (flattened format).
    
    Args:
        plants: List of PlantData objects
        output_path: Output file path
    """
    rows = []
    
    for plant in plants:
        row = {
            'scientific_name': plant.scientific_name,
            'local_name': plant.local_name,
            'family': plant.family,
            'genus': plant.genus,
            'traditional_usage': plant.traditional_usage,
            'icf': plant.cultural_consensus_icf,
            'location_nepal': plant.location_found_nepal,
            'growth_form': plant.growth_form,
            'altitude_range': plant.altitude_range_found,
            'parts_used': plant.parts_used,
            'pathogen_count': len(plant.pathogen_data) + len(plant.strain_data),
            'antibacterial_properties': plant.antibacterial_properties,
            'amr_properties': plant.amr_properties,
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding='utf-8')
