import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

# Set up the WebDriver
driver = webdriver.Chrome()  # Ensure the chromedriver is in PATH or specify its location

# File paths
urls_file_path = "C:/Users/blade/OneDrive/Desktop/Cars/cars.txt"
json_file_path = "C:/Users/blade/OneDrive/Desktop/Cars/car_data_for_text_2021.json"  # You can specify your desired path here

# Define a function to extract data from tables

def extract_data(driver):
    data = {}

    # Extract the image URL
    try:
        image = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:image"]').get_attribute("content")
        data['Image'] = image
    except Exception:
        data['Image'] = None
    # Extract brand, model, and version
    try:
        try:
            header_text =driver.find_element(By.XPATH, "//*[@id='content_container']/div[4]/h3").text 
        
        except Exception:
            header_text= driver.find_element(By.XPATH,'//*[@id="content_container"]/div[2]/h3').text
        brand, model = header_text.split(' ', 1)
        try:
            version = driver.find_element(By.XPATH, "//*[@id='content_container']/div[4]/h3/span").text
        except:
            version = driver.find_element(By.XPATH, '//*[@id="content_container"]/div[2]/h3/span').text
        if version in model:
            model = model.replace(version, '').strip()
        full_name = f"{brand} {model}"
        data["Nom"] = model if len(full_name) > 22 else full_name
        data['Brand'] = brand
        data['Model'] = model
        data['Version'] = version
        data['Generation'] = gen.__str__()
    except Exception:
        data['Brand'] = None
        data['Model'] = None
        data['Version'] = None

    # Define table headers to scrape
    sections = [
        "Caractéristiques",
        "Motorisation",
        "Transmission",
        "Dimensions",
        "Performances",
        "Consommation",
        "Equipements de sécurité",
        "Audio et communication",
        "Equipements extérieurs",
        "Equipements intérieurs",
        "Equipements fonctionnels"
    ]

    for section in sections:
        try:
            # Locate the table by its header
            table = driver.find_element(By.XPATH, f"//table[thead/tr/th[contains(text(), '{section}')]]")
            rows = table.find_elements(By.XPATH, ".//tbody/tr")

            # Extract key-value pairs
            section_data = {}
            for row in rows:
                try:
                    key = row.find_element(By.TAG_NAME, "th").text.strip()
                    value = row.find_element(By.TAG_NAME, "td").text.strip()
                    section_data[key] = value
                except Exception:
                    continue

            if section == "Caractéristiques":
                # Mapping logic for CARROSSERIE
                if "CARROSSERIE" in section_data:
                    carrosserie = section_data["CARROSSERIE"]

                    # Apply your transformation rules
                    if carrosserie in ['Citadine', 'Compacte', 'Monospace']:
                        section_data["CARROSSERIE"] = "Compacte"
                    elif carrosserie == 'Berline':
                        section_data["CARROSSERIE"] = "Sedan"
                    elif carrosserie in ['Coupé', 'Cabriolet']:
                        section_data["CARROSSERIE"] = "Premium"

                filtered_section_data = {
                    k: v for k, v in section_data.items() if k in ["CARROSSERIE", "NOMBRE DE PLACES", "NOMBRE DE PORTES"]
                }
                data[section] = filtered_section_data
            else:
                data[section] = section_data
        except Exception:
            data[section] = None

    return data


# Function to download the image and save it to the specified folder
# Function to download the image and save it to the specified folder with formatted version
def download_image(image_url, brand, model, version,gen):
    try:
        # Format brand, model, and version (replace spaces with hyphens and make lowercase)
        formatted_brand = brand.replace(" ", "-").lower()  # Adjust to .upper() if you want uppercase
        formatted_model = model.replace(" ", "-").lower()  # Adjust to .upper() if you want uppercase
        formatted_version = version.replace(" ", "-").lower()  # Adjust to .upper() if you want uppercase

        # Create the folder if it doesn't exist
        folder_path = f"C:/Users/blade/OneDrive/Desktop/Cars/photos/"
        os.makedirs(folder_path, exist_ok=True)

        # Get the image content
        response = requests.get(image_url)
        image_name = f"{formatted_brand}-{formatted_model}-{formatted_version}-{gen}.webp"  # Get the image file name from the URL

        # Define the full path to save the image
        image_path = os.path.join(folder_path, image_name)

        # Save the image
        with open(image_path, "wb") as file:
            file.write(response.content)
        print(f"Image saved to {image_path}")
    except Exception as e:
        print(f"Error downloading image: {e}")
    return image_name


# Check if the JSON file exists and load existing data
# Read URLs from the file
with open(urls_file_path, "r", encoding="utf-8") as file:
    urls = [line.strip() for line in file if line.strip()]  # Remove empty lines

global gen
gen = 3git 
# Iterate through URLs and scrape data
for url in urls:
    try:
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        scraped_data = extract_data(driver)  # Pass the driver as an argument
           
        
        if scraped_data["Audio et communication"]:
            try:
                section = scraped_data["Audio et communication"]
                connect= section["CONNECTIVITÉ"]
                scraped_data['Bluetooth'] =  True if "bluetooth" in connect.lower() else False
                scraped_data['Apple CarPlay'] = True if "apple carplay" in connect.lower() else False
                scraped_data['Android Auto'] = True if "android auto" in connect.lower() else False
            except Exception as e :
                scraped_data['Bluetooth'] =  False
                scraped_data['Apple CarPlay'] = False
                scraped_data['Android Auto'] = False
        else :
            if scraped_data.get("Audio et communication") is None:
                del scraped_data["Audio et communication"]
            try:
                section = scraped_data["Equipements intérieurs"]
                connect= section["CONNECTIVITÉ"]
                scraped_data['Bluetooth'] =  True if "bluetooth" in connect.lower() else False
                scraped_data['Apple CarPlay'] = True if "apple carplay" in connect.lower() else False
                scraped_data['Android Auto'] = True if "android auto" in connect.lower() else False
            except Exception as e :
                scraped_data['Bluetooth'] =  False
                scraped_data['Apple CarPlay'] = False
                scraped_data['Android Auto'] = False
        

        # Check if the version already exists in the model text
        print(f"Scraped data from {url}")

        # If there is an image URL, download it
        if scraped_data['Image']:
            scraped_data['Image']=download_image(scraped_data['Image'], scraped_data['Brand'], scraped_data['Model'],scraped_data['Version'], scraped_data['Generation'])
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
    with open(json_file_path, "a", encoding="utf-8") as json_file:
        json.dump(scraped_data, json_file, indent=4, ensure_ascii=False)
        json_file.write(",\n")
    #gen += 1

# Write the updated data back to the file


# Close the driver
driver.quit()
print(f"Scraping completed. Data saved to {json_file_path}")
