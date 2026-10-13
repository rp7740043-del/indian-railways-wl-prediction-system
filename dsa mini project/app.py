"""
WL Predictor - Flask Application
================================
Railway Waitlist Confirmation Prediction & Daily Analytics System.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
import predictor
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'railway_wl_predictor_secret_key_2026'

# Ensure database is initialized on startup
database.init_db()

@app.route('/')
def home():
    """Home page with hero section, quick steps, and system stats."""
    summary = database.get_analytics_summary()
    recent_tickets = database.get_recent_tickets(limit=3)
    return render_template('index.html', summary=summary, recent_tickets=recent_tickets)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Predict page: handles ticket input form and displays confirmation probability."""
    result = None
    form_data = {}

    if request.method == 'POST':
        try:
            train_no = request.form.get('train_no', '').strip()
            journey_date = request.form.get('journey_date', '').strip()
            travel_class = request.form.get('travel_class', 'SL').strip()
            quota = request.form.get('quota', 'General').strip()
            current_wl = int(request.form.get('current_wl', 1))
            days_left = int(request.form.get('days_left', 1))

            form_data = {
                'train_no': train_no,
                'journey_date': journey_date,
                'travel_class': travel_class,
                'quota': quota,
                'current_wl': current_wl,
                'days_left': days_left
            }

            # Retrieve historical movement rate and average cancellation rate for this train or overall
            avg_drop = database.calculate_avg_daily_drop(train_no=train_no)
            avg_canc = database.get_avg_cancellations(train_no=train_no)

            # Calculate prediction using separate predictor module
            prediction = predictor.calculate_wl_prediction(
                train_no=train_no,
                travel_class=travel_class,
                quota=quota,
                current_wl=current_wl,
                days_left=days_left,
                avg_daily_drop=avg_drop,
                avg_cancellations=avg_canc
            )

            # Store prediction in database
            ticket_id = database.add_ticket(
                train_no=train_no,
                journey_date=journey_date,
                travel_class=travel_class,
                quota=quota,
                current_wl=current_wl,
                days_left=days_left,
                probability=prediction['probability'],
                category=prediction['category']
            )

            result = {
                'ticket_id': ticket_id,
                'train_no': train_no,
                'journey_date': journey_date,
                'travel_class': travel_class,
                'quota': quota,
                'current_wl': current_wl,
                'days_left': days_left,
                'probability': prediction['probability'],
                'category': prediction['category'],
                'badge_color': prediction['badge_color'],
                'reason': prediction['reason'],
                'breakdown': prediction['breakdown']
            }

            flash(f"Prediction generated successfully! Estimated chance: {prediction['probability']}% ({prediction['category']})", "success")

        except Exception as e:
            flash(f"Error calculating prediction: {str(e)}", "danger")

    # Suggest a default journey date 7 days from today
    default_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    return render_template('predict.html', result=result, form_data=form_data, default_date=default_date)

@app.route('/movement')
def movement():
    """Waiting list movement tracking page with timeline and line chart."""
    tickets = database.get_all_tickets()
    selected_ticket_id = request.args.get('ticket_id', type=int)

    selected_ticket = None
    history = []
    movement_stats = {
        'start_wl': None,
        'latest_wl': None,
        'total_drop': 0,
        'avg_drop': 0.0,
        'days_tracked': 0
    }

    if tickets:
        if selected_ticket_id:
            selected_ticket = database.get_ticket(selected_ticket_id)
        if not selected_ticket:
            selected_ticket = tickets[0]
            selected_ticket_id = selected_ticket['id']

        history = database.get_wl_history(selected_ticket_id)

        if history:
            start_wl = history[0]['wl_number']
            latest_wl = history[-1]['wl_number']
            total_drop = max(0, start_wl - latest_wl)
            days_tracked = len(history)
            avg_drop = round(total_drop / max(1, days_tracked - 1), 1) if days_tracked > 1 else 0.0

            movement_stats = {
                'start_wl': start_wl,
                'latest_wl': latest_wl,
                'total_drop': total_drop,
                'avg_drop': avg_drop,
                'days_tracked': days_tracked
            }

    today_str = datetime.now().strftime('%Y-%m-%d')
    return render_template(
        'movement.html',
        tickets=tickets,
        selected_ticket=selected_ticket,
        history=history,
        stats=movement_stats,
        today_str=today_str
    )

@app.route('/movement/add', methods=['POST'])
def add_movement_entry():
    """Adds a new daily status update for a ticket."""
    try:
        ticket_id = int(request.form.get('ticket_id'))
        date_str = request.form.get('date', datetime.now().strftime('%Y-%m-%d')).strip()
        wl_number = int(request.form.get('wl_number'))

        database.add_wl_history(ticket_id, date_str, wl_number)
        flash(f"Recorded update: WL {wl_number} on {date_str} successfully!", "success")
        return redirect(url_for('movement', ticket_id=ticket_id))
    except Exception as e:
        flash(f"Failed to record update: {str(e)}", "danger")
        return redirect(url_for('movement'))

@app.route('/analytics')
def analytics():
    """Analytics dashboard with cards, charts, and recent predictions table."""
    summary = database.get_analytics_summary()
    recent_tickets = database.get_recent_tickets(limit=25)
    return render_template('analytics.html', summary=summary, recent_tickets=recent_tickets)

@app.route('/about')
def about():
    """About page detailing prediction methodology, rules, and disclaimers."""
    return render_template('about.html')

# JSON APIs for Chart.js
@app.route('/api/movement-data/<int:ticket_id>')
def api_movement_data(ticket_id):
    """Returns timeline data points for the WL movement chart."""
    history = database.get_wl_history(ticket_id)
    labels = [h['date'] for h in history]
    values = [h['wl_number'] for h in history]
    return jsonify({
        'labels': labels,
        'values': values
    })

@app.route('/api/analytics-data')
def api_analytics_data():
    """Returns cancellation and outcome chart data."""
    cancellation_data = database.get_cancellation_chart_data()
    outcomes_data = database.get_outcomes_chart_data()
    return jsonify({
        'cancellations': cancellation_data,
        'outcomes': outcomes_data
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
