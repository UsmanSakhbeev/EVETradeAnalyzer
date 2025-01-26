# EVE Online Price Analysis

This project is a web application designed to help players of **EVE Online** analyze prices of goods in the main trade hub, **Jita IV - Moon 4 - Caldari Navy Assembly Plant**. The application monitors the market, identifies profitable items listed for sale at significantly lower prices than the average or expected market value, and provides a user-friendly interface for this analysis.

## Features

- **Market Analysis**: Automatically collects and processes market data from the main trade hub.
- **Profit Identification**: Highlights items that are priced below their average market value.
- **Data Storage**: Uses PostgreSQL for storing and processing large volumes of data.
- **User Interface**: Provides an accessible web interface for interacting with the analysis results.
- **Deployment with Docker**: The entire application is containerized and deployed using Docker for portability and scalability.

## Technologies Used

- **Backend**: Python, Django
- **Database**: PostgreSQL
- **Deployment**: Docker
- **Frontend**: HTML/CSS (Django templates)

## Deployment
The application is deployed and accessible at the following link:
[http://195.80.50.122:8000/](http://195.80.50.122:8000/)

## How to Run Locally

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Set up your environment:
   - Install Docker if not already installed.
   - Create a `.env` file for environment variables (e.g., database credentials).

3. Build and run the application:
   ```bash
   docker-compose up --build
   ```

4. Access the application at:
   ```
   http://localhost:8000/
   ```

## Future Enhancements

- Add functionality to calculate and display optimal trade routes.
- Expand analysis to multiple regions and planets.
- Integrate user authentication for personalized settings.

## Feedback
Your feedback is highly appreciated! If you encounter any issues or have suggestions for improvement, please reach out.

---

Enjoy your trading in EVE Online! 🚀
