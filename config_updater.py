import json
import sys

def update_inbound_port(file_path, new_port):
    """
    Load JSON from a local file, update the port value under 'inbounds',
    and save the updated JSON back to the file.

    Args:
        file_path (str): The path to the local JSON file.
        new_port (int): The new port value to set.

    Returns:
        dict: The updated JSON object.
    """
    # Load the JSON content from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # Check if 'inbounds' key exists and is a list
    if 'inbounds' in json_data and isinstance(json_data['inbounds'], list):
        # Iterate over inbounds and update the port
        for inbound in json_data['inbounds']:
            if 'port' in inbound:
                inbound['port'] = new_port

    # Save the modified JSON back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4)

    # Return the modified JSON object
    return json_data


我现在需要一个linux脚本(预计为Debian)，帮我完成服务器开机后的一些自动操作
1.为服务器开启BBR，失败的话打印失败。
2.安装python3.9，失败的话打印失败，后面所有操作都需要刚刚python3.9来执行。安装asyncio、pyppeteer、BeautifulSoup库，失败的话打印失败。
3.随机打开63000-63999中的一个端口，然后运行china_connectivity_checker.py，这个脚本会返回True或者False，如果是True的话，则运行config_updater.py，将config.json中的inbounds的port改为刚刚随机打开的端口，如果是False的话，则重新随机打开一个端口，如果连续失败5次，则打印失败，并退出脚本。
4.将生成的config.json复制到/etc/xray/config.json，然后运行此文件夹下的compose.yaml来启动xray服务。
5.再次运行china_connectivity_checker.py，如果返回True，则打印成功，否则打印失败，并打印失败所处的步骤。

