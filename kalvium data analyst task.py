import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# Path to your WebDriver (e.g., ChromeDriver)
driver_path=r"C:\Users\91988\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
base_url = 'https://results.eci.gov.in/PcResultGenJune2024/partywiseresult'

# Function to fetch and parse HTML content of a state results page using Selenium
def fetch_state_results(url):
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.get(url)
    time.sleep(3)  # Allow time for the page to load

    try:
        table = driver.find_element(By.CLASS_NAME, 'table-partywise')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = [cell.text.strip() for cell in cells]
            data.append(row_data)
    except Exception as e:
        print(f"Error: {e}")
        data = []
    finally:
        driver.quit()

    return data

# List of state URLs to be scraped
state_urls = [
    f'{base_url}-S04.htm',  # Tamil Nadu
    f'{base_url}-S10.htm',  # Bihar
    f'{base_url}-S24.htm',  # Uttar Pradesh
    f'{base_url}-S13.htm',  # Maharashtra
]

# Scraping data for each state and aggregating
all_results = []
for state_url in state_urls:
    state_results = fetch_state_results(state_url)
    all_results.extend(state_results)

# Check if data was scraped
if not all_results:
    print("Error: No data was scraped. Please check the URLs and HTML structure.")
else:
    # Convert the scraped data into a DataFrame
    columns = ['Party', 'Won', 'Leading', 'Total']
    df = pd.DataFrame(all_results, columns=columns)

    # Save the raw scraped data to a CSV file
    df.to_csv('lok_sabha_2024_raw_results.csv', index=False)
# Load the raw data
df = pd.read_csv('lok_sabha_2024_raw_results.csv')

# Convert relevant columns to numeric types, handling non-numeric gracefully
df['Won'] = pd.to_numeric(df['Won'], errors='coerce')
df['Leading'] = pd.to_numeric(df['Leading'], errors='coerce')
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

# Remove rows with missing values
df.dropna(inplace=True)

# Reset index after cleaning
df.reset_index(drop=True, inplace=True)

# Save the cleaned data to a new CSV file
df.to_csv('lok_sabha_2024_cleaned_results.csv', index=False)
# Load the cleaned data
df = pd.read_csv('lok_sabha_2024_cleaned_results.csv')

# Initialize a dictionary to hold insights
insights = {}

# Calculate total seats won by each party
total_seats = df.groupby('Party')['Total'].sum().sort_values(ascending=False)
insights['total_seats'] = total_seats

# Identify the party with the highest number of seats
highest_seats = total_seats.idxmax()
insights['highest_seats'] = highest_seats

# Compute the distribution of seats by party
party_distribution = df['Party'].value_counts()
insights['party_distribution'] = party_distribution

# Count the number of parties that won seats
num_parties = df['Party'].nunique()
insights['num_parties'] = num_parties

# Analyze seats won by specific regional parties
regional_parties = df[df['Party'].isin(['DMK', 'JD(U)', 'SP', 'SHS', 'NCPSP'])].groupby('Party')['Total'].sum()
insights['regional_parties'] = regional_parties

# Total seats won by independent candidates
independent_seats = df[df['Party'] == 'IND']['Total'].sum()
insights['independent_seats'] = independent_seats

# Performance of new parties in this election
new_parties = df[df['Party'].isin(['ASPKR', 'ADAL'])].groupby('Party')['Total'].sum()
insights['new_parties'] = new_parties

# Highest performing party in each state
state_wise = {}
for state_url in state_urls:
    state_results = fetch_state_results(state_url)
    if state_results:
        state_df = pd.DataFrame(state_results, columns=columns)
        state_df['Total'] = pd.to_numeric(state_df['Total'], errors='coerce')
        state_highest = state_df.groupby('Party')['Total'].sum().idxmax()
        state_name = state_url.split('-')[-1].split('.')[0]
        state_wise[state_name] = state_highest
insights['state_wise'] = state_wise

# Display the insights
for key, value in insights.items():
    print(f"{key}: {value}")

# Save insights to a text file
with open('election_insights.txt', 'w') as f:
    for key, value in insights.items():
        f.write(f"{key}: {value}\n")
import matplotlib.pyplot as plt

# Plot total seats won by each party
total_seats.plot(kind='bar', figsize=(10, 6))
plt.title('Total Seats Won by Each Party')
plt.xlabel('Party')
plt.ylabel('Total Seats')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('total_seats_by_party.png')
plt.show()

# Plot party distribution
party_distribution.plot(kind='pie', figsize=(8, 8), autopct='%1.1f%%')
plt.title('Party Distribution')
plt.ylabel('')
plt.tight_layout()
plt.savefig('party_distribution.png')
plt.show()

# Save visualization file paths
visualizations = {
    'total_seats_by_party': 'total_seats_by_party.png',
    'party_distribution': 'party_distribution.png'
}

# Save visualizations information to a text file
with open('visualizations.txt', 'w') as f:
    for key, value in visualizations.items():
        f.write(f"{key}: {value}\n")
from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Lok Sabha Election 2024 Analysis Report', 0, 1, 'C')

    def add_section(self, title, content):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, content)
        self.ln(10)

    def add_image(self, image_path):
        self.image(image_path, x=None, y=None, w=0, h=0)
        self.ln(10)

# Create PDF
pdf = PDFReport()

pdf.add_page()

# Add insights to the PDF
pdf.add_section('Key Insights', '\n'.join([f"{k}: {v}" for k, v in insights.items()]))

# Add visualizations to the PDF
pdf.add_section('Visualizations', '')
for image_path in visualizations.values():
    pdf.add_image(image_path)

# Output PDF to file
pdf.output('Lok_Sabha_Election_2024_Report.pdf')
