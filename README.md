# 🚀 SpaceX Stonks - Stock Compensation Tracker

A comprehensive web application for tracking SpaceX stock compensation packages, including RSUs, ISOs, ESPP, and various grant types with automatic vesting schedule calculations.

## Features

✨ **Complete Grant Management**
- Track New Hire, Annual Performance, Promotion, Kickass, ESPP, and nqESPP grants
- Support for RSU, ISO (5-year/6-year), and Cash compensation
- Automatic vesting schedule calculation with cliff periods
- Semi-annual and monthly vesting support

📊 **Dashboard & Analytics**
- Real-time portfolio valuation
- Upcoming vest notifications
- Complete vesting schedule timeline
- Stock price history with charts

💼 **Tax Management**
- Track cash-to-cover vs shares-sold-to-cover
- Calculate vest values at different stock prices
- Historical tracking of vested shares

🔐 **Security & Access**
- User authentication with password encryption
- Admin panel for stock price management
- User data isolation and privacy
- Password reset functionality

🎨 **Modern UI**
- Dark theme with vibrant accent colors
- Responsive design for all devices
- Chart.js integration for visualizations
- Robinhood-inspired interface

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd stonks
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```
   
   Or manually create `.env` file from `.env.example` and update values.

### Running the Application

**Development mode:**
```bash
python main.py
```

The application will start at `http://127.0.0.1:5000`

**Default admin credentials:**
- Username: `admin`
- Password: `admin`

**Production mode:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## Usage Guide

### For Employees

1. **Register an account** - Create your user account
2. **Add grants** - Input your stock grants with:
   - Grant date
   - Grant type (New Hire, Bonus, etc.)
   - Share type (RSU, ISO, Cash)
   - Share quantity
3. **View dashboard** - See your total value and upcoming vests
4. **Track vesting** - Monitor your complete vesting schedule
5. **Manage taxes** - Record cash-to-cover or shares-sold decisions

### For Admins

1. **Login with admin credentials**
2. **Manage stock prices:**
   - Add new valuations
   - View price history chart
   - Update pricing as needed
3. **View users** - Monitor registered users

## Grant Types Explained

### New Hire Grant
- **Structure:** 5-year vest with 1-year cliff
- **Frequency:** Semi-annual (June 15 & November 15)
- **Type:** RSUs

### Annual Performance (Bonus)
- **Short Term:** 1-year cliff, paid all at once (RSU or Cash)
- **Long Term:** Options include:
  - RSU: Semi-annual with 1.5-year total cliff
  - ISO 5-Year: 2x shares, monthly vest, 1.5-year cliff
  - ISO 6-Year: 3x shares, monthly vest, 2.5-year cliff (0.5 initial)

### Promotion
- Same structure as New Hire grant

### Kickass Bonus
- **Structure:** 1-5 years (configurable)
- **Frequency:** Semi-annual
- **Cliff:** 1 year

### ESPP / nqESPP
- **Frequency:** Immediate (May 15 or October 15)
- **ESPP:** 15% discount
- **nqESPP:** No discount

## Project Structure

```
stonks/
├── app/
│   ├── models/              # Database models
│   │   ├── user.py         # User authentication
│   │   ├── grant.py        # Stock grants
│   │   ├── vest_event.py   # Vesting events
│   │   └── stock_price.py  # Stock valuations
│   ├── routes/             # Application routes
│   │   ├── auth.py         # Authentication
│   │   ├── main.py         # Dashboard
│   │   ├── grants.py       # Grant management
│   │   └── admin.py        # Admin panel
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, images
│   ├── utils/              # Helper functions
│   │   ├── vest_calculator.py  # Vesting logic
│   │   └── init_db.py      # Database initialization
│   └── __init__.py         # App factory
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md

```

## Technology Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Database:** SQLite (development), PostgreSQL-ready
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Charts:** Chart.js
- **Security:** Werkzeug password hashing, CSRF protection

## Development

**Run tests:**
```bash
pytest
```

**Code formatting:**
```bash
black app/
flake8 app/
```

## Deployment

### Heroku

```bash
# Create Procfile
echo "web: gunicorn main:app" > Procfile

# Deploy
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key-here
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Docker

```bash
# Build image
docker build -t spacex-stonks .

# Run container
docker run -p 5000:5000 -e SECRET_KEY=your-key spacex-stonks
```

## Security Notes

- Change the default admin password immediately in production
- Use a strong SECRET_KEY in production
- Enable HTTPS in production
- Configure proper email settings for password reset
- Consider using PostgreSQL instead of SQLite for production
- Implement rate limiting for authentication endpoints

## Contributing

This project was built based on detailed SpaceX stock compensation requirements. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Private project - All rights reserved

## Support

For questions or issues, please contact the repository owner.

---

**Built with ❤️ for SpaceX employees to better understand their stock compensation**
