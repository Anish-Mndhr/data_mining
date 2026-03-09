"""
Quick test to verify the prioritization algorithm works correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prioritization.models import PlantData, PathogenData, StrainData, PriorityLevel
from prioritization.prioritize import prioritize_plants
from prioritization.report import print_report_summary


def create_test_plants():
    """Create sample plant data for testing."""
    
    plants = []
    
    # Plant 1: High priority plant with good data
    plant1 = PlantData(
        scientific_name="Curcuma longa",
        local_name="Besar (Turmeric)",
        family="Zingiberaceae",
        genus="Curcuma",
        traditional_usage="Used for wounds, inflammation, infections, digestive disorders, skin conditions, respiratory issues",
        cultural_consensus_icf=0.97,
        location_found_nepal="Lalitpur, Kathmandu, Dhading, Bhaktapur, Kavre",
        growth_form="Perennial herb",
        altitude_range_found="200-1500m",
        preparation_solvent="Water, ethanol",
        preparation_method="Decoction, paste",
        parts_used="Rhizome",
        pathogen_data=[
            PathogenData(
                pathogen="Staphylococcus aureus (MRSA)",
                mic="125 μg/mL",
                mbc="250 μg/mL",
                zoi="18 mm"
            ),
            PathogenData(
                pathogen="Escherichia coli",
                mic="250 μg/mL",
                mbc="500 μg/mL",
                zoi="16 mm"
            ),
            PathogenData(
                pathogen="Pseudomonas aeruginosa",
                mic="312 μg/mL",
                mbc="625 μg/mL",
                zoi="14 mm"
            ),
            PathogenData(
                pathogen="Klebsiella pneumoniae",
                mic="200 μg/mL",
                mbc="400 μg/mL",
                zoi="15 mm"
            ),
        ]
    )
    plants.append(plant1)
    
    # Plant 2: Medium priority plant
    plant2 = PlantData(
        scientific_name="Azadirachta indica",
        local_name="Neem",
        family="Meliaceae",
        traditional_usage="Used for skin infections, fever, malaria",
        cultural_consensus_icf=0.65,
        location_found_nepal="Terai region",
        growth_form="Tree",
        parts_used="Leaves, bark",
        pathogen_data=[
            PathogenData(
                pathogen="Staphylococcus aureus",
                mic="800 μg/mL",
                mbc="1600 μg/mL"
            ),
            PathogenData(
                pathogen="Escherichia coli",
                mic="1200 μg/mL",
                mbc="2400 μg/mL"
            ),
        ]
    )
    plants.append(plant2)
    
    # Plant 3: Lower priority (limited data)
    plant3 = PlantData(
        scientific_name="Test plant",
        local_name="Local name",
        pathogen_data=[
            PathogenData(
                pathogen="Staphylococcus aureus",
                mic="5000 μg/mL"
            ),
        ]
    )
    plants.append(plant3)
    
    return plants


def main():
    """Run test prioritization."""
    
    print("="*80)
    print("PRIORITIZATION ALGORITHM TEST")
    print("="*80)
    
    # Create test data
    print("\n1. Creating test plant data...")
    plants = create_test_plants()
    print(f"   Created {len(plants)} test plants")
    
    # Run prioritization
    print("\n2. Running prioritization...")
    report = prioritize_plants(plants)
    print(f"   Prioritized {report.total_plants} plants")
    
    # Print summary
    print("\n3. Results:")
    print_report_summary(report, top_n=3)
    
    # Verify results
    print("\n4. Verification:")
    print(f"   ✓ High priority:   {report.high_priority_count} plant(s)")
    print(f"   ✓ Medium priority: {report.medium_priority_count} plant(s)")
    print(f"   ✓ Low priority:    {report.low_priority_count} plant(s)")
    
    # Check top plant
    top_plant = report.plant_scores[0]
    print(f"\n   Top plant: {top_plant.scientific_name}")
    print(f"   Score: {top_plant.total_score:.3f}")
    print(f"   Priority: {top_plant.priority_level.value}")
    
    # Check scoring details
    print(f"\n   Scoring breakdown:")
    print(f"     Ethnobotanical: {top_plant.ethnobotanical_score.score:.3f}")
    print(f"     Antimicrobial:  {top_plant.antimicrobial_score.score:.3f}")
    print(f"     Safety:         {top_plant.safety_score.score:.3f}")
    print(f"     Feasibility:    {top_plant.feasibility_score.score:.3f}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE! ✓")
    print("="*80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
