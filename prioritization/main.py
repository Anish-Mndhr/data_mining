#!/usr/bin/env python3
"""
Plant Prioritization CLI

Command-line interface for the plant prioritization algorithm.

Usage:
    python main.py --input plants.json --output results/
    python main.py --input data.csv --format csv --top 20
    python main.py --input main.ipynb --format notebook --export-all
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .data_loader import load_plants, validate_plants
from .prioritize import prioritize_plants, get_summary_statistics
from .report import (
    export_to_json,
    export_to_csv,
    export_to_markdown,
    export_all_formats,
    print_report_summary,
)
from .config import (
    CATEGORY_WEIGHTS,
    PRIORITY_THRESHOLDS,
    PRIORITY_SCORE_WEIGHTS,
)


class _DefaultWeights:
    """Compatibility shim for projects that only define CATEGORY_WEIGHTS."""

    ethnobotanical = CATEGORY_WEIGHTS.get('ethnobotanical', 0.30)
    efficacy = CATEGORY_WEIGHTS.get('antimicrobial_efficacy', 0.40)
    safety = CATEGORY_WEIGHTS.get('safety', 0.20)
    feasibility = CATEGORY_WEIGHTS.get('feasibility', 0.10)


DEFAULT_WEIGHTS = _DefaultWeights()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Prioritize medicinal plants for antimicrobial research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Prioritize plants from JSON file
  python -m prioritization.main --input plants.json --output results/
  
  # Prioritize from CSV with top 20 results
  python -m prioritization.main --input data.csv --format csv --top 20
  
  # Export all formats
  python -m prioritization.main --input main.ipynb --export-all
  
  # Custom weights
  python -m prioritization.main --input plants.json --ethnobotanical 0.4 --efficacy 0.3
        """
    )
    
    # Input arguments
    parser.add_argument(
        '--input', '-i',
        default=None,
        help='Input file path (JSON, CSV, or .ipynb). If omitted, common defaults are auto-detected.'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv', 'notebook', 'auto'],
        default='auto',
        help='Input file format (default: auto-detect)'
    )
    
    # Output arguments
    parser.add_argument(
        '--output', '-o',
        default='prioritization/output_from_extraction',
        help='Output directory (default: prioritization/output_from_extraction)'
    )
    
    parser.add_argument(
        '--export-format',
        choices=['json', 'csv', 'markdown', 'all'],
        default='csv',
        help='Export format (default: csv)'
    )
    
    parser.add_argument(
        '--export-all',
        action='store_true',
        help='Export in all formats'
    )
    
    parser.add_argument(
        '--top', '-t',
        type=int,
        default=10,
        help='Only export top N plants (default: 10)'
    )
    
    # Filtering arguments
    parser.add_argument(
        '--min-score',
        type=float,
        default=None,
        help='Minimum score threshold'
    )
    
    parser.add_argument(
        '--priority',
        choices=['high', 'medium', 'low'],
        default=None,
        help='Filter by priority level'
    )
    
    parser.add_argument(
        '--min-pathogens',
        type=int,
        default=1,
        help='Minimum number of pathogens tested (default: 1)'
    )
    
    parser.add_argument(
        '--min-mic',
        type=int,
        default=0,
        help='Minimum number of MIC values required (default: 0)'
    )
    
    # Scoring weight arguments
    parser.add_argument(
        '--ethnobotanical',
        type=float,
        default=DEFAULT_WEIGHTS.ethnobotanical,
        help=f'Ethnobotanical weight (default: {DEFAULT_WEIGHTS.ethnobotanical})'
    )
    
    parser.add_argument(
        '--efficacy',
        type=float,
        default=DEFAULT_WEIGHTS.efficacy,
        help=f'Antimicrobial efficacy weight (default: {DEFAULT_WEIGHTS.efficacy})'
    )
    
    parser.add_argument(
        '--safety',
        type=float,
        default=DEFAULT_WEIGHTS.safety,
        help=f'Safety profile weight (default: {DEFAULT_WEIGHTS.safety})'
    )
    
    parser.add_argument(
        '--feasibility',
        type=float,
        default=DEFAULT_WEIGHTS.feasibility,
        help=f'Research feasibility weight (default: {DEFAULT_WEIGHTS.feasibility})'
    )
    
    # Display arguments
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress console output'
    )
    
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Skip printing summary to console'
    )
    
    args = parser.parse_args()

    # Resolve input path when not explicitly provided.
    if args.input is None:
        default_candidates = [
            Path('extraction/plant_extraction_results.json'),
            Path('plant_extraction_results.json'),
        ]
        detected_input = next((str(p) for p in default_candidates if p.exists()), None)
        if detected_input is None:
            parser.error(
                "No input file provided and no default input found. "
                "Use --input <path> or place data at extraction/plant_extraction_results.json"
            )
        args.input = detected_input
    
    # Validate weights
    total_weight = args.ethnobotanical + args.efficacy + args.safety + args.feasibility
    if not (0.99 <= total_weight <= 1.01):
        print(f"Error: Weights must sum to 1.0, got {total_weight}", file=sys.stderr)
        sys.exit(1)
    
    # Update configuration
    CATEGORY_WEIGHTS['ethnobotanical'] = args.ethnobotanical
    CATEGORY_WEIGHTS['antimicrobial_efficacy'] = args.efficacy
    CATEGORY_WEIGHTS['safety'] = args.safety
    CATEGORY_WEIGHTS['feasibility'] = args.feasibility
    
    try:
        # Load plant data
        if not args.quiet:
            print(f"Loading plants from {args.input}...")
        
        input_format = None if args.format == 'auto' else args.format
        plants = load_plants(args.input, source_type=input_format)
        
        if not args.quiet:
            print(f"Loaded {len(plants)} plants")
        
        # Validate plants
        if not args.quiet:
            print("Validating plant data...")
        
        min_requirements = {
            'min_pathogens': args.min_pathogens,
            'min_mic_values': args.min_mic,
        }
        
        valid_plants = validate_plants(plants, min_requirements)
        
        if not valid_plants:
            print("Error: No plants meet minimum requirements", file=sys.stderr)
            sys.exit(1)
        
        if not args.quiet:
            print(f"{len(valid_plants)} plants meet minimum requirements")
            if len(valid_plants) < len(plants):
                print(f"Excluded {len(plants) - len(valid_plants)} plants")
        
        # Run prioritization
        if not args.quiet:
            print("\nRunning prioritization algorithm...")
        
        config = {
            'category_weights': CATEGORY_WEIGHTS.copy(),
            'priority_thresholds': PRIORITY_THRESHOLDS.copy(),
            'priority_score_weights': PRIORITY_SCORE_WEIGHTS.copy(),
        }
        
        report = prioritize_plants(valid_plants, config=config)
        
        if not args.quiet:
            print(f"Prioritization complete!")
            print(f"  High priority:   {report.high_priority_count} plants")
            print(f"  Medium priority: {report.medium_priority_count} plants")
            print(f"  Low priority:    {report.low_priority_count} plants")
        
        # Apply filters if specified
        plants_to_export = report.plant_scores
        
        if args.min_score is not None:
            plants_to_export = [p for p in plants_to_export if p.total_score >= args.min_score]
            if not args.quiet:
                print(f"\nFiltered to {len(plants_to_export)} plants with score >= {args.min_score}")
        
        if args.priority:
            from .models import PriorityLevel
            level_map = {
                'high': PriorityLevel.HIGH,
                'medium': PriorityLevel.MEDIUM,
                'low': PriorityLevel.LOW,
            }
            plants_to_export = [p for p in plants_to_export if p.priority_level == level_map[args.priority]]
            if not args.quiet:
                print(f"Filtered to {len(plants_to_export)} {args.priority} priority plants")
        
        if args.top:
            plants_to_export = plants_to_export[:args.top]
            if not args.quiet:
                print(f"Limiting to top {args.top} plants")
        
        # Create filtered report
        from .models import PrioritizationReport
        filtered_report = PrioritizationReport(
            total_plants=len(plants_to_export),
            plant_scores=plants_to_export,
            config=config,
        )
        
        # Print summary
        if not args.no_summary and not args.quiet:
            print("\n" + "="*80)
            print_report_summary(filtered_report, top_n=10)
        
        # Export results
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not args.quiet:
            print(f"\nExporting results to {output_dir}/")
        
        if args.export_all or args.export_format == 'all':
            output_files = export_all_formats(filtered_report, output_dir)
            if not args.quiet:
                print("Exported files:")
                for fmt, path in output_files.items():
                    print(f"  {fmt:10s}: {path}")
        else:
            if args.export_format == 'json':
                output_file = output_dir / "prioritization_report.json"
                export_to_json(filtered_report, output_file, include_details=True)
            elif args.export_format == 'csv':
                output_file = output_dir / "prioritization_report.csv"
                export_to_csv(filtered_report, output_file, include_justifications=True)
            elif args.export_format == 'markdown':
                output_file = output_dir / "prioritization_report.md"
                export_to_markdown(filtered_report, output_file, top_n=args.top)
            
            if not args.quiet:
                print(f"Exported: {output_file}")
        
        # Print statistics
        if args.verbose and not args.quiet:
            print("\n" + "="*80)
            print("DETAILED STATISTICS")
            print("="*80)
            stats = get_summary_statistics(filtered_report)
            import json
            print(json.dumps(stats, indent=2))
        
        if not args.quiet:
            print("\n✓ Prioritization complete!")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
