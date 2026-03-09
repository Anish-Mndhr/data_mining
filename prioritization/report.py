"""
Report generation and visualization utilities.

Generates comprehensive reports in multiple formats:
- JSON: Structured data export
- CSV: Tabular format for spreadsheets
- HTML: Interactive web report
- Markdown: Documentation-friendly format
- Charts: Visual analytics
"""

import json
import csv
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from .models import PrioritizationReport, PrioritizationScore, PriorityLevel


def export_to_json(
    report: PrioritizationReport,
    output_path: Union[str, Path],
    indent: int = 2,
    include_details: bool = True
) -> None:
    """
    Export prioritization report to JSON file.
    
    Args:
        report: PrioritizationReport object
        output_path: Output file path
        indent: JSON indentation level
        include_details: Include detailed scoring breakdown
    """
    data = {
        "metadata": {
            "generated_at": report.generated_at.isoformat(),
            "version": report.version,
            "total_plants": report.total_plants,
        },
        "summary": {
            "high_priority": report.high_priority_count,
            "medium_priority": report.medium_priority_count,
            "low_priority": report.low_priority_count,
            "average_score": round(report.average_score, 3),
            "median_score": round(report.median_score, 3),
        },
        "configuration": report.config,
        "plants": []
    }
    
    for plant in report.plant_scores:
        plant_data = {
            "rank": plant.rank,
            "scientific_name": plant.scientific_name,
            "local_name": plant.local_name,
            "total_score": round(plant.total_score, 3),
            "priority_level": plant.priority_level.value,
            "percentile": round(plant.percentile, 1) if plant.percentile else None,
            "scores": {
                "ethnobotanical": round(plant.ethnobotanical_score.score, 3),
                "antimicrobial": round(plant.antimicrobial_score.score, 3),
                "safety": round(plant.safety_score.score, 3),
                "feasibility": round(plant.feasibility_score.score, 3),
            },
            "metrics": {
                "pathogen_count": plant.pathogen_count,
                "mic_count": plant.mic_count,
                "who_priority_pathogens": plant.who_priority_pathogens,
                "amr_strain_count": plant.amr_strain_count,
            }
        }
        
        if include_details:
            plant_data["score_details"] = {
                "ethnobotanical": {
                    "score": round(plant.ethnobotanical_score.score, 3),
                    "weight": plant.ethnobotanical_score.weight,
                    "weighted_score": round(plant.ethnobotanical_score.weighted_score, 3),
                    "justification": plant.ethnobotanical_score.justification,
                    "details": plant.ethnobotanical_score.details,
                },
                "antimicrobial": {
                    "score": round(plant.antimicrobial_score.score, 3),
                    "weight": plant.antimicrobial_score.weight,
                    "weighted_score": round(plant.antimicrobial_score.weighted_score, 3),
                    "justification": plant.antimicrobial_score.justification,
                    "details": plant.antimicrobial_score.details,
                },
                "safety": {
                    "score": round(plant.safety_score.score, 3),
                    "weight": plant.safety_score.weight,
                    "weighted_score": round(plant.safety_score.weighted_score, 3),
                    "justification": plant.safety_score.justification,
                    "details": plant.safety_score.details,
                },
                "feasibility": {
                    "score": round(plant.feasibility_score.score, 3),
                    "weight": plant.feasibility_score.weight,
                    "weighted_score": round(plant.feasibility_score.weighted_score, 3),
                    "justification": plant.feasibility_score.justification,
                    "details": plant.feasibility_score.details,
                }
            }
        
        data["plants"].append(plant_data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)


def export_to_csv(
    report: PrioritizationReport,
    output_path: Union[str, Path],
    include_justifications: bool = False
) -> None:
    """
    Export prioritization report to CSV file.
    
    Args:
        report: PrioritizationReport object
        output_path: Output file path
        include_justifications: Include scoring justifications
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'rank',
            'scientific_name',
            'local_name',
            'total_score',
            'priority_level',
            'percentile',
            'ethnobotanical_score',
            'antimicrobial_score',
            'safety_score',
            'feasibility_score',
            'pathogen_count',
            'mic_count',
            'who_priority_pathogens',
            'amr_strain_count',
        ]
        
        if include_justifications:
            fieldnames.extend([
                'ethnobotanical_justification',
                'antimicrobial_justification',
                'safety_justification',
                'feasibility_justification',
            ])
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for plant in report.plant_scores:
            row = {
                'rank': plant.rank,
                'scientific_name': plant.scientific_name,
                'local_name': plant.local_name or '',
                'total_score': round(plant.total_score, 3),
                'priority_level': plant.priority_level.value,
                'percentile': round(plant.percentile, 1) if plant.percentile else '',
                'ethnobotanical_score': round(plant.ethnobotanical_score.score, 3),
                'antimicrobial_score': round(plant.antimicrobial_score.score, 3),
                'safety_score': round(plant.safety_score.score, 3),
                'feasibility_score': round(plant.feasibility_score.score, 3),
                'pathogen_count': plant.pathogen_count,
                'mic_count': plant.mic_count,
                'who_priority_pathogens': plant.who_priority_pathogens,
                'amr_strain_count': plant.amr_strain_count,
            }
            
            if include_justifications:
                row.update({
                    'ethnobotanical_justification': plant.ethnobotanical_score.justification,
                    'antimicrobial_justification': plant.antimicrobial_score.justification,
                    'safety_justification': plant.safety_score.justification,
                    'feasibility_justification': plant.feasibility_score.justification,
                })
            
            writer.writerow(row)


def export_to_markdown(
    report: PrioritizationReport,
    output_path: Union[str, Path],
    top_n: Optional[int] = None
) -> None:
    """
    Export prioritization report to Markdown file.
    
    Args:
        report: PrioritizationReport object
        output_path: Output file path
        top_n: Only include top N plants (None = all)
    """
    plants_to_show = report.plant_scores[:top_n] if top_n else report.plant_scores
    
    md_content = f"""# Plant Prioritization Report

**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Algorithm Version:** {report.version}  
**Total Plants Analyzed:** {report.total_plants}

## Executive Summary

### Priority Distribution
- 🔴 **High Priority:** {report.high_priority_count} plants
- 🟡 **Medium Priority:** {report.medium_priority_count} plants
- ⚪ **Low Priority:** {report.low_priority_count} plants

### Score Statistics
- **Average Score:** {report.average_score:.3f}
- **Median Score:** {report.median_score:.3f}

---

## Prioritized Plants

| Rank | Plant | Local Name | Score | Priority | Ethnobotanical | Antimicrobial | Safety | Feasibility |
|------|-------|------------|-------|----------|----------------|---------------|--------|-------------|
"""
    
    for plant in plants_to_show:
        priority_emoji = {
            PriorityLevel.HIGH: "🔴",
            PriorityLevel.MEDIUM: "🟡",
            PriorityLevel.LOW: "⚪",
        }
        
        md_content += f"| {plant.rank} | *{plant.scientific_name}* | {plant.local_name or '-'} | "
        md_content += f"{plant.total_score:.3f} | {priority_emoji[plant.priority_level]} {plant.priority_level.value.upper()} | "
        md_content += f"{plant.ethnobotanical_score.score:.3f} | {plant.antimicrobial_score.score:.3f} | "
        md_content += f"{plant.safety_score.score:.3f} | {plant.feasibility_score.score:.3f} |\n"
    
    md_content += f"""
---

## Detailed Scores

"""
    
    for plant in plants_to_show[:20]:  # Show details for top 20
        priority_emoji = {
            PriorityLevel.HIGH: "🔴",
            PriorityLevel.MEDIUM: "🟡",
            PriorityLevel.LOW: "⚪",
        }
        
        md_content += f"""
### {plant.rank}. *{plant.scientific_name}* {priority_emoji[plant.priority_level]}

**Local Name:** {plant.local_name or 'N/A'}  
**Total Score:** {plant.total_score:.3f} | **Percentile:** {plant.percentile:.1f}%  
**Priority Level:** {plant.priority_level.value.upper()}

#### Category Scores

| Category | Score | Weight | Weighted | Justification |
|----------|-------|--------|----------|---------------|
| Ethnobotanical | {plant.ethnobotanical_score.score:.3f} | {plant.ethnobotanical_score.weight} | {plant.ethnobotanical_score.weighted_score:.3f} | {plant.ethnobotanical_score.justification} |
| Antimicrobial | {plant.antimicrobial_score.score:.3f} | {plant.antimicrobial_score.weight} | {plant.antimicrobial_score.weighted_score:.3f} | {plant.antimicrobial_score.justification} |
| Safety | {plant.safety_score.score:.3f} | {plant.safety_score.weight} | {plant.safety_score.weighted_score:.3f} | {plant.safety_score.justification} |
| Feasibility | {plant.feasibility_score.score:.3f} | {plant.feasibility_score.weight} | {plant.feasibility_score.weighted_score:.3f} | {plant.feasibility_score.justification} |

#### Metrics
- **Pathogens Tested:** {plant.pathogen_count}
- **MIC Values:** {plant.mic_count}
- **WHO Priority Pathogens:** {plant.who_priority_pathogens}
- **AMR Strains:** {plant.amr_strain_count}

---
"""
    
    md_content += """
## Methodology

This prioritization framework evaluates medicinal plants using a comprehensive multi-criteria scoring system:

### Scoring Categories

1. **Ethnobotanical Validation (30%)**
   - Informant Consensus Factor (ICF)
   - Traditional usage breadth
   - Cultural validation

2. **Antimicrobial Efficacy (40%)**
   - MIC potency (lower is better)
   - Pathogen spectrum breadth
   - MBC/MIC ratio (bactericidal vs bacteriostatic)
   - Activity against AMR strains

3. **Safety Profile (20%)**
   - Toxicity data
   - Preparation method safety
   - Adverse effects

4. **Research Feasibility (10%)**
   - Geographic availability in Nepal
   - Parts accessibility
   - Cultivation potential
   - Seasonal availability

### Priority Levels

- **High Priority (≥0.70):** Excellent candidates for immediate research
- **Medium Priority (0.50-0.69):** Promising candidates worth investigating
- **Low Priority (<0.50):** Lower confidence or limited data

---

*Report generated by Lacuna Prioritization Algorithm v{report.version}*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)


def generate_summary_text(report: PrioritizationReport, top_n: int = 10) -> str:
    """
    Generate a text summary of the prioritization report.
    
    Args:
        report: PrioritizationReport object
        top_n: Number of top plants to highlight
        
    Returns:
        Formatted text summary
    """
    summary = f"""
PLANT PRIORITIZATION SUMMARY
{'='*80}

Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
Algorithm Version: {report.version}
Total Plants Analyzed: {report.total_plants}

PRIORITY DISTRIBUTION
{'-'*80}
High Priority:   {report.high_priority_count:3d} plants ({report.high_priority_count/report.total_plants*100:.1f}%)
Medium Priority: {report.medium_priority_count:3d} plants ({report.medium_priority_count/report.total_plants*100:.1f}%)
Low Priority:    {report.low_priority_count:3d} plants ({report.low_priority_count/report.total_plants*100:.1f}%)

SCORE STATISTICS
{'-'*80}
Average Score: {report.average_score:.3f}
Median Score:  {report.median_score:.3f}

TOP {top_n} PLANTS
{'-'*80}
"""
    
    for i, plant in enumerate(report.plant_scores[:top_n], 1):
        priority_symbol = {
            PriorityLevel.HIGH: "★",
            PriorityLevel.MEDIUM: "◆",
            PriorityLevel.LOW: "○",
        }
        
        summary += f"\n{i:2d}. {priority_symbol[plant.priority_level]} {plant.scientific_name}"
        if plant.local_name:
            summary += f" ({plant.local_name})"
        summary += f"\n    Score: {plant.total_score:.3f} | Priority: {plant.priority_level.value.upper()}"
        summary += f"\n    Ethnobotanical: {plant.ethnobotanical_score.score:.3f} | "
        summary += f"Antimicrobial: {plant.antimicrobial_score.score:.3f} | "
        summary += f"Safety: {plant.safety_score.score:.3f} | "
        summary += f"Feasibility: {plant.feasibility_score.score:.3f}"
        summary += f"\n    Pathogens: {plant.pathogen_count} | MIC values: {plant.mic_count}"
        summary += "\n"
    
    summary += f"\n{'='*80}\n"
    
    return summary


def print_report_summary(report: PrioritizationReport, top_n: int = 10) -> None:
    """
    Print a formatted summary to console.
    
    Args:
        report: PrioritizationReport object
        top_n: Number of top plants to display
    """
    print(generate_summary_text(report, top_n))


def export_all_formats(
    report: PrioritizationReport,
    output_dir: Union[str, Path],
    base_name: str = "prioritization_report"
) -> Dict[str, Path]:
    """
    Export report in all available formats.
    
    Args:
        report: PrioritizationReport object
        output_dir: Output directory
        base_name: Base filename (without extension)
        
    Returns:
        Dictionary mapping format to output path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_with_timestamp = f"{base_name}_{timestamp}"
    
    output_files = {}
    
    # JSON (detailed)
    json_path = output_dir / f"{base_with_timestamp}.json"
    export_to_json(report, json_path, include_details=True)
    output_files['json'] = json_path
    
    # CSV
    csv_path = output_dir / f"{base_with_timestamp}.csv"
    export_to_csv(report, csv_path, include_justifications=True)
    output_files['csv'] = csv_path
    
    # Markdown
    md_path = output_dir / f"{base_with_timestamp}.md"
    export_to_markdown(report, md_path, top_n=None)
    output_files['markdown'] = md_path
    
    # Text summary
    txt_path = output_dir / f"{base_with_timestamp}_summary.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(generate_summary_text(report, top_n=20))
    output_files['text'] = txt_path
    
    return output_files
