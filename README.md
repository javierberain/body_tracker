# Body Tracker Web App

A simple and elegant web application to track body composition measurements including weight, body fat percentage, lean mass, and body circumferences.

## Features

- **User Authentication**: Secure login system with password hashing
- **Data Entry**: Easy form to input measurements
- **Trend Visualization**: Interactive charts showing progress over time
- **Admin Panel**: Admin can view all users and manage accounts
- **Data Import**: Script to import historical data from Google Sheets

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js

## Local Setup

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the app**:
   - Open browser to `http://localhost:5000`
   - Default admin login:
     - Username: `admin`
     - Password: `admin123` (CHANGE THIS IMMEDIATELY)

## First Steps

1. **Login as admin** (admin/admin123)
2. **Change admin password** (use admin panel to create a new admin user, then delete the default one)
3. **Create user accounts** for your 3 users
4. **Import historical data** (see below)

## Importing Historical Data from Google Sheets

1. **Export your Google Sheet as CSV**
   - File → Download → CSV

2. **Ensure your CSV has these columns** (column names can vary slightly):
   - timestamp (or date)
   - weight
   - bmi
   - body_fat_percentage (or body_fat)
   - visceral_fat_index (or visceral_fat)
   - lean_mass_percentage (or lean_mass)
   - waist_circumference (or waist)
   - bicep_circumference (or bicep)
   - thigh_circumference (or thigh)
   - chest_circumference (or chest)

3. **Run the import script**:
   ```bash
   python import_data.py your_data.csv username
   ```

   Example:
   ```bash
   python import_data.py javier_data.csv javier
   ```

## Deploying Online (Free Options)

### Option 1: Render (Recommended)

1. **Create account** at [render.com](https://render.com)

2. **Push code to GitHub** (create a repo and push this code)

3. **Create new Web Service** on Render:
   - Connect your GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Set environment variable**:
   - Key: `SECRET_KEY`
   - Value: Generate a random string (e.g., using Python: `import secrets; print(secrets.token_hex(32))`)

5. **Deploy!** Render will give you a URL like `https://your-app.onrender.com`

### Option 2: Railway

1. **Create account** at [railway.app](https://railway.app)

2. **Create new project** from GitHub repo

3. **Set environment variables**:
   - `SECRET_KEY`: Random string

4. **Railway will auto-deploy** and provide a URL

### Option 3: PythonAnywhere

1. **Create account** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload files** via their interface

3. **Create web app** following their Flask setup guide

## Important Security Notes

1. **Change default admin password immediately**
2. **Set a strong SECRET_KEY** in production
3. **Use HTTPS** (Render/Railway provide this automatically)
4. **Regular backups**: Download the `body_tracker.db` file periodically

## Project Structure

```
body-tracker/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── import_data.py         # Data import script
├── body_tracker.db        # SQLite database (created on first run)
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── add_measurement.html
│   ├── trends.html
│   ├── admin.html
│   ├── create_user.html
│   └── view_user.html
└── static/
    └── css/
        └── style.css      # Styling
```

## Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- password_hash
- is_admin (Boolean)

### Measurements Table
- id (Primary Key)
- user_id (Foreign Key)
- timestamp
- weight
- bmi
- body_fat_percentage
- visceral_fat_index
- lean_mass_percentage
- waist_circumference
- bicep_circumference
- thigh_circumference
- chest_circumference

## Troubleshooting

**Can't login?**
- Make sure you created user accounts via admin panel
- Default admin: username `admin`, password `admin123`

**Import script fails?**
- Check CSV column names match expected format
- Ensure date format is recognized
- Look for error messages indicating which row failed

**Charts not showing?**
- Make sure you have at least 2 measurements entered
- Check browser console for JavaScript errors

## Future Enhancements (Optional)

- Export data to CSV
- Set goals and track progress
- Photo uploads for progress comparison
- Mobile app version
- Email notifications for logging reminders

## Support

For issues or questions, check the code comments or create an issue in the GitHub repository.
