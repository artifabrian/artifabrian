import subprocess
from datetime import datetime, timedelta

def is_weekend(date):
    return date.weekday() >= 5

def is_older_than_a_month(date):
    one_month_ago = datetime.now() - timedelta(days=30)
    return date < one_month_ago

def delete_weekend_commits():
    # Get a list of commit hashes, dates, and author emails
    commit_log = subprocess.check_output(
        ['git', 'log', '--pretty=format:%H %ai %ae'], text=True
    ).split('\n')

    # Parse the commit log into a list of tuples (commit_hash, commit_date, author_email)
    commits = []
    for line in commit_log:
        commit_hash, date_str, author_email = line.split(' ', 2)
        commit_date = datetime.strptime(date_str, '%Y-%m-%d')
        commits.append((commit_hash, commit_date, author_email))

    # Find the weekend commits older than a month
    weekend_commits = [
        commit for commit in commits if is_weekend(commit[1]) and is_older_than_a_month(commit[1])
    ]

    # Remove the weekend commits
    for commit in weekend_commits:
        subprocess.run(['git', 'rebase', '--onto', commit[0] + '^', commit[0]])
        print(f"Removed commit {commit[0]} from {commit[2]} on {commit[1].strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    delete_weekend_commits()
