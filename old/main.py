import requests
import time

API_KEY = "uPi2GRteUXOs94UAQtR-Zg"

def generate_image(prompt, width=640, height=640):
    headers = {
        "Client-Agent": "ImageGenBot:1.0",
        "apikey": API_KEY
    }

    payload = {
        "prompt": prompt,
        "params": {
            "n": 1,
            "width": width,
            "height": height,
            "steps": 20,
            "cfg_scale": 7,
            "sampler_name": "k_euler"
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["stable_diffusion"]
    }

    # Step 1: Submit generation request
    submit_response = requests.post(
        "https://stablehorde.net/api/v2/generate/async",
        json=payload,
        headers=headers
    )

    if submit_response.status_code != 200 or "id" not in submit_response.json():
        print("Error submitting request:", submit_response.text)
        return

    request_id = submit_response.json()["id"]
    print(f"✅ Request submitted. Request ID: {request_id}")

    # Step 2: Poll until generation complete
    check_url = f"https://stablehorde.net/api/v2/generate/check/{request_id}"
    while True:
        time.sleep(5)
        check_response = requests.get(check_url, headers=headers).json()
        if check_response.get("done"):
            print("✅ Image generation completed.")
            break
        print(f"⏳ Waiting... ({check_response.get('waiting', '?')} in queue)")

    # Step 3: Download the image
    result_url = f"https://stablehorde.net/api/v2/generate/status/{request_id}"
    result = requests.get(result_url, headers=headers).json()

    generations = result.get("generations", [])
    if not generations:
        print("⚠️ No generations found.")
        return

    img_url = "https://stablehorde.net" + generations[0]["img"]
    img_data = requests.get(img_url).content
    filename = f"image_{int(time.time())}.png"

    with open(filename, "wb") as f:
        f.write(img_data)

    print(f"✅ Image saved as: {filename}")

# 🔧 Example usage
generate_image("A surreal mountain landscape with glowing rivers at night")
