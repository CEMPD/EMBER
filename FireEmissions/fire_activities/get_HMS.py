import os
import requests
import argparse
from datetime import datetime, timedelta

# Function to download files within a date range
def download_files(start_date, end_date, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    current_date = start_date
    year = start_date.year  # Extract year from the start date

    while current_date <= end_date:
        month = f"{current_date.month:02d}"
        day = f"{current_date.day:02d}"
        
        # Construct the file URL dynamically based on the year
        file_url = f"https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Fire_Points/Text/{year}/{month}/hms_fire{year}{month}{day}.txt"
        file_name = f"hms{year}{month}{day}.txt"
        file_path = os.path.join(output_dir, file_name)

        try:
            response = requests.get(file_url, timeout=10)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"✅ Downloaded: {file_name}")
            else:
                print(f"❌ Not Found: {file_name}")
        except requests.RequestException as e:
            print(f"⚠️ Error downloading {file_name}: {e}")

        current_date += timedelta(days=1)

    print("✅ All downloads complete!")

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Download NOAA HMS Fire Points TXT files for a given date range.")
    parser.add_argument("start_date", type=str, help="Start date in YYYYMMDD format")
    parser.add_argument("end_date", type=str, help="End date in YYYYMMDD format")

    # Parse args initially to get the start date before setting default output
    temp_args, _ = parser.parse_known_args()
    try:
        default_year = datetime.strptime(temp_args.start_date, "%Y%m%d").year
        default_output = f"hms_fire_{default_year}"
    except ValueError:
        default_output = "hms_fire_data"  # Fallback if the date format is wrong

    parser.add_argument("--output", type=str, default=default_output, help="Output directory (default: hms_fire_YYYY)")

    args = parser.parse_args()

    # Convert input dates to datetime objects
    try:
        start_date = datetime.strptime(args.start_date, "%Y%m%d")
        end_date = datetime.strptime(args.end_date, "%Y%m%d")
    except ValueError:
        print("❌ Invalid date format! Please use YYYYMMDD.")
        return

    # Validate that start date is before end date
    if start_date > end_date:
        print("❌ Error: Start date must be before or equal to end date.")
        return

    # Start downloading
    download_files(start_date, end_date, args.output)

if __name__ == "__main__":
    main()