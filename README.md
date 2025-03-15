# ETF Investment Strategy Application

This web application helps you analyze ETF investment strategies using historical data. You can visualize ETF price charts, implement moving average strategies, and track the performance of periodic investments.

## Features

- Selection of various MSCI ETFs including MSCI World and Emerging Markets
- Weekly candlestick display of ETF prices
- Moving average visualization and strategy implementation
- Monthly investment simulation with customizable parameters
- Portfolio value tracking over time
- Performance metrics calculation

## Installation and Setup

### Option 1: Local Development

1. Clone this repository:
   ```
   git clone <repository-url>
   cd etf-investment-app
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

### Option 2: Docker Deployment

1. Build the Docker image:
   ```
   docker build -t etf-investment-app .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 etf-investment-app
   ```

3. Access the application at `http://localhost:5000`

### Option 3: Cloud Deployment

#### Heroku Deployment

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku and create a new app:
   ```
   heroku login
   heroku create etf-investment-app
   ```

3. Deploy the application:
   ```
   git push heroku main
   ```

4. Open the application:
   ```
   heroku open
   ```

## Usage Instructions

1. **Select ETF**: Choose from the available MSCI ETFs in the dropdown menu
2. **Set Investment Parameters**:
   - Enter the monthly investment amount in Euros
   - Select a start date for your investment timeline
   - Define the moving average length in weeks
   - Choose whether to use the moving average strategy

3. **Calculate Strategy**: Click the "Calculate Strategy" button to run the simulation

4. **Analyze Results**:
   - View the ETF price chart with moving average overlay
   - Track portfolio value over time compared to total investment
   - Review performance metrics in the results card

## Moving Average Strategy Explained

When the "Use Moving Average Strategy" option is enabled:
- If the ETF price is above the moving average, the monthly investment amount is used to purchase ETF shares
- If the ETF price is below the moving average, the monthly investment amount is kept as cash
- This strategy aims to avoid buying during downtrends and accumulate cash for better buying opportunities

## Technical Implementation

- **Backend**: Flask (Python)
- **Data Source**: Yahoo Finance API via yfinance
- **Frontend**: HTML, Bootstrap, Chart.js
- **Deployment**: Docker, Gunicorn

## Future Enhancements

- Add support for ECB interest rates for cash holdings
- Implement comparison between multiple ETFs
- Add more investment strategies (e.g., value averaging)
- Enable custom investment schedules
- Incorporate dividend reinvestment calculations
- Add export functionality for analysis results
