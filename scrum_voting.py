from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import csv
import datetime
import os

app = Flask(__name__)
app.secret_key = 'secret_key_for_flash_messages'

# Define allowed votes
allowed_votes = {"0", "1", "2", "3", "5"}

# Members list
members = ["Alice", "Bob", "Charlie"]

# Store votes
votes = {member: "" for member in members}

# Admin credentials
ADMIN_PASSWORD = "admin123"

# HTML template for home page
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Scrum Story Point Voting</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin-top: 50px;
            background-color: #f9f9f9;
        }
        form {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        input[type="text"] {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            width: 200px;
            font-size: 16px;
            text-align: center;
        }
        input[type="submit"] {
            padding: 10px 20px;
            background-color: #007aff;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #005bb5;
        }
        .flash-message {
            color: #007aff;
            font-weight: bold;
            margin-top: 30px;
        }
        .voted-box {
            background-color: lightgrey;
            color: #007aff;
            font-weight: bold;
            text-align: center;
        }
        table {
            margin-top: 30px;
            border-collapse: collapse;
            width: 80%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 20px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007aff;
            color: white;
        }
    </style>
</head>
<body>
    <h2>Scrum Story Point Voting</h2>
    <form method="post" action="/vote">
        {% for member in members %}
            <label for="{{ member }}">{{ member }}</label>
            {% if votes[member] %}
                <input type="text" id="{{ member }}" name="{{ member }}" value="VOTED" readonly class="voted-box">
            {% else %}
                <input type="text" id="{{ member }}" name="{{ member }}">
            {% endif %}
        {% endfor %}
        <input type="submit" value="Submit Vote">
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash-message">
          {% for message in messages %}
            {{ message }}
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}
</body>
</html>
"""

# (Admin template update is now included visually too)

@app.route('/', methods=['GET'])
def home():
    return render_template_string(html_template, members=members, votes=votes)

@app.route('/vote', methods=['POST'])
def vote():
    updated_member = None
    for member in members:
        vote_value = request.form.get(member)
        if vote_value and not votes[member]:
            if vote_value in allowed_votes:
                votes[member] = vote_value
                updated_member = member
                break
            else:
                return "Invalid vote. Please enter 0, 1, 2, 3, or 5."

    if updated_member:
        save_votes(partial=True)
        flash(f"Vote recorded for {updated_member}!")

    if all(votes[m] for m in members):
        save_votes(partial=False)

    return redirect(url_for('home'))

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    average = calculate_average()
    return render_template_string(admin_template, votes=votes, average=average)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Incorrect password."
    return '''
    <form method="post">
        <input type="password" name="password" placeholder="Enter Admin Password">
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/reset', methods=['POST'])
def reset_votes():
    global votes
    votes = {member: "" for member in members}
    return redirect(url_for('admin'))

def save_votes(partial):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    csv_filename = "story_point_votes.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Voter", "Vote"])
        for member, vote in votes.items():
            writer.writerow([member, vote])
        writer.writerow([])
        if not partial:
            total = sum(int(vote) for vote in votes.values())
            average = total / len(votes)
            writer.writerow(["Average", round(average, 2)])
        writer.writerow(["Last Updated", timestamp])

def calculate_average():
    valid_votes = [int(vote) for vote in votes.values() if vote]
    if valid_votes:
        return round(sum(valid_votes) / len(valid_votes), 2)
    return 0.00

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
