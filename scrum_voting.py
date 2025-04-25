from flask import Flask, render_template_string, request, redirect, url_for
import csv

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
</head>
<body>
    <h2>Scrum Story Point Voting</h2>
    <form method="post">
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

@app.route('/', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
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

    return render_template_string(html_template, members=members, votes=votes)

@app.route('/thank_you')
def thank_you():
    return render_template_string(thank_you_template)

def save_votes():
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

if __name__ == '__main__':
    app.run(debug=True)
