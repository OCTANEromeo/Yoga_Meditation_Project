import os
import requests

# Create poses directory if it doesn't exist
poses_dir = 'static/images/poses'
os.makedirs(poses_dir, exist_ok=True)

# List of poses and their image URLs
poses = {
    'pranamasana': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/pranamasana.jpg',
    'hasta_uttanasana': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/hasta-uttanasana.jpg',
    'hasta_padasana': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/hasta-padasana.jpg',
    'ashwa_sanchalanasana': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/ashwa-sanchalanasana.jpg',
    'parvatasana': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/parvatasana.jpg',
    'ashtanga_namaskara': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/ashtanga-namaskara.jpg',
    'bhujangasana': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/bhujangasana.jpg',
    'adho_mukha_svanasana': 'https://raw.githubusercontent.com/yoga-images/surya-namaskar/main/adho-mukha-svanasana.jpg'
}

# Download each pose image
for pose_name, url in poses.items():
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(poses_dir, f'{pose_name}.jpg'), 'wb') as f:
                f.write(response.content)
            print(f'Downloaded {pose_name}.jpg')
        else:
            print(f'Failed to download {pose_name}.jpg')
    except Exception as e:
        print(f'Error downloading {pose_name}.jpg: {e}')
