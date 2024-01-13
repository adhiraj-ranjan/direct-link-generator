import base64
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urlparse

def get_onedrive_direct_link(URL):
    data_bytes64 = base64.b64encode(bytes(URL, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl


def get_mediafire_direct_link(URL, get_json=False):
    try:
        down_link = str(URL)
        mid = down_link.split('/', 5)
        if mid[3] == "view":
            mid[3] = "file"
            down_link = '/'.join(mid)
        r = requests.get(down_link)
        soup = BeautifulSoup(r.content, "html.parser")
        a_href = soup.find("a", {"class": "input popsok"}).get("href")
        a = str(a_href)

        if not get_json: # only get direct url
            return a

        id = URL.split('/', 5)[4]
        a_byte = soup.find("a", {"class": "input popsok"}).get_text()
        a_name = soup.find("div", {"class": "dl-btn-label"}).get_text()
        details = soup.find("ul", {"class": "details"})
        li_items = details.find_all('li')[1]
        some = li_items.find_all("span")[0].get_text().split()
        dat = list(some)
        down = a_byte.replace(" ", "").strip()
        time = dat[1]
        date = dat[0]
        byte = down.split("(", 1)[1].split(")", 1)[0]
        name = a_name.replace(" ", "").strip()
        return {
        "status": "true",
        "data": {
            "file": {
            "url": {
                'directDownload': a,
                "original": URL,
            },
            "metadata": {
                "id": id,
                "name": name,
                "size": {
                "readable": byte
                },
                "DateAndTime": {
                "time": time,
                "date": date
                }
            }
            }
        }
        }
    except:
        return "Invalid Link"


def get_google_drive_direct_link(URL, get_json=False):
    try:
        down = URL.split('/', 6)
        url = f'https://drive.google.com/uc?export=download&id={down[5]}'

        if not get_json:
            return url # return only url

        session = requests.Session()

        response = session.get(url, stream=True)

        # Get the headers from the response
        headers = response.headers
        # Get the Content-Disposition header
        content_disp = headers.get('content-disposition')

        # Extract the filename from the content disposition header using regex
        filename = None
        if content_disp:
            match = re.search(r'filename="(.+)"', content_disp)
            if match:
                filename = match.group(1)

        # Get the Content-Length header
        content_length = headers.get('content-length')

        # Get the Last-Modified header
        last_modified = headers.get('last-modified')

        # Get the Content-Type header
        content_type = headers.get('content-type')

        return {
        "status": "true",
        "data": {
            "file": {
                "url": {
                    'directDownload': url,
                    "original": URL,
                },
                "metadata": {
                    "id":
                        down[5],
                    "name":
                        filename if filename else 'No filename provided by the server.',
                    "size": {
                        "readable":
                        f'{round(int(content_length) / (1024 * 1024), 2)} MB' if
                        content_length else 'No content length provided by the server.',
                        "type":
                        content_type
                        if content_type else 'No content type provided by the server.'
                    },
                    "DateAndTime":
                        last_modified if last_modified else
                        'No last modified date provided by the server.',
                }
                }
        }
        }

    except:
        return "Invalid link"


def extract_first_link(paragraph):
    # Using regex to find all URLs in the paragraph
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', paragraph)

    if urls:
        # Parsing the first URL using urlparse
        parsed_url = urlparse(urls[0])
        # Returning the first link
        return parsed_url.geturl()

    # Return None if no URLs are found
    return None

def identify_service_convert(URL):
    parsed_url = urlparse(URL)
    domain = parsed_url.netloc
    # print(domain)
    if domain == "www.mediafire.com":
        return get_mediafire_direct_link(URL)
    elif domain == "drive.google.com":
        return get_google_drive_direct_link(URL)
    elif domain == "1drv.ms":
        return get_onedrive_direct_link(URL)
    else:
        return "This Site is currently not supported."