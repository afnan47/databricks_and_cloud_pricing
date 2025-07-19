# 💰 Databricks & Cloud Pricing Calculator

A modern web application for calculating combined AWS and Databricks pricing for your data engineering workloads.

## 🚀 Features

- **Real-time Pricing**: Get live pricing from Vantage API for AWS and Databricks pricing APIs
- **Smart Instance Selection**: Dropdown with 760+ AWS instance types with search and categorization
- **Multiple Instance Support**: Calculate costs for multiple instance types and configurations
- **Flexible Configuration**: Support for different compute types, plans, and regions
- **Visual Analytics**: Interactive charts and breakdowns of costs
- **Export Capabilities**: Export results to CSV or JSON formats
- **Modern UI**: Beautiful, responsive interface built with Streamlit

## 📋 Requirements

- Python 3.12+
- Vantage API token (for AWS pricing)
- Internet connection (for API calls)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd databricks_and_cloud_pricing
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Vantage API token:
   ```
   VANTAGE_API_TOKEN=your_vantage_api_token_here
   ```

## 🔑 Getting Your Vantage API Token

1. Visit [Vantage](https://www.vantage.sh/)
2. Sign up for a free account
3. Navigate to your API settings
4. Generate a new API token
5. Add the token to your `.env` file

## 🚀 Running the Application

### Option 1: Using Streamlit directly
```bash
streamlit run src/streamlit_app.py
```

### Option 2: Using the project script
```bash
uv run pricing-calculator
```

The application will open in your default browser at `http://localhost:8501`.

## 📖 Usage

### 1. Configure Your Settings
- **Cloud Provider**: Currently supports AWS (GCP and Azure coming soon)
- **Region**: Select your AWS region
- **Databricks Plan**: Choose Standard, Premium, or Enterprise
- **Compute Type**: Select Jobs Compute, All-Purpose Compute, SQL Compute, or ML Runtime

### 2. Enter Instance Details
- **Instance Type**: Use the dropdown to search and select from 760+ available AWS instance types
  - Type to search: Start typing to filter instance types
  - Categories: View instance types by category (General Purpose, Compute Optimized, Memory Optimized, etc.)
  - Instance Details: See detailed specifications when an instance type is selected
- **Number of Instances**: How many instances you'll run
- **Hours per Run**: How many hours per run the instances will run (max 168 hours = 1 week)

### 3. Calculate Pricing
Click "Calculate Pricing" to get your results. The application will:
- Fetch AWS pricing from Vantage API
- Fetch Databricks pricing from their public API
- Calculate combined costs
- Display detailed breakdowns

### 4. View Results
- **Summary Metrics**: Total costs, instance counts, and hours
- **Cost Breakdown**: Visual pie chart showing AWS vs Databricks costs
- **Detailed Table**: Complete breakdown of all costs
- **Export Options**: Download results as CSV or JSON

## 🧪 Testing

Run the test suite:
```bash
uv run pytest tests/
```

Run with coverage:
```bash
uv run pytest tests/ --cov=src --cov-report=html
```

## 📁 Project Structure

```
databricks_and_cloud_pricing/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main Streamlit application
│   ├── config.py            # Configuration and constants
│   ├── api_client.py        # API clients for Vantage and Databricks
│   ├── calculator.py        # Core pricing calculation logic
│   ├── utils.py             # Utility functions for export and formatting
│   ├── streamlit_app.py     # Streamlit entry point
│   └── aws.json            # AWS instance type data from Databricks API
├── tests/
│   └── test_calculator.py   # Unit tests
├── pyproject.toml           # Project configuration
├── env.example              # Environment variables template
└── README.md               # This file
```

## 📊 Instance Type Data

The application includes a comprehensive database of AWS instance types sourced from Databricks' pricing API. The data includes:

- **760+ Instance Types**: Complete list of available AWS instance types
- **Categorized Organization**: Instance types organized by purpose:
  - General Purpose (201 types)
  - Compute Optimized (110 types)
  - Memory Optimized (226 types)
  - Storage Optimized (32 types)
  - GPU Instances (20 types)
  - Other (171 types)
- **Detailed Specifications**: Each instance type includes specifications like vCPU, memory, storage, and pricing information
- **Search Functionality**: Type to search and filter instance types quickly

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VANTAGE_API_TOKEN` | Your Vantage API token | Required |
| `DEFAULT_REGION` | Default AWS region | `us-east-1` |
| `DEFAULT_COMPUTE_TYPE` | Default Databricks compute type | `Jobs Compute` |
| `DEFAULT_PLAN` | Default Databricks plan | `Enterprise` |

### Supported AWS Regions

- us-east-1 (N. Virginia)
- us-east-2 (Ohio)
- us-west-1 (N. California)
- us-west-2 (Oregon)
- eu-west-1 (Ireland)
- eu-central-1 (Frankfurt)
- ap-southeast-1 (Singapore)
- ap-northeast-1 (Tokyo)

### Supported Databricks Plans

- **Premium**: Advanced features and priority support
- **Enterprise**: Full enterprise features and dedicated support

### Supported Compute Types

- **Jobs Compute**: For batch processing jobs
- **All-Purpose Compute**: For interactive notebooks and jobs
- **SQL Compute**: For SQL analytics workloads
- **ML Runtime**: For machine learning workloads

## 🚧 Future Enhancements

- [ ] Support for GCP and Azure
- [ ] Excel export functionality
- [ ] Multiple tasks under Databricks jobs
- [ ] Cost optimization recommendations
- [ ] Historical pricing tracking
- [ ] Advanced filtering and search
- [ ] Bulk import/export capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check that your Vantage API token is valid
2. Ensure you have an internet connection for API calls
3. Verify your instance type is supported
4. Check the logs for detailed error messages

For additional help, please open an issue on GitHub.

## 🙏 Acknowledgments

- [Vantage](https://www.vantage.sh/) for providing AWS pricing data
- [Databricks](https://databricks.com/) for their public pricing APIs
- [Streamlit](https://streamlit.io/) for the web framework
- [Plotly](https://plotly.com/) for interactive visualizations