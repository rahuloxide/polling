from flask import Flask, render_template_string, request, redirect, url_for, flash
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

# HTML template for home page
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Scrum Story Point Voting</title>
    <style>
        .flash-message {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h2>Scrum Story Point Voting</h2>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
          {% for message in messages %}
            <li class="flash-message">{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method="post" action="/vote">
        {% for member in members %}
            <label for="{{ member }}">{{ member }}:</label>
            {% if votes[member] %}
                <input type="text" id="{{ member }}" name="{{ member }}" value="*" readonly><br><br>
            {% else %}
                <input type="text" id="{{ member }}" name="{{ member }}"><br><br>
            {% endif %}
        {% endfor %}
        <input type="submit" value="Submit Vote">
    </form>
    <br>
    <a href="/admin">Go to Admin Page</a>
</body>
</html>
"""

# HTML template for admin page
admin_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Scrum Story Point Voting</title>
    <script>
        function confirmReset() {
            return confirm('Are you sure you want to reset all votes?');
        }
    </script>
</head>
<body>
    <h2>Admin Panel</h2>
    <table border="1">
        <tr>
            <th>Member</th>
            <th>Vote</th>
        </tr>
        {% for member, vote in votes.items() %}
        <tr>
            <td>{{ member }}</td>
            <td>{{ vote if vote else 'Not Voted' }}</td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <form method="post" action="/reset" onsubmit="return confirmReset();">
        <input type="submit" value="Reset Votes">
    </form>
    <br>
    <a href="/">Go Back to Voting Page</a>
</body>
</html>
"""

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
    return render_template_string(admin_template, votes=votes)

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
            writer.writerow(["Average", average])
        writer.writerow(["Last Updated", timestamp])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
