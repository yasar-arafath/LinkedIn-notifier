import time
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def load_previous_data():
    try:
        df = pd.read_excel("linkedin_data.xlsx")
        if not df.empty:
            return df.iloc[-1].to_dict()
    except FileNotFoundError:
        pass
    return None

def save_current_data(username, notification_count, unread_messages, previous_data):
    timestamp = pd.Timestamp.now()
    data = {
        "User": username,
        "Date Time": timestamp,
        "Messages": unread_messages,
        "Notification": notification_count,
        "Message Comparison": previous_data["Messages"] if previous_data else None,
        "Notification Comparison": previous_data["Notification"] if previous_data else None
    }
    df = pd.DataFrame(data, index=[0])

    try:
        existing_df = pd.read_excel("linkedin_data.xlsx")
        updated_df = pd.concat([existing_df, df])
        updated_df.to_excel("linkedin_data.xlsx", index=False)
    except FileNotFoundError:
        df.to_excel("linkedin_data.xlsx", index=False)

def check_linkedin_notifications():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.linkedin.com/in/yasar-arafat/?originalSubdomain=in")

    badge_element = driver.find_element_by_xpath("//a[@href='/notifications/']")
    notification_count = int(badge_element.text.strip())

    messages_element = driver.find_element_by_xpath("//a[@href='/messaging/thread/']")
    unread_messages = int(messages_element.text.strip())

    driver.quit()

    return notification_count, unread_messages

def send_email_notification(notification_count, unread_messages, previous_data):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    gmail_user = "yasararafate@gmail.com"
    gmail_password = "mypassword"

    server.login(gmail_user, gmail_password)
    subject = "LinkedIn Notifications Update"
    body = f"You have {notification_count} new notifications and {unread_messages} unread messages on LinkedIn.\n\n"

    if previous_data is not None:
        prev_notification_count = previous_data["Notification"]
        prev_unread_messages = previous_data["Messages"]
        body += f"Comparison with previous data:\n"
        body += f"Previous notification count: {prev_notification_count}\n"
        body += f"Previous unread messages: {prev_unread_messages}\n"

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = gmail_user
    message["To"] = "yasararafate@gmail.com"

    html = f"""
    <html>
      <body>
        <h2>LinkedIn Notifications Update</h2>
        <p>You have {notification_count} new notifications and {unread_messages} unread messages on LinkedIn.</p>
        <h3>Comparison with previous data:</h3>
        <table>
          <tr>
            <th>Previous notification count</th>
            <th>Previous unread messages</th>
          </tr>
          <tr>
            <td>{prev_notification_count}</td>
            <td>{prev_unread_messages}</td>
          </tr>
        </table>
      </body>
    </html>
    """

    part = MIMEText(html, "html")
    message.attach(part)

    server.sendmail(gmail_user, "yasararafate@gmail.com", message.as_string())

def main():
    previous_data = load_previous_data()

    while True:
        notification_count, unread_messages = check_linkedin_notifications()

        save_current_data("User123", notification_count, unread_messages, previous_data)

        if notification_count > 0:
            send_email_notification(notification_count, unread_messages, previous_data)

        previous_data = {
            "Notification": notification_count,
            "Messages": unread_messages,
        }

        time.sleep(3 * 3600)

if __name__ == "__main__":
    main()
