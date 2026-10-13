"""
WL Predictor - Prediction Engine
=================================
Calculates the estimated probability of a railway waitlisted ticket
progressing to RAC or Confirmed status prior to chart preparation.
"""

def calculate_wl_prediction(train_no, travel_class, quota, current_wl, days_left, avg_daily_drop=None, avg_cancellations=None):
    """
    Computes confirmation probability based on:
    1. Base score (50)
    2. Current WL position
    3. Days remaining until journey
    4. Movement rate (average daily drop from history)
    5. Travel class and booking quota adjustments
    6. Historical cancellation trends

    Returns:
        dict: {
            'probability': int (1-99),
            'category': 'High' | 'Medium' | 'Low',
            'badge_color': 'success' | 'warning' | 'danger',
            'reason': str,
            'breakdown': {
                'base': int,
                'position_score': int,
                'time_score': int,
                'movement_score': int,
                'class_quota_score': int,
                'cancellation_score': int,
                'raw_total': int
            }
        }
    """
    # 1. Base Score
    base_score = 50

    # 2. Position Score: Lower WL number significantly increases chances
    current_wl = max(1, int(current_wl))
    if current_wl <= 5:
        position_score = 25
        pos_desc = "Single-digit WL position (+25%)"
    elif current_wl <= 15:
        position_score = 15
        pos_desc = "Low WL position 6-15 (+15%)"
    elif current_wl <= 30:
        position_score = 5
        pos_desc = "Moderate WL position 16-30 (+5%)"
    elif current_wl <= 50:
        position_score = -8
        pos_desc = "High WL position 31-50 (-8%)"
    elif current_wl <= 90:
        position_score = -20
        pos_desc = "Very high WL position 51-90 (-20%)"
    else:
        position_score = -32
        pos_desc = "Deep waitlist > 90 (-32%)"

    # 3. Time Score: More days give more opportunity for passenger cancellations
    days_left = max(0, int(days_left))
    if days_left > 15:
        time_score = 15
        time_desc = f"{days_left} days left - abundant cancellation window (+15%)"
    elif days_left >= 7:
        time_score = 10
        time_desc = f"{days_left} days left - healthy booking movement window (+10%)"
    elif days_left >= 3:
        time_score = 4
        time_desc = f"{days_left} days left - moderate remaining time (+4%)"
    elif days_left == 2:
        time_score = -4
        time_desc = "Only 2 days remaining - cancellations slowing down (-4%)"
    else:  # 0 or 1 day left
        time_score = -18
        time_desc = f"{days_left} day(s) remaining - final chart preparation imminent (-18%)"

    # 4. Movement Score: Daily waitlist clearing velocity
    if avg_daily_drop is None or avg_daily_drop <= 0:
        # Default assumption based on typical express train dynamics
        avg_drop = 2.0
    else:
        avg_drop = float(avg_daily_drop)

    if avg_drop >= 6.0:
        movement_score = 16
        move_desc = f"Rapid WL clearance (~{avg_drop:.1f}/day) (+16%)"
    elif avg_drop >= 3.0:
        movement_score = 10
        move_desc = f"Active WL clearance (~{avg_drop:.1f}/day) (+10%)"
    elif avg_drop >= 1.0:
        movement_score = 4
        move_desc = f"Moderate WL clearance (~{avg_drop:.1f}/day) (+4%)"
    elif avg_drop > 0:
        movement_score = -3
        move_desc = f"Sluggish clearance (~{avg_drop:.1f}/day) (-3%)"
    else:
        movement_score = -12
        move_desc = "Stagnant waitlist movement (-12%)"

    # 5. Class and Quota Factor
    class_adjustments = {
        'SL': 10,   # Sleeper: maximum berths, highest cancellation turnover
        '3A': 5,    # 3rd AC: high capacity, regular cancellations
        '2A': -5,   # 2nd AC: fewer coaches, lower turnover
        '1A': -14,  # 1st AC: very few cabins, negligible cancellations
        'CC': 2     # Chair Car: daytime commuters, moderate turnover
    }
    class_score = class_adjustments.get(travel_class.upper(), 0)

    quota_adjustments = {
        'General': 5,
        'GN': 5,
        'Tatkal': -16,     # Tatkal WL rarely confirms as passengers don't cancel no-refund tickets
        'TQ': -16,
        'Ladies': 2,
        'LD': 2,
        'Senior Citizen': 2,
        'SS': 2
    }
    quota_score = quota_adjustments.get(quota, 0)
    class_quota_score = class_score + quota_score

    # 6. Historical Cancellation Factor
    if avg_cancellations is None or avg_cancellations <= 0:
        avg_canc = 6.0
    else:
        avg_canc = float(avg_cancellations)

    if avg_canc >= 12.0:
        cancellation_score = 10
    elif avg_canc >= 7.0:
        cancellation_score = 6
    elif avg_canc >= 3.0:
        cancellation_score = 3
    else:
        cancellation_score = -2

    # Calculate Raw Total
    raw_total = base_score + position_score + time_score + movement_score + class_quota_score + cancellation_score

    # Clamp probability strictly between 1 and 99
    probability = max(1, min(99, int(raw_total)))

    # Determine Category and Badge Color
    if probability >= 70:
        category = "High"
        badge_color = "success"
    elif probability >= 40:
        category = "Medium"
        badge_color = "warning"
    else:
        category = "Low"
        badge_color = "danger"

    # Generate Explainable One-Line Reason
    reasons = []
    if current_wl <= 15:
        reasons.append("manageable WL position")
    elif current_wl > 50:
        reasons.append("heavy backlog in waitlist")

    if days_left >= 7:
        reasons.append("sufficient days for passenger drops")
    elif days_left <= 1:
        reasons.append("critical pre-charting time limit")

    if quota in ('Tatkal', 'TQ'):
        reasons.append("restrictive Tatkal quota cancellation rules")
    elif travel_class.upper() == 'SL':
        reasons.append("high turnover volume in Sleeper class")
    elif travel_class.upper() == '1A':
        reasons.append("limited berth inventory in First AC")

    if reasons:
        reason = f"{category} likelihood primarily influenced by {', and '.join(reasons)}."
    else:
        reason = f"{category} probability based on balanced waitlist progression and historical cancellation patterns."

    return {
        'probability': probability,
        'category': category,
        'badge_color': badge_color,
        'reason': reason,
        'breakdown': {
            'base': base_score,
            'position_score': position_score,
            'position_desc': pos_desc,
            'time_score': time_score,
            'time_desc': time_desc,
            'movement_score': movement_score,
            'movement_desc': move_desc,
            'class_quota_score': class_quota_score,
            'class_score': class_score,
            'quota_score': quota_score,
            'cancellation_score': cancellation_score,
            'avg_cancellations': round(avg_canc, 1),
            'raw_total': raw_total
        }
    }
