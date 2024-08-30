import sys
import asyncio
import requests
from pyppeteer import launch
from bs4 import BeautifulSoup


def get_ip():
    urls = [
        "http://ip.me",
        "http://ifconfig.me",
        "http://icanhazip.com",
        "http://ipinfo.io/ip",
    ]

    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Failed to retrieve IP from {url}: {response.status_code}")
        except requests.RequestException as e:
            print(f"An error occurred when accessing {url}: {e}")

    return "Failed to retrieve IP from both services."


async def fetch_html_from_pingpe(ip, port):
    """
    Fetch HTML content from the specified tcp.ping.pe page using Pyppeteer.

    Args:
        ip (str): The IP address to check.
        port (str): The port number to check.

    Returns:
        str: The HTML content of the page.
    """
    url = f"https://tcp.ping.pe/{ip}:{port}"

    # Launch the headless browser
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Navigate to the specified URL
    await page.goto(url)
    await asyncio.sleep(10)  # Wait for the page and JavaScript to load

    # Get the HTML content of the page
    html_content = await page.content()

    # Close the browser
    await browser.close()

    return html_content


def parse_ping_results(html):
    """
    Parse the HTML content to extract the ping results.

    Args:
        html (str): The HTML content of the page.

    Returns:
        dict: A dictionary with the ping result IDs as keys and the result text as values.
    """
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html, "html.parser")

    # Find all <tr> tags that contain ping results
    result_rows = soup.find_all("tr", id=lambda x: x and x.startswith("ping-"))

    # Create a dictionary to store the extracted results
    ping_results = {}

    for row in result_rows:
        result_id = row.find("td", {"id": lambda x: x and x.endswith("-result")}).get(
            "id"
        )
        result_text = row.find(
            "td", {"id": lambda x: x and x.endswith("-result")}
        ).text.strip()

        # Store the result in the dictionary
        ping_results[result_id] = result_text

    return ping_results


def evaluate_cn_connectivity(ping_results):
    """
    Evaluate whether more than half of the CN (China) ping results are successful.

    Args:
        ping_results (dict): A dictionary containing ping result IDs and their corresponding texts.

    Returns:
        bool: True if more than half of the CN results are successful, False otherwise.
    """
    total_cn_tests = 0
    successful_cn_tests = 0

    for result_id, result_text in ping_results.items():
        if result_id.startswith("tcp-CN"):
            total_cn_tests += 1
            if "successful" in result_text:
                successful_cn_tests += 1

    # If no CN tests were found, return False
    if total_cn_tests == 0:
        return False

    # Return True if more than half of the CN tests are successful
    return successful_cn_tests > total_cn_tests / 2


async def check_server_connectivity_in_china(ip, port):
    """
    Check if a server's port is accessible from China by evaluating ping results.

    Args:
        ip (str): The IP address of the server.
        port (str): The port number to check.

    Returns:
        bool: True if the server is accessible from China, False otherwise.
    """
    # Fetch HTML content from the specified page
    html_content = await fetch_html_from_pingpe(ip, port)

    # Parse the HTML content to extract ping results
    ping_results = parse_ping_results(html_content)

    # Evaluate CN connectivity based on the parsed results
    return evaluate_cn_connectivity(ping_results)


if __name__ == "__main__":
    # Check if IP and port were provided as command line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <PORT>")
        sys.exit(1)

    ip = get_ip()
    port = sys.argv[1]

    # Run the check and get the result
    result = asyncio.get_event_loop().run_until_complete(check_server_connectivity_in_china(ip, port))

    # Print the result to stdout
    if result:
        print("True")
    else:
        print("False")