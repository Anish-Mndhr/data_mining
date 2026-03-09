# Quick Start Guide - Plant Prioritization Algorithm

## Installation

```bash
# Navigate to prioritization directory
cd firecrawl/prioritization/

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Command Line (Simplest)

```bash
# Prioritize plants from Firecrawl output
python -m prioritization.main --input ../main.ipynb --output results/

# View top 10 plants only
python -m prioritization.main --input plants.json --top 10 --export-all

# Filter high priority plants
python -m prioritization.main --input data.csv --priority high --output high_priority/
```

### 2. Python Script

Create a file `run_prioritization.py`:

```python
from prioritization import load_plants, prioritize_plants, export_all_formats

# Load plant data
plants = load_plants('../main.ipynb', source_type='notebook')

# Run prioritization
report = prioritize_plants(plants)

# Print summary
print(f"Total plants: {report.total_plants}")
print(f"High priority: {report.high_priority_count}")

# Export results
export_all_formats(report, output_dir='results/')
print(f"\nResults saved to results/")
```

Run it:
```bash
python run_prioritization.py
```

### 3. Interactive (Jupyter Notebook)

Open `example_usage.ipynb` in Jupyter:

```bash
jupyter notebook example_usage.ipynb
```

## Common Tasks

### Task 1: Find High Priority Plants

```bash
python -m prioritization.main \
    --input plants.json \
    --priority high \
    --min-pathogens 3 \
    --output high_priority/
```

### Task 2: Custom Weights (Safety Focus)

```bash
python -m prioritization.main \
    --input plants.json \
    --ethnobotanical 0.25 \
    --efficacy 0.30 \
    --safety 0.35 \
    --feasibility 0.10 \
    --output safety_focused/
```

### Task 3: Filter by WHO Priority Pathogens

```python
from prioritization import load_plants, prioritize_plants

plants = load_plants('plants.json')
report = prioritize_plants(plants)

who_plants = [p for p in report.plant_scores if p.who_priority_pathogens > 0]
print(f"Plants with WHO priority pathogens: {len(who_plants)}")

for plant in who_plants[:10]:
    print(f"{plant.scientific_name}: {plant.who_priority_pathogens} WHO pathogens")
```

## Understanding Output

### Priority Levels
- **High (≥0.70)**: Excellent candidates → Immediate research
- **Medium (0.50-0.69)**: Promising candidates → Worth investigating  
- **Low (<0.50)**: Limited data or lower potential

### Score Components
Each plant gets scores in 4 categories:
1. **Ethnobotanical (30%)**: Traditional knowledge validation
2. **Antimicrobial (40%)**: Efficacy against pathogens
3. **Safety (20%)**: Toxicity and preparation safety
4. **Feasibility (10%)**: Geographic availability & accessibility

### Output Files
After running, you'll get:
- `prioritization_report_TIMESTAMP.json` - Detailed structured data
- `prioritization_report_TIMESTAMP.csv` - Spreadsheet format
- `prioritization_report_TIMESTAMP.md` - Human-readable report
- `prioritization_report_TIMESTAMP_summary.txt` - Quick overview

## Troubleshooting

### No module named 'pydantic'
```bash
pip install pydantic pandas numpy
```

### No plants in output
- Check minimum requirements (default: 1 pathogen, 0 MIC values)
- Reduce requirements: `--min-pathogens 0 --min-mic 0`

### Import errors
- Make sure you're running from correct directory
- Use module syntax: `python -m prioritization.main`
- Or run from parent: `cd firecrawl && python prioritization/script.py`

## Next Steps

1. **Review Results**: Check top 10 plants in markdown report
2. **Filter Data**: Use `--priority high` or `--min-score 0.70`
3. **Customize Weights**: Adjust to your research priorities
4. **Export**: Use `--export-all` for all formats

## Getting Help

```bash
# Show all options
python -m prioritization.main --help

# Run test
python prioritization/test_prioritization.py

# View example notebook
jupyter notebook example_usage.ipynb
```

## Example Output

```
PLANT PRIORITIZATION SUMMARY
================================================================================

Generated: 2026-03-09 13:35:05
Total Plants Analyzed: 25

PRIORITY DISTRIBUTION
--------------------------------------------------------------------------------
High Priority:     8 plants (32.0%)
Medium Priority:  12 plants (48.0%)
Low Priority:      5 plants (20.0%)

SCORE STATISTICS
--------------------------------------------------------------------------------
Average Score: 0.612
Median Score:  0.587

TOP 10 PLANTS
--------------------------------------------------------------------------------

 1. ★ Curcuma longa (Besar)
    Score: 0.823 | Priority: HIGH
    Ethnobotanical: 0.891 | Antimicrobial: 0.845 | Safety: 0.712 | Feasibility: 0.654
    Pathogens: 5 | MIC values: 5

 2. ★ Azadirachta indica (Neem)
    Score: 0.784 | Priority: HIGH
    ...
```

That's it! Start with the simple command line usage, then explore the Python API and notebook for more advanced features.
