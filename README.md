# Firecrawl Antimicrobial Data Extraction (Python)

Extract detailed pharmacological and antimicrobial data for medicinal plants from Nepal using the Firecrawl Python SDK with Pydantic schema validation.

## Features

- **Structured Data Extraction**: Uses Pydantic models for type-safe data validation
- **Comprehensive Data Points**: Extracts botanical metadata, geographic information, and detailed antimicrobial assay results
- **Pathogen-Specific Data**: Captures MIC, ZOI, MBC, and assay details for multiple pathogens
- **Citation Tracking**: Each data point includes source URL citations
- **Agent-based Extraction**: Leverages Firecrawl's AI agent for intelligent data gathering

## Prerequisites

- Python 3.8 or higher
- Firecrawl API key (get one at [firecrawl.dev](https://firecrawl.dev))

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Update your API key in the notebook or create an environment variable:

```python
app = FirecrawlApp(api_key="your-api-key-here")
```

## Usage

### Running the Notebook

Open `main.ipynb` in Jupyter Notebook or VS Code and run the cells sequentially.

The notebook:

1. Imports required libraries (firecrawl, pydantic, typing)
2. Initializes the Firecrawl app with your API key
3. Defines the extraction schema with all required fields
4. Executes the agent with a detailed prompt
5. Outputs the extracted data in JSON format

### Example

```python
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Dict

app = FirecrawlApp(api_key="your-api-key")

class ExtractSchema(BaseModel):
    scientific_name: str
    local_name: str
    family: str
    pathogen_data: List[Dict]
    # ... other fields

result = app.agent(
    schema=ExtractSchema,
    prompt="Extract antimicrobial data for Swertia chirata from Nepal...",
    model="spark-1-mini"
)

print(result.model_dump_json(indent=2))
```

## Data Schema

The extraction schema captures:

### Ethnobotanical Metadata

- Scientific name, local name, family, genus
- Growth form and location in Nepal
- Traditional usage and cultural consensus index (ICF)

### Extraction & Preparation

- Preparation solvent and method
- Extraction solvent
- Compound class
- Plant parts with antimicrobial activity

### Antimicrobial Data (per pathogen)

- Pathogen tested (e.g., S. aureus, P. aeruginosa, K. pneumoniae, E. coli)
- Minimum Inhibitory Concentration (MIC)
- Minimum Bactericidal Concentration (MBC)
- Zone of Inhibition (ZOI)
- Assay method
- Source URL citations

## Project Structure

```
firecrawl/
├── main.ipynb           # Main extraction notebook
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Output Format

The agent returns structured JSON data:

```json
{
  "scientific_name": "Swertia chirata",
  "local_name": "Chiraito",
  "family": "Gentianaceae",
  "location_found_nepal": "Eastern Himalayas",
  "pathogen_data": [
    {
      "pathogen": "Staphylococcus aureus",
      "mic": "125 μg/mL",
      "mbc": "250 μg/mL",
      "zoi": "18 mm",
      "assay_type": "Disc diffusion",
      "source_url": "https://..."
    }
  ]
}
```

## Customization

### Change Target Plant

Modify the prompt in the agent call:

```python
prompt="Extract detailed pharmacological data for [Your Plant Name]..."
```

### Add/Remove Fields

Update the `ExtractSchema` class to include or exclude fields as needed.

### Change Model

Available models: `spark-1-mini`, `spark-1`, etc.

```python
result = app.agent(schema=ExtractSchema, prompt="...", model="spark-1")
```

## Notes

- Each agent call consumes Firecrawl API credits
- Results depend on available online scientific sources
- Data accuracy depends on source material quality
- Manual verification recommended for research purposes
- The agent searches globally for antimicrobial data but focuses on Nepal for ethnobotanical metadata

## License

MIT

## Support

For issues with:

- Firecrawl API: Visit [firecrawl.dev](https://firecrawl.dev)
- This notebook: Create an issue in the repository
# data_mining
