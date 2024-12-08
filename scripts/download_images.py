import requests

images_dir = "apps/web/static/images"
image_urls = [
    "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiRwfwaJ4QdAUcmkIwCdj190oOTLcKG0qM_TGhkJ7A06ZjhKfR_iAj0S9vyJU8NtbFENZDMNghW01bnRTc-gHimagErWgYiLWtfryiWTvLaxtvhFSnyTvGx6AMuY5I-cWyDcqfpjPYOwvI_/s1600/"
]
image_names = ["bg_natural_sougen.jpg"]


def main():
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        with open(f"{images_dir}/{image_names[i]}", "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    main()
