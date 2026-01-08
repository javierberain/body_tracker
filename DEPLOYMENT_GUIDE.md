# Body Tracker - Quick Deployment Guide

## 🚀 Get Your App Online in 15 Minutes

### Step 1: Test Locally First (5 minutes)

1. Open terminal/command prompt
2. Navigate to the project folder:
   ```bash
   cd body-tracker
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python app.py
   ```

5. Open browser to `http://localhost:5000`
6. Login with: username `admin`, password `admin123`

### Step 2: Prepare for Deployment

✅ **Change admin password immediately:**
1. Login as admin
2. Go to Admin Panel
3. Create a new admin user with a strong password
4. Logout and login with new admin
5. Delete the default admin user

✅ **Create your 3 user accounts:**
1. In Admin Panel, click "Create New User"
2. Set username and password (write them down!)
3. Repeat for all 3 users

### Step 3: Deploy to Render (10 minutes)

**Why Render?** Free tier, easy setup, automatic HTTPS, no credit card required.

1. **Create GitHub account** (if you don't have one)
   - Go to github.com
   - Sign up for free

2. **Create a new repository**
   - Click "New repository"
   - Name it "body-tracker"
   - Make it Private (keep your data secure)
   - Don't initialize with README
   - Click "Create repository"

3. **Upload your code to GitHub**
   
   Option A - Using GitHub web interface (easiest):
   - Click "uploading an existing file"
   - Drag all files from the body-tracker folder
   - Click "Commit changes"
   
   Option B - Using Git command line:
   ```bash
   cd body-tracker
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR-USERNAME/body-tracker.git
   git push -u origin main
   ```

4. **Create Render account**
   - Go to render.com
   - Sign up with your GitHub account (easier)

5. **Deploy your app**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect it's a Flask app
   - Settings to configure:
     - **Name**: body-tracker (or any name you like)
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - Click "Create Web Service"

6. **Set environment variable**
   - In your Render dashboard, go to "Environment"
   - Click "Add Environment Variable"
   - Key: `SECRET_KEY`
   - Value: Generate a random string (go to https://randomkeygen.com/ and copy a "Fort Knox Password")
   - Click "Save Changes"

7. **Wait for deployment** (2-3 minutes)
   - Render will show deployment logs
   - When done, you'll see "Live" status
   - Click the URL at the top (like https://body-tracker-xxxx.onrender.com)

### Step 4: Import Your Historical Data

If you have data in Google Sheets:

1. **Export to CSV**
   - Open your Google Sheet
   - File → Download → Comma Separated Values (.csv)

2. **Make sure CSV has these columns**:
   - timestamp (or date)
   - weight, bmi
   - body_fat_percentage (or body_fat)
   - visceral_fat_index (or visceral_fat)
   - lean_mass_percentage (or lean_mass)
   - waist_circumference (or waist)
   - bicep_circumference (or bicep)
   - thigh_circumference (or thigh)
   - chest_circumference (or chest)

3. **Run locally to import** (Render doesn't support direct file uploads):
   ```bash
   python import_data.py your_data.csv username
   ```

4. **Upload database to Render**:
   - The import creates `body_tracker.db` file
   - You'll need to manually copy this to Render or re-enter data through the web interface

   OR (simpler): Just enter data through the web interface going forward!

### Step 5: Start Using Your App! 🎉

1. **Access your live app** at the Render URL
2. **Login** with your user accounts
3. **Add measurements** regularly
4. **View trends** to track progress

## 📊 Tips for Best Results

- **Weekly logs**: Set a reminder for the same day/time each week
- **Morning measurements**: More consistent (before eating/drinking)
- **Same conditions**: Use same scale, same time of day
- **Photos**: Take progress photos (store separately) on measurement days

## 🔒 Security Notes

- ✅ All passwords are hashed (secure)
- ✅ Render provides HTTPS automatically
- ✅ Database is private to your app
- ⚠️ Keep your admin password secret
- ⚠️ Don't share your app URL publicly

## 💾 Backing Up Your Data

**Important**: Render's free tier may delete your database after inactivity!

**Solution 1 - Keep it active**: Visit your app at least once every 2 weeks

**Solution 2 - Manual backups**:
1. Login as admin
2. View each user's data
3. Copy to a spreadsheet periodically

**Solution 3 - Add export feature** (future enhancement):
You could add a "Download CSV" button to export all data

## 🆘 Troubleshooting

**Can't access the app?**
- Check Render dashboard for "Live" status
- Wait 2 minutes after first deploy
- Render free tier apps "sleep" after inactivity - first visit may take 30 seconds to wake up

**Forgot admin password?**
- Run locally: `python app.py`
- Database is in `body_tracker.db`
- Use import_data.py logic to create a new admin in code

**Charts not showing?**
- Need at least 2 measurements
- Check browser console (F12) for errors

**Import script errors?**
- Check CSV column names exactly match expected format
- Check date format is recognized
- See sample_data.csv for reference

## 📈 Next Steps (Optional)

1. **Custom domain**: Render allows custom domains in free tier
2. **Email reminders**: Set up weekly calendar reminders to log data
3. **Team accountability**: Share progress with workout buddies
4. **Add features**: Export CSV, photo uploads, goal setting

---

Need help? Check the README.md for full documentation!
