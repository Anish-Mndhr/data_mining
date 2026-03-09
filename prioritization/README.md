# Plant Prioritization Algorithm

A comprehensive multi-criteria decision analysis (MCDA) system for prioritizing medicinal plants as potential sources of novel antimicrobial agents, with special focus on antimicrobial resistance (AMR).

## Overview

This prioritization framework integrates ethnobotanical knowledge, pharmacological efficacy, safety profiles, and research feasibility to rank medicinal plants for antimicrobial drug discovery research.

### Key Features

- **Multi-Criteria Scoring**: Weighted evaluation across 4 main categories
- **Ethnobotanical Validation**: Traditional knowledge and cultural consensus (ICF)
- **Antimicrobial Efficacy**: MIC/MBC potency, pathogen spectrum, AMR activity
- **Safety Assessment**: Toxicity, preparation methods, adverse effects
- **Research Feasibility**: Geographic availability, accessibility, cultivation
- **WHO Priority Pathogen Focus**: Bonus scoring for critical AMR pathogens
- **Flexible Configuration**: Customizable weights and thresholds
- **Multiple Export Formats**: JSON, CSV, Markdown, HTML reports

## Installation

```bash
# Clone or navigate to the prioritization directory
cd firecrawl/prioritization/

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Command Line Usage

```bash
# Basic prioritization
python -m prioritization.main --input ../main.ipynb --output results/

# With custom parameters
python -m prioritization.main \
    --input plants.json \
    --output results/ \
    --top 20 \
    --min-pathogens 3 \
    --export-all

# Custom scoring weights
python -m prioritization.main \
    --input data.csv \
    --ethnobotanical 0.4 \
    --efficacy 0.3 \
    --safety 0.2 \
    --feasibility 0.1
```

### Python API Usage

```python
from prioritization import (
    load_plants,
    validate_plants,
    prioritize_plants,
    export_all_formats,
)

# Load plant data
plants = load_plants('plants.json')

# Validate minimum requirements
valid_plants = validate_plants(plants, min_requirements={
    'min_pathogens': 1,
    'min_mic_values': 1,
})

# Run prioritization
report = prioritize_plants(valid_plants)

# View top results
for plant in report.get_top_n(10):
    print(f"{plant.rank}. {plant.scientific_name}")
    print(f"   Score: {plant.total_score:.3f} ({plant.priority_level.value})")
    print(f"   Ethnobotanical: {plant.ethnobotanical_score.score:.3f}")
    print(f"   Antimicrobial: {plant.antimicrobial_score.score:.3f}")
    print()

# Export results
export_all_formats(report, output_dir='results/')
```

## Methodology

### Scoring Categories

The algorithm evaluates plants across four weighted categories:

#### 1. Ethnobotanical Validation (30%)

- **ICF Score (50%)**: Informant Consensus Factor (0-1 scale)
  - ≥0.80: Excellent traditional consensus
  - 0.60-0.79: Good consensus
  - 0.40-0.59: Moderate consensus
  - <0.40: Weak consensus

- **Traditional Usage Breadth (30%)**: Number of documented uses
  - 7+ uses: 1.0
  - 4-6 uses: 0.6
  - 1-3 uses: 0.3

- **Cultural Validation (20%)**: Presence of:
  - Found in Nepal
  - Has local name
  - Traditional preparation method documented

#### 2. Antimicrobial Efficacy (40%)

- **MIC Potency (40%)**: Minimum Inhibitory Concentration
  - ≤100 μg/mL: Excellent (1.0)
  - 100-500 μg/mL: Good (0.8)
  - 500-1000 μg/mL: Moderate (0.6)
  - 1000-5000 μg/mL: Weak (0.3)
  - >5000 μg/mL: Poor (0.1)
  - **WHO Priority Pathogen Bonus**: 1.5x weight
  - **AMR Strain Bonus**: 1.3x weight

- **Pathogen Spectrum (30%)**: Breadth of activity
  - 5+ pathogens: 1.0
  - 3-4 pathogens: 0.6
  - 1-2 pathogens: 0.3

- **MBC/MIC Ratio (20%)**: Bactericidal vs. bacteriostatic
  - Ratio ≤4: Bactericidal (1.0)
  - Ratio >4: Bacteriostatic (0.5)

- **AMR Effectiveness (10%)**: Activity against resistant strains
  - Scored based on count of WHO priority/AMR pathogens

#### 3. Safety Profile (20%)

- **Toxicity Profile (50%)**: Known safety data
  - Keywords: "safe", "non-toxic", "edible" → High score
  - Keywords: "toxic", "poison" → Low score
  - Default: Moderate (0.5)

- **Preparation Safety (30%)**: Extraction methods
  - Aqueous/water: Safe (1.0)
  - Ethanol/alcohol: Moderate (0.7)
  - Harsh solvents: Requires processing (0.4)

- **Adverse Effects (20%)**: Reported side effects
  - Well-tolerated: 1.0
  - Side effects reported: 0.3
  - Unknown: 0.6

#### 4. Research Feasibility (10%)

- **Geographic Availability (40%)**: Distribution in Nepal
  - 3+ locations: 1.0
  - 1-2 locations: 0.7
  - Unspecified: 0.3

- **Parts Accessibility (30%)**: Ease of collection
  - Leaves/flowers/bark: Easy (1.0)
  - Roots/rhizomes: Moderate (0.6)
  - Whole plant: Difficult (0.4)

- **Cultivation Potential (20%)**: Growth characteristics
  - Herb/annual/perennial: Easy (0.9)
  - Shrub: Moderate (0.6)
  - Tree: Slow (0.3)

- **Seasonality (10%)**: Year-round availability
  - Wide altitude range: Better availability (0.7)
  - Default: Seasonal variation (0.6)

### Priority Classification

Based on composite score (0-1 scale):

- **High Priority** (≥0.70): Excellent candidates for immediate research
- **Medium Priority** (0.50-0.69): Promising candidates worth investigating
- **Low Priority** (<0.50): Lower confidence or limited data

## Data Requirements

### Input Formats

The algorithm accepts data in multiple formats:

#### JSON Format
```json
{
  "scientific_name": "Curcuma longa",
  "local_name": "Besar",
  "cultural_consensus_icf": 0.97,
  "traditional_usage": "Used for wounds, cuts, inflammation...",
  "location_found_nepal": "Lalitpur, Kathmandu, Dhading",
  "pathogen_data": [
    {
      "pathogen": "Staphylococcus aureus",
      "mic": "125 μg/mL",
      "mbc": "250 μg/mL",
      "zoi": "18 mm"
    }
  ]
}
```

#### CSV Format
Columns: `scientific_name`, `local_name`, `icf`, `traditional_usage`, `location_nepal`, etc.

#### Jupyter Notebook
Automatically extracts data from Firecrawl extraction outputs in `.ipynb` files.

### Minimum Requirements

For valid scoring, plants must have:
- Scientific name
- At least 1 pathogen tested (in `pathogen_data` or `strain_data`)
- Optional: MIC values for higher confidence

## Configuration

### Custom Weights

Modify `config.py` or pass via CLI:

```python
# Default weights
CATEGORY_WEIGHTS = {
    "ethnobotanical": 0.30,
    "antimicrobial_efficacy": 0.40,
    "safety": 0.20,
    "feasibility": 0.10,
}
```

### Priority Thresholds

```python
PRIORITY_THRESHOLDS = {
    "high": 0.70,
    "medium": 0.50,
    "low": 0.0,
}
```

### MIC Thresholds

```python
MIC_THRESHOLDS = {
    "excellent": 100,    # μg/mL
    "good": 500,
    "moderate": 1000,
    "weak": 5000,
}
```

## Output Formats

### JSON Export
Structured data with detailed scoring breakdown:
```json
{
  "metadata": {...},
  "summary": {...},
  "plants": [
    {
      "rank": 1,
      "scientific_name": "...",
      "total_score": 0.823,
      "priority_level": "high",
      "scores": {...},
      "score_details": {...}
    }
  ]
}
```

### CSV Export
Tabular format for spreadsheet analysis:
```
rank,scientific_name,total_score,priority_level,ethnobotanical_score,...
1,Curcuma longa,0.823,high,0.891,0.845,0.712,0.654
```

### Markdown Export
Human-readable report with tables and justifications.

### Summary Statistics
```
Priority Distribution:
  High:   15 plants (30%)
  Medium: 25 plants (50%)
  Low:    10 plants (20%)

Average Score: 0.612
Median Score:  0.587
```

## Examples

### Example 1: Prioritize from Firecrawl Output

```bash
python -m prioritization.main \
    --input ../main.ipynb \
    --format notebook \
    --output results/ \
    --export-all \
    --verbose
```

### Example 2: Filter High Priority Plants

```bash
python -m prioritization.main \
    --input plants.json \
    --priority high \
    --min-score 0.75 \
    --output high_priority/ \
    --top 10
```

### Example 3: Custom Weights for Safety-Focused Research

```bash
python -m prioritization.main \
    --input plants.json \
    --ethnobotanical 0.25 \
    --efficacy 0.30 \
    --safety 0.35 \
    --feasibility 0.10 \
    --output safety_focused/
```

### Example 4: Python API with Filtering

```python
from prioritization import load_plants, prioritize_plants, PriorityLevel

# Load and prioritize
plants = load_plants('plants.json')
report = prioritize_plants(plants)

# Get high priority plants with WHO priority pathogens
high_priority = [
    p for p in report.plant_scores
    if p.priority_level == PriorityLevel.HIGH
    and p.who_priority_pathogens > 0
]

print(f"Found {len(high_priority)} high priority plants with WHO pathogens")

for plant in high_priority:
    print(f"\n{plant.scientific_name}")
    print(f"  Score: {plant.total_score:.3f}")
    print(f"  WHO Pathogens: {plant.who_priority_pathogens}")
    print(f"  AMR Strains: {plant.amr_strain_count}")
    print(f"  Antimicrobial: {plant.antimicrobial_score.justification}")
```

## CLI Reference

```
usage: main.py [-h] --input INPUT [--format {json,csv,notebook,auto}]
               [--output OUTPUT] [--export-format {json,csv,markdown,all}]
               [--export-all] [--top TOP] [--min-score MIN_SCORE]
               [--priority {high,medium,low}] [--min-pathogens MIN_PATHOGENS]
               [--min-mic MIN_MIC] [--ethnobotanical ETHNOBOTANICAL]
               [--efficacy EFFICACY] [--safety SAFETY]
               [--feasibility FEASIBILITY] [--verbose] [--quiet]
               [--no-summary]

Options:
  -h, --help            Show help message
  -i, --input INPUT     Input file path (JSON, CSV, or .ipynb)
  -f, --format          Input format (json, csv, notebook, auto)
  -o, --output OUTPUT   Output directory
  --export-format       Export format (json, csv, markdown, all)
  --export-all          Export in all formats
  -t, --top TOP         Only export top N plants
  --min-score           Minimum score threshold
  --priority            Filter by priority level
  --min-pathogens       Minimum number of pathogens (default: 1)
  --min-mic             Minimum MIC values required (default: 0)
  --ethnobotanical      Ethnobotanical weight (default: 0.30)
  --efficacy            Efficacy weight (default: 0.40)
  --safety              Safety weight (default: 0.20)
  --feasibility         Feasibility weight (default: 0.10)
  -v, --verbose         Verbose output
  -q, --quiet           Suppress console output
  --no-summary          Skip printing summary
```

## Project Structure

```
prioritization/
├── __init__.py           # Package initialization
├── config.py             # Configuration and constants
├── models.py             # Pydantic data models
├── scoring.py            # Scoring algorithms
├── data_loader.py        # Data loading and normalization
├── prioritize.py         # Main prioritization engine
├── report.py             # Report generation
├── main.py               # CLI interface
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Algorithm Version

**Version**: 1.0.0  
**Date**: March 2026  
**Authors**: Acaiberry Technologies / Lacuna Project Team

## Citation

If you use this prioritization framework in your research, please cite:

```
Lacuna Plant Prioritization Algorithm v1.0
Acaiberry Technologies (2026)
Comprehensive Prioritization Framework for AI-Driven Discovery of 
Novel Antimicrobial Agents from Medicinal Plants
```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: [repository link]
- Email: [contact email]
- Documentation: [docs link]

## Changelog

### v1.0.0 (2026-03-09)
- Initial release
- Multi-criteria scoring system
- Support for JSON, CSV, and notebook inputs
- Multiple export formats
- CLI and Python API
- WHO priority pathogen weighting
- AMR strain bonus scoring
- Comprehensive documentation
