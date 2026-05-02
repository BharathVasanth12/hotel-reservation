# 🌐 Hotel Reservation Web App

Beautiful and elegant web interface for predicting hotel booking cancellations.

## 🎨 Features

- **Elegant Design**: Modern gradient UI with smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Real-time Predictions**: Instant cancellation probability predictions
- **Visual Feedback**: Color-coded results with probability bars
- **Model Performance**: Displays key metrics (F1: 90%, ROC-AUC: 91.4%)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install flask joblib
```

### 2. Train the Model (if not already done)

```bash
PYTHONPATH=/path/to/Hotel_Reservation python3 pipeline/training_pipeline.py
```

This will generate the model at `artifacts/model/hotel_reservation_model.joblib`

### 3. Run the Flask App

```bash
python app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5001**

## 📝 How to Use

1. **Fill in Reservation Details**: Enter guest information, stay duration, room preferences, etc.
2. **Click "Predict Cancellation"**: Submit the form to get prediction
3. **View Results**: See cancellation probability with visual indicators:
   - 🟢 **Green** = Low cancellation risk (< 50%)
   - 🔴 **Red** = High cancellation risk (> 50%)

## 🔌 API Integration

To integrate with the actual prediction API, uncomment the API call section in `templates/index.html` (line 431-464) and update the endpoint.

### API Endpoint

**POST** `/predict`

**Request Body:**
```json
{
  "no_of_adults": 2,
  "no_of_children": 0,
  "no_of_weekend_nights": 1,
  "no_of_week_nights": 2,
  "type_of_meal_plan": "Meal Plan 1",
  "room_type_reserved": "Room_Type 1",
  "required_car_parking_space": 0,
  "lead_time": 30,
  "arrival_year": 2024,
  "arrival_month": 6,
  "arrival_date": 15,
  "market_segment_type": "Online",
  "repeated_guest": 0,
  "no_of_previous_cancellations": 0,
  "no_of_previous_bookings_not_canceled": 0,
  "avg_price_per_room": 100.0,
  "no_of_special_requests": 0
}
```

**Response:**
```json
{
  "prediction": 0,
  "probability": 0.23,
  "status": "Confirmed"
}
```

## 📂 File Structure

```
Hotel_Reservation/
├── app.py                  # Flask application
├── templates/
│   └── index.html         # Web interface
└── artifacts/
    └── model/
        └── hotel_reservation_model.joblib
```

## 🎨 Customization

### Colors

Edit the gradient colors in `templates/index.html`:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Model Stats

Update the statistics in the hero section:

```html
<div class="stat-card">
    <h3>90.0%</h3>
    <p>F1-Score</p>
</div>
```

## 🔒 Security Notes

For production deployment:
- Add input validation
- Implement rate limiting
- Use HTTPS
- Add authentication if needed
- Set `debug=False` in `app.py`

## 📱 Screenshots

The interface includes:
- Split-screen layout with hero section
- Interactive form with 17 input fields
- Real-time loading animation
- Color-coded prediction results
- Probability visualization bar

---

Built with ❤️ using Flask, HTML5, CSS3, and JavaScript
