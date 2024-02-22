import sqlite3
import time
from pytube import YouTube
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
import getpass
import subprocess


def week_before():
    """Return WebKit/Chrome timestamps in micro seconds"""
    # Get the current epoch time in seconds since 1970
    epoch_time_seconds = time.time()
    # Convert the current time to microseconds (WebKit timestamp)
    # plus Webkit/Chrome's time starts in 1601. minus one week
    # There are 89 leap years between 1970 and 1601
    webkit_timestamp = int(epoch_time_seconds * 1000000) \
                       + ((1970 - 1601) * 365 + 89) * 86400 * 1000000 \
                       - 604800 * 1000000
    print(f"Current time in Epoch timestamp is {epoch_time_seconds}")
    print("A week ago in Webkit/Chrome timestamp is ", webkit_timestamp)
    return webkit_timestamp


def CalculateDuration():
    # get the Chrome database
    con = sqlite3.connect(f"/Users/{getpass.getuser()}/Library/Application Support/Google/Chrome/Default/History")
    cursor = con.cursor()
    # SQL query to get the visited websites history for the last 7 days(7x24 hours).
    cursor.execute(f"SELECT last_visit_time, url FROM urls where last_visit_time > {week_before()}")

    urls = cursor.fetchall()
    # sorting the data by non-descending order
    urls.sort()

    # track the duration on YouTube with the all_the_microseconds variable
    all_the_microseconds = 0

    # iterate through all the visited websites.
    for i, url in enumerate(urls):
        print(i, url)
        # a url contains epoch time and website's address in a tuple.
        if "youtube.com/watch" in url[1] and i != len(urls) - 1:
            # getting the video's entire duration
            video = url[1]
            yt = YouTube(video)
            # return the video's duration in sec as an int
            video_length = yt.length

            # if a record is YouTube, add the elapsed time
            # by comparing the time of the next visited website.
            # But, there is a problem... The elapsed time should not exceed the video's length.
            # Because exceeding the video's length can happen when leaving the browser open after watching a video.
            all_the_microseconds += min(int(urls[i + 1][0] - url[0]), video_length * 1000000)

    # Calculate hrs, mins, secs from microseconds.
    seconds = all_the_microseconds / 1000000
    hours = int(seconds // 3600)
    remainder = seconds % 3600
    minutes = int(remainder // 60)
    final_seconds = int(remainder % 60)

    text = f"You spent \n\n{hours} hours {minutes} minutes {final_seconds} seconds \n\non Youtube in the last 7 days."
    print(text)
    return text

# Library(PyQt5.QtWidgets) to make a desktop app.
class DesktopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Duration App")

        # Create widgets
        self.entry = QLineEdit()
        self.button = QPushButton("Quit Chrome and Calculate Duration")
        self.greeting_label = QLabel("Calculation takes a few seconds or more")

        # Set up layout
        self.setFixedWidth(350)
        self.setFixedHeight(200)
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.greeting_label)

        self.setLayout(layout)

        # Connect button click to greet method
        self.button.clicked.connect(self.start)

    def start(self):
        subprocess.run(["pkill", "-f", "Google Chrome"])
        self.greeting_label.setText(CalculateDuration())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    greeting_app = DesktopApp()
    greeting_app.show()
    sys.exit(app.exec_())
