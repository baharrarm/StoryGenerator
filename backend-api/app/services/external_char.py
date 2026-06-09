import httpx, os

URL = os.getenv("EXTERNAL_CHARACTER_API_URL", "https://randomuser.me/api/?nat=au,us,gb")


def get_random_character():
    # with httpx.Client(timeout=5) as client:
    #     r = client.get(URL)
    #     r.raise_for_status()
    #     d = r.json()["results"][0]
    #     name = f"{d['name']['first']} {d['name']['last']}"
    #     age = d["dob"]["age"]
    #     city = d["location"]["city"]
    #     country = d["location"]["country"]
    #     return {"name": name, "traits": f"{age} from {city}, {country}"}
    try:
        with httpx.Client(timeout=5) as client:
            r = client.get(URL)
            r.raise_for_status()
            d = r.json()["results"][0]
            name = f"{d['name']['first']} {d['name']['last']}"
            age = d["dob"]["age"]
            city = d["location"]["city"]
            country = d["location"]["country"]
            return {"name": name, "traits": f"{age} from {city}, {country}"}
    except Exception:
        # fallback
        return {"name": "Alex Morgan", "traits": "26 from Brisbane, Australia"}
