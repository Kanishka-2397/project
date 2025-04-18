# config.py
import json

_config = {
    "url": [
        "https://www.lg.com/us/laptops/lg-16z90ts-g.aug9u1-gram-laptop",
        "https://www.lg.com/us/speakers/lg-xboom-grab-portable-speaker"
    ],
    "item": [
        {
            "name": "model_id",
            "selector": "span.MuiTypography-root.MuiTypography-overline.css-rrulv7",
            "match": "first",
            "type": "text"
        },
        {
            "name": "title",
            "selector": "h2.MuiTypography-root.MuiTypography-h5.css-72m7wz",
            "match": "first",
            "type": "text"
        },
        {
            "name": "key_features",
            "selector": "ul.css-1he9hsx",
            "match": "first",
            "type": "text"
        },
        {
            "name": "image_urls",
            "selector": "img",
            "match": "all",
            "type": "text"
        }
    ]
}

def get_config(load_from_file=False):
    if load_from_file:
        with open("config.json", "r") as f:
            return json.load(f)
    return _config

def generate_config():
    with open("config.json", "w") as f:
        json.dump(_config, f, indent=4)

if __name__ == "__main__":
    generate_config()
