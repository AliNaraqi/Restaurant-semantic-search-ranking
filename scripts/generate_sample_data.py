"""Generate a Yelp-schema sample restaurant dataset for local development.

When you download the real Yelp Open Dataset, place the JSON files in
data/raw/ and re-run `python scripts/prepare_data.py`.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "sample"
OUT.mkdir(parents=True, exist_ok=True)

random.seed(42)

# Rich restaurant catalog covering cuisines, price, ambience, dietary needs
RESTAURANTS = [
    # Quiet Italian / romantic / vegetarian-friendly
    {
        "business_id": "b001",
        "name": "Osteria Luna",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.5,
        "review_count": 842,
        "is_open": 1,
        "categories": "Restaurants, Italian, Vegetarian, Wine Bars",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'romantic': True, 'intimate': True, 'quiet': True}",
            "RestaurantsVegetarianFriendly": "True",
            "NoiseLevel": "u'quiet'",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
            "WiFi": "u'free'",
            "BusinessParking": "{'street': True, 'valet': True}",
        },
        "hours": {"Monday": "17:0-22:0", "Friday": "17:0-23:0", "Saturday": "17:0-23:0"},
        "tags": ["quiet", "romantic", "date night", "vegetarian", "pasta", "wine"],
    },
    {
        "business_id": "b002",
        "name": "Trattoria Verde",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.3,
        "review_count": 521,
        "is_open": 1,
        "categories": "Restaurants, Italian, Vegan, Mediterranean",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'intimate': True, 'classy': True}",
            "RestaurantsVegetarianFriendly": "True",
            "NoiseLevel": "u'average'",
            "GoodForMeal": "{'dinner': True, 'lunch': True}",
        },
        "hours": {"Tuesday": "11:0-21:0", "Saturday": "11:0-22:0"},
        "tags": ["italian", "vegan", "vegetarian", "date", "mediterranean"],
    },
    {
        "business_id": "b003",
        "name": "Nonna's Candlelight",
        "city": "Vancouver",
        "state": "BC",
        "postal_code": "V6B",
        "latitude": 49.2827,
        "longitude": -123.1207,
        "stars": 4.7,
        "review_count": 310,
        "is_open": 1,
        "categories": "Restaurants, Italian, Seafood",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'romantic': True, 'quiet': True, 'upscale': True}",
            "NoiseLevel": "u'quiet'",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Wednesday": "17:0-22:0", "Saturday": "17:0-23:0"},
        "tags": ["quiet", "romantic", "candlelight", "italian", "date night", "vegetarian options"],
    },
    # Loud / casual Italian (should rank lower for "quiet date")
    {
        "business_id": "b004",
        "name": "Pizza Slam Downtown",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 3.9,
        "review_count": 1204,
        "is_open": 1,
        "categories": "Restaurants, Pizza, Italian, Bars",
        "attributes": {
            "RestaurantsPriceRange2": "1",
            "Ambience": "{'casual': True, 'noisy': True, 'touristy': True}",
            "NoiseLevel": "u'loud'",
            "GoodForMeal": "{'lunch': True, 'dinner': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Monday": "11:0-23:0"},
        "tags": ["pizza", "loud", "casual", "cheap", "groups"],
    },
    # Japanese / sushi
    {
        "business_id": "b005",
        "name": "Sakura Omakase",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.8,
        "review_count": 456,
        "is_open": 1,
        "categories": "Restaurants, Japanese, Sushi Bars, Seafood",
        "attributes": {
            "RestaurantsPriceRange2": "4",
            "Ambience": "{'upscale': True, 'intimate': True, 'quiet': True}",
            "NoiseLevel": "u'quiet'",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
        },
        "hours": {"Thursday": "17:30-22:0", "Saturday": "17:0-22:30"},
        "tags": ["sushi", "omakase", "quiet", "upscale", "date night", "japanese"],
    },
    {
        "business_id": "b006",
        "name": "Ramen House Noodle Bar",
        "city": "Montreal",
        "state": "QC",
        "postal_code": "H2X",
        "latitude": 45.5017,
        "longitude": -73.5673,
        "stars": 4.2,
        "review_count": 980,
        "is_open": 1,
        "categories": "Restaurants, Japanese, Ramen, Noodles",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'trendy': True}",
            "NoiseLevel": "u'average'",
            "GoodForMeal": "{'lunch': True, 'dinner': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Monday": "11:30-21:0"},
        "tags": ["ramen", "noodles", "casual", "vegetarian broth option"],
    },
    # Mexican
    {
        "business_id": "b007",
        "name": "Casa Sol",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.4,
        "review_count": 667,
        "is_open": 1,
        "categories": "Restaurants, Mexican, Vegetarian, Cocktail Bars",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'hipster': True}",
            "NoiseLevel": "u'average'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'lunch': True, 'dinner': True, 'brunch': True}",
        },
        "hours": {"Friday": "11:0-23:0"},
        "tags": ["mexican", "tacos", "vegetarian", "margaritas", "brunch"],
    },
    {
        "business_id": "b008",
        "name": "Quiet Cantina",
        "city": "Ottawa",
        "state": "ON",
        "postal_code": "K1P",
        "latitude": 45.4215,
        "longitude": -75.6972,
        "stars": 4.1,
        "review_count": 203,
        "is_open": 1,
        "categories": "Restaurants, Mexican, Bars",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'romantic': True, 'quiet': True}",
            "NoiseLevel": "u'quiet'",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
        },
        "hours": {"Saturday": "17:0-22:0"},
        "tags": ["mexican", "quiet", "date", "cocktails"],
    },
    # Indian / vegetarian heavy
    {
        "business_id": "b009",
        "name": "Spice Garden Vegetarian",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.6,
        "review_count": 734,
        "is_open": 1,
        "categories": "Restaurants, Indian, Vegetarian, Vegan",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'family': True}",
            "NoiseLevel": "u'average'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'lunch': True, 'dinner': True}",
        },
        "hours": {"Monday": "11:0-21:0"},
        "tags": ["indian", "vegetarian", "vegan", "curry", "family"],
    },
    {
        "business_id": "b010",
        "name": "Taj Palace Fine Dining",
        "city": "Calgary",
        "state": "AB",
        "postal_code": "T2P",
        "latitude": 51.0447,
        "longitude": -114.0719,
        "stars": 4.5,
        "review_count": 412,
        "is_open": 1,
        "categories": "Restaurants, Indian, Seafood",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'upscale': True, 'romantic': True, 'quiet': True}",
            "NoiseLevel": "u'quiet'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
        },
        "hours": {"Friday": "17:0-22:30"},
        "tags": ["indian", "upscale", "quiet", "date night", "vegetarian options"],
    },
    # Chinese
    {
        "business_id": "b011",
        "name": "Dragon Dumpling House",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.0,
        "review_count": 1550,
        "is_open": 1,
        "categories": "Restaurants, Chinese, Dim Sum, Noodles",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'touristy': True}",
            "NoiseLevel": "u'loud'",
            "GoodForMeal": "{'lunch': True, 'brunch': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Saturday": "10:0-21:0"},
        "tags": ["dim sum", "dumplings", "chinese", "loud", "groups"],
    },
    {
        "business_id": "b012",
        "name": "Jade Tea House",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.4,
        "review_count": 289,
        "is_open": 1,
        "categories": "Restaurants, Chinese, Tea Rooms, Vegetarian",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'quiet': True, 'intimate': True}",
            "NoiseLevel": "u'quiet'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'lunch': True, 'afternoon': True}",
        },
        "hours": {"Tuesday": "11:0-20:0"},
        "tags": ["quiet", "tea", "vegetarian", "chinese", "intimate"],
    },
    # American / steakhouse / brunch
    {
        "business_id": "b013",
        "name": "The Ember Room",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.6,
        "review_count": 598,
        "is_open": 1,
        "categories": "Restaurants, Steakhouses, American (New), Wine Bars",
        "attributes": {
            "RestaurantsPriceRange2": "4",
            "Ambience": "{'upscale': True, 'romantic': True, 'quiet': True}",
            "NoiseLevel": "u'quiet'",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
        },
        "hours": {"Friday": "17:0-23:0"},
        "tags": ["steak", "upscale", "quiet", "date night", "wine"],
    },
    {
        "business_id": "b014",
        "name": "Sunny Side Brunch Club",
        "city": "Vancouver",
        "state": "BC",
        "postal_code": "V6B",
        "latitude": 49.2827,
        "longitude": -123.1207,
        "stars": 4.2,
        "review_count": 871,
        "is_open": 1,
        "categories": "Restaurants, American (Traditional), Breakfast & Brunch, Coffee & Tea",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'trendy': True}",
            "NoiseLevel": "u'average'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'brunch': True, 'breakfast': True}",
        },
        "hours": {"Sunday": "8:0-15:0"},
        "tags": ["brunch", "breakfast", "eggs", "coffee", "vegetarian"],
    },
    # Thai / Vietnamese / Korean
    {
        "business_id": "b015",
        "name": "Lotus Thai Garden",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.3,
        "review_count": 445,
        "is_open": 1,
        "categories": "Restaurants, Thai, Vegetarian, Asian Fusion",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'intimate': True, 'quiet': True}",
            "NoiseLevel": "u'quiet'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dinner': True, 'lunch': True, 'datenight': True}",
        },
        "hours": {"Wednesday": "11:30-21:30"},
        "tags": ["thai", "quiet", "vegetarian", "date", "curry"],
    },
    {
        "business_id": "b016",
        "name": "Pho Night Market",
        "city": "Calgary",
        "state": "AB",
        "postal_code": "T2P",
        "latitude": 51.0447,
        "longitude": -114.0719,
        "stars": 4.1,
        "review_count": 1120,
        "is_open": 1,
        "categories": "Restaurants, Vietnamese, Noodles, Soup",
        "attributes": {
            "RestaurantsPriceRange2": "1",
            "Ambience": "{'casual': True}",
            "NoiseLevel": "u'loud'",
            "GoodForMeal": "{'lunch': True, 'dinner': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Monday": "10:0-22:0"},
        "tags": ["pho", "vietnamese", "cheap", "loud", "noodles"],
    },
    {
        "business_id": "b017",
        "name": "Seoul BBQ Garden",
        "city": "Edmonton",
        "state": "AB",
        "postal_code": "T5J",
        "latitude": 53.5461,
        "longitude": -113.4938,
        "stars": 4.0,
        "review_count": 920,
        "is_open": 1,
        "categories": "Restaurants, Korean, Barbeque, Asian Fusion",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'lively': True}",
            "NoiseLevel": "u'loud'",
            "GoodForMeal": "{'dinner': True, 'groups': True}",
        },
        "hours": {"Saturday": "16:0-23:0"},
        "tags": ["korean", "bbq", "groups", "loud", "grill"],
    },
    # French / Mediterranean
    {
        "business_id": "b018",
        "name": "Bistro Amélie",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.7,
        "review_count": 378,
        "is_open": 1,
        "categories": "Restaurants, French, Wine Bars, Cocktail Bars",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'romantic': True, 'intimate': True, 'quiet': True}",
            "NoiseLevel": "u'quiet'",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Thursday": "17:0-22:0", "Saturday": "17:0-23:0"},
        "tags": ["french", "romantic", "quiet", "date night", "wine", "vegetarian options"],
    },
    {
        "business_id": "b019",
        "name": "Aegean Table",
        "city": "Montreal",
        "state": "QC",
        "postal_code": "H2X",
        "latitude": 45.5017,
        "longitude": -73.5673,
        "stars": 4.4,
        "review_count": 256,
        "is_open": 1,
        "categories": "Restaurants, Mediterranean, Greek, Vegetarian",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'intimate': True}",
            "NoiseLevel": "u'average'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'lunch': True, 'dinner': True}",
        },
        "hours": {"Tuesday": "11:0-21:0"},
        "tags": ["mediterranean", "greek", "vegetarian", "hummus", "outdoor"],
    },
    # Fast food / noisy (negative controls)
    {
        "business_id": "b020",
        "name": "Burger Blast Drive-Thru",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 3.2,
        "review_count": 2100,
        "is_open": 1,
        "categories": "Restaurants, Burgers, Fast Food, American (Traditional)",
        "attributes": {
            "RestaurantsPriceRange2": "1",
            "Ambience": "{'casual': True}",
            "NoiseLevel": "u'very_loud'",
            "GoodForMeal": "{'lunch': True}",
        },
        "hours": {"Monday": "6:0-24:0"},
        "tags": ["burgers", "fast food", "cheap", "loud", "drive-thru"],
    },
    # More Italian variants
    {
        "business_id": "b021",
        "name": "Il Cortile Quiet Kitchen",
        "city": "Ottawa",
        "state": "ON",
        "postal_code": "K1P",
        "latitude": 45.4215,
        "longitude": -75.6972,
        "stars": 4.6,
        "review_count": 198,
        "is_open": 1,
        "categories": "Restaurants, Italian, Vegetarian, Wine Bars",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'romantic': True, 'quiet': True, 'intimate': True}",
            "NoiseLevel": "u'quiet'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
        },
        "hours": {"Friday": "17:0-22:0"},
        "tags": ["italian", "quiet", "romantic", "vegetarian", "date night", "pasta"],
    },
    {
        "business_id": "b022",
        "name": "Pasta Party Warehouse",
        "city": "Calgary",
        "state": "AB",
        "postal_code": "T2P",
        "latitude": 51.0447,
        "longitude": -114.0719,
        "stars": 3.7,
        "review_count": 640,
        "is_open": 1,
        "categories": "Restaurants, Italian, Pizza, Bars",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'lively': True}",
            "NoiseLevel": "u'loud'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dinner': True, 'groups': True}",
        },
        "hours": {"Saturday": "12:0-23:0"},
        "tags": ["italian", "pasta", "loud", "groups", "party"],
    },
    # Seafood / vegan / dessert
    {
        "business_id": "b023",
        "name": "Harbor Light Seafood",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "stars": 4.3,
        "review_count": 701,
        "is_open": 1,
        "categories": "Restaurants, Seafood, American (New)",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'classy': True, 'touristy': True}",
            "NoiseLevel": "u'average'",
            "GoodForMeal": "{'dinner': True, 'lunch': True}",
        },
        "hours": {"Saturday": "11:0-22:0"},
        "tags": ["seafood", "fish", "crab", "waterfront"],
    },
    {
        "business_id": "b024",
        "name": "Green Leaf Vegan Kitchen",
        "city": "Vancouver",
        "state": "BC",
        "postal_code": "V6B",
        "latitude": 49.2827,
        "longitude": -123.1207,
        "stars": 4.5,
        "review_count": 512,
        "is_open": 1,
        "categories": "Restaurants, Vegan, Vegetarian, Healthy",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'casual': True, 'hipster': True}",
            "NoiseLevel": "u'average'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'lunch': True, 'dinner': True}",
        },
        "hours": {"Monday": "11:0-21:0"},
        "tags": ["vegan", "vegetarian", "healthy", "bowls", "plant-based"],
    },
    {
        "business_id": "b025",
        "name": "Midnight Gelato & Espresso",
        "city": "Winnipeg",
        "state": "MB",
        "postal_code": "R3C",
        "latitude": 49.8951,
        "longitude": -97.1384,
        "stars": 4.4,
        "review_count": 334,
        "is_open": 1,
        "categories": "Restaurants, Desserts, Coffee & Tea, Ice Cream & Frozen Yogurt",
        "attributes": {
            "RestaurantsPriceRange2": "1",
            "Ambience": "{'intimate': True, 'quiet': True}",
            "NoiseLevel": "u'quiet'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dessert': True}",
        },
        "hours": {"Friday": "12:0-23:0"},
        "tags": ["dessert", "gelato", "quiet", "coffee", "date dessert"],
    },
    # Extra variety for ranking experiments
    {
        "business_id": "b026",
        "name": "Bamboo Sushi Lounge",
        "city": "Ottawa",
        "state": "ON",
        "postal_code": "K1P",
        "latitude": 45.4215,
        "longitude": -75.6972,
        "stars": 4.2,
        "review_count": 388,
        "is_open": 1,
        "categories": "Restaurants, Japanese, Sushi Bars, Cocktail Bars",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'trendy': True, 'intimate': True}",
            "NoiseLevel": "u'average'",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Saturday": "17:0-23:0"},
        "tags": ["sushi", "cocktails", "date", "japanese", "vegetarian rolls"],
    },
    {
        "business_id": "b027",
        "name": "Family Style Italian Feast",
        "city": "Halifax",
        "state": "NS",
        "postal_code": "B3J",
        "latitude": 44.6488,
        "longitude": -63.5752,
        "stars": 3.8,
        "review_count": 455,
        "is_open": 1,
        "categories": "Restaurants, Italian, Pizza, Caterers",
        "attributes": {
            "RestaurantsPriceRange2": "2",
            "Ambience": "{'family': True, 'casual': True}",
            "NoiseLevel": "u'loud'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dinner': True, 'groups': True}",
        },
        "hours": {"Sunday": "12:0-21:0"},
        "tags": ["italian", "family", "loud", "pizza", "groups"],
    },
    {
        "business_id": "b028",
        "name": "Whisper Wine & Cheese",
        "city": "Quebec City",
        "state": "QC",
        "postal_code": "G1R",
        "latitude": 46.8139,
        "longitude": -71.208,
        "stars": 4.8,
        "review_count": 167,
        "is_open": 1,
        "categories": "Restaurants, Wine Bars, Cheese Shops, Mediterranean",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'romantic': True, 'quiet': True, 'intimate': True}",
            "NoiseLevel": "u'quiet'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dinner': True, 'datenight': True}",
        },
        "hours": {"Friday": "16:0-22:0"},
        "tags": ["wine", "quiet", "romantic", "cheese", "date night", "vegetarian"],
    },
    {
        "business_id": "b029",
        "name": "Taco Truck Alley",
        "city": "Vancouver",
        "state": "BC",
        "postal_code": "V6B",
        "latitude": 49.2827,
        "longitude": -123.1207,
        "stars": 4.0,
        "review_count": 1890,
        "is_open": 1,
        "categories": "Restaurants, Mexican, Food Trucks, Street Vendors",
        "attributes": {
            "RestaurantsPriceRange2": "1",
            "Ambience": "{'casual': True}",
            "NoiseLevel": "u'loud'",
            "GoodForMeal": "{'lunch': True, 'dinner': True}",
            "RestaurantsVegetarianFriendly": "True",
        },
        "hours": {"Monday": "11:0-21:0"},
        "tags": ["tacos", "street food", "cheap", "loud", "casual"],
    },
    {
        "business_id": "b030",
        "name": "Roma Quiet Courtyard",
        "city": "Victoria",
        "state": "BC",
        "postal_code": "V8W",
        "latitude": 48.4284,
        "longitude": -123.3656,
        "stars": 4.5,
        "review_count": 275,
        "is_open": 1,
        "categories": "Restaurants, Italian, Vegetarian, Outdoor Dining",
        "attributes": {
            "RestaurantsPriceRange2": "3",
            "Ambience": "{'romantic': True, 'quiet': True, 'intimate': True}",
            "NoiseLevel": "u'quiet'",
            "RestaurantsVegetarianFriendly": "True",
            "GoodForMeal": "{'dinner': True, 'datenight': True, 'lunch': True}",
        },
        "hours": {"Wednesday": "12:0-21:30", "Saturday": "12:0-22:30"},
        "tags": ["italian", "quiet", "courtyard", "romantic", "vegetarian", "date night"],
    },
]

REVIEW_TEMPLATES = {
    "italian_quiet": [
        "Perfect quiet Italian spot for a romantic date. Excellent vegetarian pasta options and soft lighting.",
        "Intimate atmosphere, low noise, incredible risotto. Great for anniversaries.",
        "Came for a date night — candlelit tables, thoughtful vegetarian menu, superb wine list.",
        "Peaceful dining room. The eggplant parmesan was outstanding. Highly recommend for couples.",
    ],
    "italian_loud": [
        "Fun pizza place but extremely loud. Not suitable for a quiet conversation.",
        "Great Italian food for groups. Expect noise and wait times on weekends.",
        "Casual pasta joint — tasty but chaotic. Skip if you want romance.",
    ],
    "japanese": [
        "Exquisite sushi and a calm omakase counter. Ideal for a special night out.",
        "Fresh fish, attentive service, quiet dining room.",
        "Ramen was rich and comforting. Casual vibe, sometimes busy.",
    ],
    "mexican": [
        "Flavorful tacos and solid vegetarian burritos. Lively patio.",
        "Quiet cantina with craft cocktails — surprising date-night gem.",
        "Street-style Mexican, cheap and cheerful but noisy.",
    ],
    "indian": [
        "Best vegetarian thali in town. Spicy, aromatic, filling.",
        "Upscale Indian with quiet booths and excellent paneer dishes for date night.",
        "Family-friendly Indian buffet. Average noise.",
    ],
    "chinese": [
        "Dim sum carts flying by — delicious but loud and crowded.",
        "Serene tea house with vegetarian dumplings. Perfect afternoon escape.",
    ],
    "american": [
        "Steakhouse perfection: quiet, upscale, great wine pairings for dates.",
        "Brunch crowd is energetic. Eggs Benedict and bottomless coffee.",
        "Fast burgers, drive-thru speed, not a sit-down experience.",
    ],
    "thai": [
        "Quiet Thai garden with excellent tofu curry. Romantic and vegetarian-friendly.",
        "Authentic flavors, intimate setting, soft music.",
    ],
    "vietnamese": [
        "Huge bowls of pho. Cash only vibe, loud and bustling.",
    ],
    "korean": [
        "Tabletop BBQ for groups. Smoky, loud, and fun — not quiet.",
    ],
    "french": [
        "Charming French bistro. Quiet, romantic, vegetarian tasting menu available.",
        "Wine-forward date night. Soft jazz and candlelight.",
    ],
    "mediterranean": [
        "Fresh Mediterranean plates, lots of vegetarian mezze.",
    ],
    "seafood": [
        "Fresh catch and bay views. A bit touristy but solid seafood.",
    ],
    "vegan": [
        "Plant-based bowls that even omnivores love. Casual and bright.",
    ],
    "dessert": [
        "Quiet gelato spot for after-dinner dates. Excellent espresso.",
    ],
    "wine": [
        "Whisper-quiet wine bar with cheese boards. Pure romance.",
    ],
}

CATEGORY_TO_REVIEW_KEY = {
    "Italian": "italian_quiet",
    "Pizza": "italian_loud",
    "Japanese": "japanese",
    "Sushi": "japanese",
    "Ramen": "japanese",
    "Mexican": "mexican",
    "Indian": "indian",
    "Chinese": "chinese",
    "Dim Sum": "chinese",
    "Steakhouses": "american",
    "American": "american",
    "Burgers": "american",
    "Breakfast": "american",
    "Thai": "thai",
    "Vietnamese": "vietnamese",
    "Korean": "korean",
    "French": "french",
    "Mediterranean": "mediterranean",
    "Greek": "mediterranean",
    "Seafood": "seafood",
    "Vegan": "vegan",
    "Desserts": "dessert",
    "Wine Bars": "wine",
}


def pick_review_key(categories: str, tags: list[str]) -> str:
    cats = categories
    if "quiet" in tags or "romantic" in tags or "date night" in tags:
        if "Italian" in cats:
            return "italian_quiet"
        if "French" in cats or "Wine" in cats:
            return "french" if "French" in cats else "wine"
    if "loud" in tags or "Pizza" in cats and "quiet" not in tags:
        if "Italian" in cats or "Pizza" in cats:
            return "italian_loud"
    for key, mapped in CATEGORY_TO_REVIEW_KEY.items():
        if key in cats:
            return mapped
    return "american"


def build_search_text(biz: dict) -> str:
    attrs = biz.get("attributes") or {}
    parts = [
        biz["name"],
        biz["categories"],
        " ".join(biz.get("tags", [])),
        f"city {biz['city']}",
        f"rating {biz['stars']}",
        f"price {attrs.get('RestaurantsPriceRange2', '')}",
        f"noise {attrs.get('NoiseLevel', '')}",
        f"ambience {attrs.get('Ambience', '')}",
    ]
    return " | ".join(str(p) for p in parts if p)


def main() -> None:
    businesses = []
    for biz in RESTAURANTS:
        row = {k: v for k, v in biz.items() if k != "tags"}
        row["address"] = f"{random.randint(100, 9999)} Main St"
        businesses.append(row)

    reviews = []
    rid = 1
    for biz in RESTAURANTS:
        key = pick_review_key(biz["categories"], biz["tags"])
        templates = REVIEW_TEMPLATES[key]
        # Bias reviews toward tags for retrieval quality
        tag_line = (
            f" Known for: {', '.join(biz['tags'][:5])}."
            if biz.get("tags")
            else ""
        )
        n = min(8, max(3, biz["review_count"] // 100))
        for i in range(n):
            text = templates[i % len(templates)] + tag_line
            stars = min(5.0, max(1.0, round(biz["stars"] + random.uniform(-0.5, 0.5), 1)))
            reviews.append(
                {
                    "review_id": f"r{rid:04d}",
                    "user_id": f"u{random.randint(1, 200):03d}",
                    "business_id": biz["business_id"],
                    "stars": stars,
                    "useful": random.randint(0, 20),
                    "funny": random.randint(0, 5),
                    "cool": random.randint(0, 10),
                    "text": text,
                    "date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                }
            )
            rid += 1

    biz_path = OUT / "businesses.jsonl"
    rev_path = OUT / "reviews.jsonl"
    with biz_path.open("w", encoding="utf-8") as f:
        for row in businesses:
            f.write(json.dumps(row) + "\n")
    with rev_path.open("w", encoding="utf-8") as f:
        for row in reviews:
            f.write(json.dumps(row) + "\n")

    # Also store tags sidecar for preprocessing enrichment
    tags_path = OUT / "business_tags.json"
    tags_path.write_text(
        json.dumps({b["business_id"]: b["tags"] for b in RESTAURANTS}, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {len(businesses)} businesses → {biz_path}")
    print(f"Wrote {len(reviews)} reviews → {rev_path}")
    print(f"Wrote tags → {tags_path}")


if __name__ == "__main__":
    main()
