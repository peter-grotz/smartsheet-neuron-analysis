# Smartsheet Neuron Reconstruction Analysis - Code Ocean Capsule

[![Code Ocean](https://codeocean.com/codeocean-assets/badge/open-in-code-ocean.svg)](https://codeocean.com)

A comprehensive analysis tool for neuron reconstruction data stored in Smartsheet, designed for seamless integration with Code Ocean capsules.

## Overview

This tool analyzes neuron reconstruction data by soma location, providing detailed statistics and interactive visualizations. It supports filtering by HIVE status and can analyze specific brain regions or all locations together.

**Key Features:**
- Soma location-based analysis (VM, PVT, LC, etc.)
- HIVE filtering for specialized cell types  
- "All" option to analyze all neurons regardless of location
- Interactive and programmatic execution modes
- Comprehensive CSV reports and interactive plots
- Code Ocean App Builder integration

## Code Ocean Implementation Guide

### Capsule Structure

This repository is already organized in the Code Ocean-compatible structure:

```
smartsheet_api_search/
├── code/                           # All Python scripts
│   ├── run                        # Main entry point (shell script)
│   ├── run_analysis.py           # Interactive entry point
│   ├── app_analysis.py           # App Builder entry point
│   ├── main.py                   # Core application logic
│   ├── soma_analyzer.py          # Analysis engine
│   ├── smartsheet_client.py      # Smartsheet API client
│   ├── visualizer.py             # Plotting functionality
│   ├── data_processor.py         # Data processing utilities
│   ├── interactive_soma_analysis.py  # Interactive CLI
│   └── config.py                 # Configuration management
├── environment/
│   └── requirements.txt          # Python dependencies
├── metadata/
│   └── metadata.yml              # Capsule metadata and App Builder config
├── README.md                     # This file
├── QUICK_REFERENCE.md            # App Builder parameter examples
└── env_example.txt               # Environment variable template
```

### Setting Up Your Code Ocean Capsule

#### Method 1: Clone from GitHub (Recommended)

1. **Push to GitHub**: Push this repository to your GitHub account
2. **Create Capsule**: In Code Ocean, click "+" → "Clone from Git"
3. **Enter Repository URL**: Paste your GitHub repository URL
4. **Select Environment**: Choose "Python 3.9+" base environment

#### Method 2: Manual Upload

1. **Create New Capsule**: In Code Ocean, click "+" → "New Capsule"
2. **Select Environment**: Choose "Python 3.9+" base environment
3. **Upload Files**: Upload all files maintaining the directory structure above

### Environment Configuration

#### 1. Set Environment Variables

In your Code Ocean capsule, go to **Environment** → **Environment Variables** and add:

```
SMARTSHEET_ACCESS_TOKEN = your_actual_token_here
```

**To get your Smartsheet API token:**
1. Log in to Smartsheet
2. Go to Account → Apps & Integrations → API Access
3. Generate new access token
4. Copy and paste into Code Ocean

#### 2. Install Dependencies

Code Ocean will automatically install dependencies from `environment/requirements.txt`:
- smartsheet-python-sdk==3.0.3
- pandas==2.1.4
- matplotlib==3.8.2
- plotly==5.17.0
- python-dotenv==1.0.0
- requests==2.31.0
- numpy==1.24.3
- kaleido==0.2.1

#### 3. Verify Setup

Click **"Run"** in your Code Ocean capsule. You should see:
```
Code Ocean - Smartsheet Neuron Reconstruction Analysis
========================================================
Running in Code Ocean environment
Output will be saved to /results
Smartsheet Neuron Reconstruction Analysis Tool
```

### Using the Analysis Tool

#### Interactive Mode (Default)

When you run the capsule, it will prompt you for:

1. **Soma Location**: Enter brain region (e.g., "VM", "PVT", "LC") or "all" for all regions
2. **HIVE Filter**: Enter "yes" to filter for HIVE-marked cells only, "no" for all cells
3. **Plot Format**: Choose output format (svg, png, html)

Example interaction:
```
Enter soma location to analyze (or 'all' for all neurons): SI
Apply HIVE filter? (yes/no) [default: no]: yes
Select plot format (svg/png/html) [default: svg]: svg
```

#### App Builder Mode (Parameter Input)

The capsule includes App Builder integration for web-based parameter input.

**Available Parameters:**
```
--soma_location SI --hive_filter --plot_format svg
--soma_location all --plot_format html
--soma_location VM --hive_filter --plot_format png
--soma_location PVT LC --plot_format svg
```

**Parameter Reference:**
- `--soma_location`: Brain region(s) to analyze or "all"
- `--hive_filter`: Include this flag to filter for HIVE cells only
- `--plot_format`: Output format (svg, png, html) [default: svg]

See `QUICK_REFERENCE.md` for copy-paste examples.

### Output Files

All results are saved to `/results/` and include:

**CSV Files:**
- `soma_analysis_{LOCATION}_{TIMESTAMP}.csv` - Detailed analysis results
- `soma_analysis_{LOCATION}_HIVE_{TIMESTAMP}.csv` - HIVE-filtered results

**Visualization Files:**
- `soma_analysis_plot_{LOCATION}_{TIMESTAMP}.{format}` - Stacked bar charts
- Interactive plots showing neuron status distribution by sample

**Example Outputs:**
```
/results/
├── soma_analysis_SI_20240118_143022.csv
├── soma_analysis_SI_HIVE_20240118_143022.csv
├── soma_analysis_plot_SI_20240118_143022.svg
└── soma_analysis_plot_SI_HIVE_20240118_143022.svg
```

### Analysis Features

#### Soma Location Analysis
- Analyzes neuron reconstruction data by brain region
- Combines CCF and Manual soma compartment annotations
- Supports multiple region analysis and "all" regions option

#### HIVE Filtering
- Filters for cells marked as "HIVE" in the Smartsheet
- Boolean-based filtering (True/False values)
- Can be combined with any soma location analysis

#### Status Tracking
- **Completed**: Fully reconstructed neurons
- **Pending Review**: Awaiting quality control
- **In Progress**: Currently being reconstructed
- **Hold**: Temporarily paused
- **Untraceable**: Cannot be reconstructed
- **Incomplete**: Partial reconstruction

#### Sample-Level Aggregation
- Groups neurons by sample ID (extracted from cell IDs)
- Provides genotype and registration status information
- Calculates status distribution per sample

### Use Cases

**Research Applications:**
- Compare reconstruction progress across brain regions
- Analyze HIVE cell distribution and status
- Track genotype-specific reconstruction patterns
- Generate progress reports for reconstruction pipelines

**Quality Control:**
- Monitor reconstruction status across samples
- Identify bottlenecks in the reconstruction process
- Track completion rates by brain region

**Data Management:**
- Export structured data for further analysis
- Generate visualizations for presentations
- Maintain reproducible analysis workflows

### Data Requirements

Your Smartsheet must contain these columns:
- `ID`: Cell identifier (format: "N030-657676")
- `CCF Soma Compartment`: Brain region from atlas
- `Manual Estimated Soma Compartment`: Manually annotated region
- `Status 1`: Reconstruction status
- `Genotype`: Cell genotype information
- `Registered?`: Registration status
- `HIVE?`: Boolean column for HIVE marking (True/False)

### Code Ocean Best Practices

1. **Reproducibility**: All dependencies are locked to specific versions
2. **Documentation**: Comprehensive inline documentation and examples
3. **Error Handling**: Robust error messages and validation
4. **Output Management**: All results automatically saved to `/results/`
5. **Environment Validation**: Automatic checking of required tokens

### Troubleshooting

**Common Issues:**

1. **"SMARTSHEET_ACCESS_TOKEN not set"**
   - Add your token to Environment Variables in Code Ocean
   - Verify token has read access to your Smartsheet

2. **"No neurons found matching criteria"**
   - Check soma location spelling (case-insensitive)
   - Verify data exists in the specified Smartsheet
   - Try "all" to see available data

3. **"HIVE column not found"**
   - Ensure your Smartsheet has a column with "hive" in the name
   - Check that the column contains boolean True/False values

4. **Import Errors**
   - Verify all files are in the correct directories
   - Check that `requirements.txt` was processed correctly

### Support

For Code Ocean-specific issues:
- Check Code Ocean documentation: https://help.codeocean.com
- Verify capsule permissions and environment variables
- Ensure proper directory structure is maintained

For analysis questions:
- Review example outputs in `QUICK_REFERENCE.md`
- Check available soma locations in your data
- Verify Smartsheet column names and data types

---

**Ready to analyze your neuron reconstruction data in Code Ocean!** 