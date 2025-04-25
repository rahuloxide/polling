from flask import Flask, render_template_string, request, redirect, url_for
import csv
import datetime
import os

app = Flask(__name__)

# Define allowed votes
allowed_votes = {"0", "1", "2", "3", "5"}

# Members list
members = ["Alice", "Bob", "Charlie"]

# Store votes
votes = {member: "" for member in members}

# HTML template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Scrum Story Point Voting</title>
    <script>
        function confirmReset() {
            return confirm('Are you sure you want to reset all votes?');
        }
    </script>
</head>
<body>
    <h2>Scrum Story Point Voting</h2>
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
    <form method="post" action="/reset" onsubmit="return confirmReset();">
        <input type="submit" value="Reset Votes">
    </form>
</body>
</html>
"""

thank_you_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Thank You</title>
</head>
<body>
    <h2>Thank you for voting!</h2>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(html_template, members=members, votes=votes)

@app.route('/vote', methods=['POST'])
def vote():
    for member in members:
        vote_value = request.form.get(member)
        if vote_value and not votes[member]:
            if vote_value in allowed_votes:
                votes[member] = vote_value
                break
            else:
                return "Invalid vote. Please enter 0, 1, 2, 3, or 5."

    if all(votes[m] for m in members):
        save_votes()

    return redirect(url_for('thank_you'))

@app.route('/reset', methods=['POST'])
def reset_votes():
    global votes
    votes = {member: "" for member in members}
    return redirect(url_for('home'))

@app.route('/thank_you')
def thank_you():
    return render_template_string(thank_you_template)

def save_votes():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    csv_filename = "story_point_votes.csv"
    total = sum(int(vote) for vote in votes.values())
    average = total / len(votes)
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Voter", "Vote"])
        for member, vote in votes.items():
            writer.writerow([member, vote])
        writer.writerow([])
        writer.writerow(["Average", average])
        writer.writerow(["Timestamp", timestamp])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
