from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
from datetime import datetime
import os
import time


# =========================================================
# 1. CHROME HEADLESS SETUP
# =========================================================

options = Options()

# Headless mode
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 20)


# =========================================================
# 2. OPEN COINMARKETCAP
# =========================================================

print("\n==========================================")
print(" CRYPTOCURRENCY PRICE TRACKER")
print("==========================================")

print("\nOpening CoinMarketCap in headless mode...")

driver.get("https://coinmarketcap.com/")

try:

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table tbody tr")
        )
    )

    print("CoinMarketCap opened successfully!")

except Exception as e:

    print("\n❌ Cryptocurrency table could not be loaded.")
    print("Error:", e)

    driver.quit()
    exit()


time.sleep(3)


# =========================================================
# 3. SCRAPE TOP 10 CRYPTOCURRENCIES
# =========================================================

crypto_data = []

rows = driver.find_elements(
    By.CSS_SELECTOR,
    "table tbody tr"
)

print(f"\nRows found: {len(rows)}")

print("\n==========================================")
print(" TOP 10 CRYPTOCURRENCIES")
print("==========================================")


for row in rows:

    # Stop after collecting 10 valid coins
    if len(crypto_data) >= 10:
        break

    try:

        columns = row.find_elements(
            By.TAG_NAME,
            "td"
        )

        if len(columns) < 8:
            continue


        # -------------------------------------------------
        # Coin Name
        # -------------------------------------------------

        raw_name = columns[2].text.strip()

        name_lines = [
            line.strip()
            for line in raw_name.splitlines()
            if line.strip()
        ]

        if len(name_lines) == 0:
            continue

        coin_name = name_lines[0]


        # -------------------------------------------------
        # Skip CoinMarketCap 20 Index
        # -------------------------------------------------

        if "CoinMarketCap 20" in coin_name:
            continue


        # -------------------------------------------------
        # Price
        # -------------------------------------------------

        price = columns[3].text.strip()


        # -------------------------------------------------
        # 24 Hour Change
        # -------------------------------------------------

        change_24h = columns[4].text.strip()


        # -------------------------------------------------
        # Market Cap
        # -------------------------------------------------

        market_cap = columns[7].text.strip()


        # -------------------------------------------------
        # Clean values
        # -------------------------------------------------

        coin_name = " ".join(coin_name.split())
        price = " ".join(price.split())
        change_24h = " ".join(change_24h.split())
        market_cap = " ".join(market_cap.split())


        # -------------------------------------------------
        # Timestamp
        # -------------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        # -------------------------------------------------
        # Store Data
        # -------------------------------------------------

        crypto_data.append({

            "Coin Name": coin_name,
            "Price": price,
            "24h Change": change_24h,
            "Market Cap": market_cap,
            "Timestamp": timestamp

        })


        # -------------------------------------------------
        # Display
        # -------------------------------------------------

        number = len(crypto_data)

        print(f"\n{number}. {coin_name}")
        print(f"   Price      : {price}")
        print(f"   24h Change : {change_24h}")
        print(f"   Market Cap : {market_cap}")


    except Exception as e:

        print("\n⚠️ Error reading a row:", e)
        continue


# =========================================================
# 4. CHECK DATA
# =========================================================

if len(crypto_data) == 0:

    print("\n❌ No cryptocurrency data collected.")

    driver.quit()
    exit()


print("\n==========================================")
print(
    f"✅ Successfully collected "
    f"{len(crypto_data)} cryptocurrencies."
)
print("==========================================")


# =========================================================
# 5. CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(crypto_data)


# =========================================================
# 6. SAVE DATA TO CSV
# =========================================================

file_name = "crypto_prices.csv"

file_exists = os.path.exists(file_name)


df.to_csv(

    file_name,
    mode="a",
    header=not file_exists,
    index=False

)


print("\n✅ Data added successfully!")
print(f"CSV File: {file_name}")


# =========================================================
# 7. FILTER MENU
# =========================================================

print("\n==========================================")
print("        CRYPTOCURRENCY FILTER")
print("==========================================")

print("1. Show All Coins")
print("2. Filter by 24h Change")
print("3. Filter by Price")


choice = input(
    "\nEnter your choice (1/2/3): "
)


# =========================================================
# OPTION 1 - SHOW ALL COINS
# =========================================================

if choice == "1":

    print("\n==========================================")
    print("          ALL TOP 10 COINS")
    print("==========================================")

    display_df = df[
        [
            "Coin Name",
            "Price",
            "24h Change",
            "Market Cap"
        ]
    ]

    print(
        display_df.to_string(index=False)
    )


# =========================================================
# OPTION 2 - FILTER BY 24H CHANGE
# =========================================================

elif choice == "2":

    try:

        minimum_change = float(
            input(
                "\nEnter minimum 24h change (%): "
            )
        )


        # Convert percentage to number

        df["Change_Value"] = (

            df["24h Change"]

            .str.replace(
                "%",
                "",
                regex=False
            )

            .str.replace(
                ",",
                "",
                regex=False
            )

            .astype(float)

        )


        filtered = df[
            df["Change_Value"] >= minimum_change
        ]


        print(
            f"\n=========================================="
        )

        print(
            f" COINS WITH 24h CHANGE >= "
            f"{minimum_change}%"
        )

        print(
            f"=========================================="
        )


        if filtered.empty:

            print("\nNo coins found.")

        else:

            print(

                filtered[
                    [
                        "Coin Name",
                        "Price",
                        "24h Change",
                        "Market Cap"
                    ]
                ].to_string(index=False)

            )


    except ValueError:

        print(
            "\n❌ Please enter a valid number."
        )


# =========================================================
# OPTION 3 - FILTER BY PRICE
# =========================================================

elif choice == "3":

    try:

        maximum_price = float(
            input(
                "\nEnter maximum price: "
            )
        )


        # Convert price to number

        df["Price_Value"] = (

            df["Price"]

            .str.replace(
                "$",
                "",
                regex=False
            )

            .str.replace(
                ",",
                "",
                regex=False
            )

            .astype(float)

        )


        filtered = df[
            df["Price_Value"] <= maximum_price
        ]


        print(
            f"\n=========================================="
        )

        print(
            f" COINS WITH PRICE <= ${maximum_price}"
        )

        print(
            f"=========================================="
        )


        if filtered.empty:

            print("\nNo coins found.")

        else:

            print(

                filtered[
                    [
                        "Coin Name",
                        "Price",
                        "24h Change",
                        "Market Cap"
                    ]
                ].to_string(index=False)

            )


    except ValueError:

        print(
            "\n❌ Please enter a valid number."
        )


# =========================================================
# INVALID CHOICE
# =========================================================

else:

    print(
        "\n❌ Invalid choice."
    )

    print(
        "Please select 1, 2, or 3."
    )


# =========================================================
# 8. CLOSE DRIVER
# =========================================================

driver.quit()


print("\n==========================================")
print("   PROGRAM COMPLETED SUCCESSFULLY!")
print("   Chrome ran in HEADLESS mode.")
print("==========================================")