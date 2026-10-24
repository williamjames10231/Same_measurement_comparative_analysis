import csv
from datetime import datetime
import json
import re
import time
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "bulacan_camanava_scraped.csv"

# -------------------------------------------------------------
# 1. TARGET PAGES REGISTRY
# Add or remove Facebook agency URLs here with their metadata
# -------------------------------------------------------------
TARGET_AGENCIES = [
    # --- PROVINCIAL & REGIONAL HUBS ---
    {
        "url": "https://www.facebook.com/share/1EYVEuEk1i/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Bulacan (General)",
        "user_id": "bulacan_pdrrmo",
    },
    # --- BULACAN: CITIES ---
    {
        "url": "https://www.facebook.com/share/1D9yG4Ygq6/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "City of Malolos",
        "user_id": "malolos_cdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Gku63fZAq/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "City of Meycauayan",
        "user_id": "meycauayan_cdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Di8rdQRXt/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "City of San Jose del Monte",
        "user_id": "csjdm_cdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1FUiL2ejY4/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "City of Baliuag",
        "user_id": "baliuag_cdrrmo",
    },
    # --- BULACAN: COASTAL & RIVERINE (HIGH-FLOOD RISK) ---
    {
        "url": "https://www.facebook.com/share/17ngLr4cef/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Calumpit",
        "user_id": "calumpit_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Dm7KWrPQZ/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Hagonoy",
        "user_id": "hagonoy_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/19ir5EyyNg/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Marilao",
        "user_id": "marilao_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1BxUhSc9b2/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Bocaue",
        "user_id": "bocaue_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1C4f8zAhhx/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Paombong",
        "user_id": "paombong_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1HmARFDtxY/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Obando",
        "user_id": "obando_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1QzQRukG9V/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Bulakan",
        "user_id": "bulakan_mdrrmo",
    },
    # --- BULACAN: CENTRAL & DAM/RIVER VALLEY MUNICIPALITIES ---
    {
        "url": "https://www.facebook.com/share/1JWZjKPTM4/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Bustos",
        "user_id": "bustos_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1FLmd5zyCY/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Plaridel",
        "user_id": "plaridel_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/19TQHLEXRX/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Pulilan",
        "user_id": "pulilan_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Djyt96hab/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Guiguinto",
        "user_id": "guiguinto_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Dm7KWrPQZ/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Hagonoy",
        "user_id": "hagonoy_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Gwb8GXD7H/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Pandi",
        "user_id": "pandi_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1QzQRukG9V/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Bulakan",
        "user_id": "bulakan_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1CFKMHF83a/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Santa Maria",
        "user_id": "santamaria_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/19fRTWwvuA/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "San Miguel",
        "user_id": "sanmiguel_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1c873uQ9R9/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "San Ildefonso",
        "user_id": "sanildefonso_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/19VnxKnacR/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "San Rafael",
        "user_id": "sanrafael_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Jbk8F5h9t/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Angat",
        "user_id": "angat_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1DVqbV4di8/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Norzagaray",
        "user_id": "norzagaray_mdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1GZYq16Fex/?mibextid=wwXIfr",
        "default_region": "Bulacan",
        "default_location": "Doña Remedios Trinidad",
        "user_id": "drt_mdrrmo",
    },
    # --- CAMANAVA (NORTH NCR FLOOD BASIN) ---
    {
        "url": "https://www.facebook.com/share/1Gku63fZAq/?mibextid=wwXIfr",
        "default_region": "CAMANAVA",
        "default_location": "Valenzuela City",
        "user_id": "valenzuela_cdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1ELBPLvCvS/?mibextid=wwXIfr",
        "default_region": "CAMANAVA",
        "default_location": "Malabon City",
        "user_id": "malabon_cdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1Dgp44yRXw/?mibextid=wwXIfr",
        "default_region": "CAMANAVA",
        "default_location": "Navotas City",
        "user_id": "navotas_cdrrmo",
    },
    {
        "url": "https://www.facebook.com/share/1F78Zh77BW/?mibextid=wwXIfr",
        "default_region": "CAMANAVA",
        "default_location": "Caloocan City",
        "user_id": "caloocan_drrmo",
    },
]

# Specific barangay/municipality patterns for fine-grained tagging
LOCATIONS_MAPPING = {
    "Calumpit": ("Bulacan", "Calumpit"),
    "Hagonoy": ("Bulacan", "Hagonoy"),
    "Malolos": ("Bulacan", "City of Malolos"),
    "Marilao": ("Bulacan", "Marilao"),
    "Meycauayan": ("Bulacan", "City of Meycauayan"),
    "Bocaue": ("Bulacan", "Bocaue"),
    "Guiguinto": ("Bulacan", "Guiguinto"),
    "Balagtas": ("Bulacan", "Balagtas"),
    "San Miguel": ("Bulacan", "San Miguel"),
    "San Ildefonso": ("Bulacan", "San Ildefonso"),
    "San Rafael": ("Bulacan", "San Rafael"),
    "Bustos": ("Bulacan", "Bustos"),
    "Baliuag": ("Bulacan", "City of Baliuag"),
    "Plaridel": ("Bulacan", "Plaridel"),
    "Pulilan": ("Bulacan", "Pulilan"),
    "Paombong": ("Bulacan", "Paombong"),
    "Obando": ("Bulacan", "Obando"),
    "Bulakan": ("Bulacan", "Bulakan"),
    "Santa Maria": ("Bulacan", "Santa Maria"),
    "Sta. Maria": ("Bulacan", "Santa Maria"),
    "Norzagaray": ("Bulacan", "Norzagaray"),
    "Angat": ("Bulacan", "Angat"),
    "San Jose del Monte": ("Bulacan", "City of San Jose del Monte"),
    "CSJDM": ("Bulacan", "City of San Jose del Monte"),
    "SJDM": ("Bulacan", "City of San Jose del Monte"),
    "Doña Remedios Trinidad": ("Bulacan", "Doña Remedios Trinidad"),
    "DRT": ("Bulacan", "Doña Remedios Trinidad"),
    "Caloocan": ("CAMANAVA", "Caloocan City"),
    "Bagong Silang": ("CAMANAVA", "Brgy. Bagong Silang"),
    "Malabon": ("CAMANAVA", "Malabon City"),
    "Navotas": ("CAMANAVA", "Navotas City"),
    "Valenzuela": ("CAMANAVA", "Valenzuela City"),
    "Polo": ("CAMANAVA", "Valenzuela City"),
}

DISASTER_EVENTS = [
    # Historical Events & Entities
    "Typhoon Ulysses",
    "Typhoon Rolly",
    "Typhoon Quinta",
    "Typhoon Fabian",
    "Typhoon Karding",
    "Typhoon Paeng",
    "Typhoon Egay",
    "Typhoon Falcon",
    "Typhoon Carina",
    "Bustos Dam",
    "Angat Dam",
    "Ipo Dam",

    # Weather Phenomena (Parallel: English & Tagalog)
    "Typhoon", "Bagyo",
    "Monsoon", "Habagat", "Amihan",
    "Rainfall", "Buhos ng ulan",
    "Rain", "Ulan",
    "Heavy Rain", "Malakas na ulan",
    "Thunderstorm", "Kidlat at kulog",
    "Storm", "Unos",
    "Storm Surge", "Daluyong",
    "Low Pressure Area", "LPA", "Namumuong sama ng panahon",

    # Water & Flood Status (Parallel: English & Tagalog)
    "Flooding", "Pagbaha",
    "Flood", "Baha",
    "Flash flood", "Biglaang baha",
    "Submerged", "Lubog sa baha", "Lubog",
    "Water level", "Antas ng tubig",
    "Overflow", "Umaapaw", "Umapaw",
    "High Tide", "Taib",
    "Dam release", "Pagpapakawala ng tubig",
    "Spillway",

    # Rescue & Emergency Actions (Parallel: English & Tagalog)
    "Rescue", "Saklolo", "Sagip",
    "Help", "Tulong",
    "Evacuate", "Lumikas",
    "Evacuation", "Paglikas", "Likas",
    "Evacuation Center", "Sentro ng paglikas",
    "Trapped", "Na-trap", "Nakulong",
    "Stranded", "Naipit",
    "Missing", "Nawawala",
    "Casualty", "Nasawi", "Patay",
    "Relief goods", "Ayuda",

    # Warnings, Advisories & Hazards
    "Red Warning Level",
    "Orange Warning Level",
    "Yellow Warning Level",
    "Signal No. 1",
    "Signal No. 2",
    "Signal No. 3",
    "Signal No. 4",
    "Signal No. 5",
    "Advisory", "Abiso",
    "Alert", "Alerto",
    "Hazard", "Panganib",
    "Landslide", "Pagguho ng lupa",
    "Class suspension", "Walang pasok", "Suspindido ang klase",
    "Threatening", "Nagbabanta"
]
def clean_text_payload(raw_text):
    """Safely decode JSON escape sequences and strip broken surrogates."""
    try:
        cleaned = json.loads(f'"{raw_text}"')
    except Exception:
        try:
            cleaned = raw_text.encode("utf-8", "surrogatepass").decode("unicode_escape", "surrogatepass")
        except Exception:
            cleaned = raw_text

    return cleaned.encode("utf-8", "surrogatepass").decode("utf-8", "ignore").replace("\n", " ").strip()

def detect_location(text, fallback_region, fallback_location):
    for keyword, (region, loc_name) in LOCATIONS_MAPPING.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE):
            return region, loc_name
    return fallback_region, fallback_location

def detect_disaster_event(text):
    for event in DISASTER_EVENTS:
        if re.search(r"\b" + re.escape(event) + r"\b", text, re.IGNORECASE):
            return event
    return ""

all_rows = []
global_post_counter = 1
global_comment_counter = 1

with sync_playwright() as p:
    print("Launching Chromium...")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    for agency in TARGET_AGENCIES:
        url = agency["url"]
        user_id = agency["user_id"]
        def_reg = agency["default_region"]
        def_loc = agency["default_location"]

        page_posts = []
        page_comments = []

        def make_interceptor(posts_list, comments_list):
            def intercept(response):
                if "graphql" in response.url and response.status == 200:
                    try:
                        body = response.text()
                        
                        # Extract Main Posts (Facebook uses 'creation_time')
                        post_matches = re.findall(r'"text":"(.*?)".*?"creation_time":(\d+)', body)
                        for text_chunk, ts in post_matches:
                            clean_txt = clean_text_payload(text_chunk)
                            if len(clean_txt) > 15:
                                rx_reactions = re.search(r'"reaction_count":\{"count":(\d+)\}', body)
                                rx_comments = re.search(r'"comment_count":\{"total_count":(\d+)\}', body)
                                rx_shares = re.search(r'"share_count":\{"count":(\d+)\}', body)

                                posts_list.append({
                                    "raw_text": clean_txt,
                                    "unix_ts": int(ts),
                                    "reactions": int(rx_reactions.group(1)) if rx_reactions else 0,
                                    "comments": int(rx_comments.group(1)) if rx_comments else 0,
                                    "shares": int(rx_shares.group(1)) if rx_shares else 0,
                                })

                        # Extract Comments (Facebook often uses 'created_time' and 'body' for comments)
                        comment_matches = re.findall(r'"body":\{"text":"(.*?)"\}.*?"created_time":(\d+)', body)
                        for text_chunk, ts in comment_matches:
                            clean_txt = clean_text_payload(text_chunk)
                            if len(clean_txt) > 5:
                                comments_list.append({
                                    "raw_text": clean_txt,
                                    "unix_ts": int(ts)
                                })
                    except Exception:
                        pass
            return intercept

        page = context.new_page()

        page.route(
            "**/*",
            lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_()
        )

        interceptor = make_interceptor(page_posts, page_comments)
        page.on("response", interceptor)

        print(f"\n==========================================")
        print(f"Scraping Agency: {user_id} ({url})")
        print(f"==========================================")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)  # Extended wait time so the feed actually loads
            page.keyboard.press("Escape")
            time.sleep(2)

            for i in range(2000):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3.0)
                print(f"[{user_id}] Scroll {i+1}/15 | Posts: {len(page_posts)} | Comments: {len(page_comments)}")

        except Exception as e:
            print(f"Error loading {url}: {e}")

        page.close()

        # Deduplicate and process Posts
        unique_posts = list({r["raw_text"]: r for r in page_posts}.values())
        current_parent_id = ""

        for item in unique_posts:
            dt = datetime.fromtimestamp(item["unix_ts"])
            region, location = detect_location(item["raw_text"], def_reg, def_loc)
            disaster_event = detect_disaster_event(item["raw_text"])
            current_parent_id = f"P{global_post_counter:07d}"

            all_rows.append({
                "post_id": current_parent_id,
                "parent_post_id": "",
                "row_type": "post",
                "timestamp": dt.strftime("%m/%d/%Y %H:%M"),
                "date": dt.strftime("%m/%d/%Y"),
                "year": dt.year,
                "month": dt.month,
                "day_of_week": dt.strftime("%A"),
                "region": region,
                "location": location,
                "disaster_event": disaster_event,
                "source_type": "Facebook Agency Post",
                "user_id": user_id,
                "text": item["raw_text"],
                "num_reactions": item["reactions"],
                "num_comments": item["comments"],
                "num_shares": item["shares"],
            })
            global_post_counter += 1

        # Deduplicate and process Comments (Assigning them to the last seen post)
        unique_comments = list({r["raw_text"]: r for r in page_comments}.values())
        for item in unique_comments:
            dt = datetime.fromtimestamp(item["unix_ts"])
            region, location = detect_location(item["raw_text"], def_reg, def_loc)
            
            all_rows.append({
                "post_id": f"C{global_comment_counter:07d}",
                "parent_post_id": current_parent_id if current_parent_id else f"P{global_post_counter:07d}",
                "row_type": "comment",
                "timestamp": dt.strftime("%m/%d/%Y %H:%M"),
                "date": dt.strftime("%m/%d/%Y"),
                "year": dt.year,
                "month": dt.month,
                "day_of_week": dt.strftime("%A"),
                "region": region,
                "location": location,
                "disaster_event": "",
                "source_type": "Facebook Comment",
                "user_id": "anonymous_public",
                "text": item["raw_text"],
                "num_reactions": 0,
                "num_comments": 0,
                "num_shares": 0,
            })
            global_comment_counter += 1

        time.sleep(3)

    browser.close()

# -------------------------------------------------------------
# 3. WRITE CONSOLIDATED CSV
# -------------------------------------------------------------
fieldnames = [
    "post_id", "parent_post_id", "row_type", "timestamp", "date", "year", "month", 
    "day_of_week", "region", "location", "disaster_event", "source_type", 
    "user_id", "text", "num_reactions", "num_comments", "num_shares"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig", errors="ignore") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nAll agencies completed! Total rows collected: {len(all_rows)}. Saved to '{OUTPUT_FILE}'.")