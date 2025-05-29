import asyncio
from playwright.async_api import async_playwright
import os
import json
import argparse

CONFIG_DIR = os.path.join("configs", "devices")

def list_available_devices():
    """列出 configs/devices 目录中可用的设备配置文件"""
    if not os.path.exists(CONFIG_DIR):
        print(f"配置目录 {CONFIG_DIR} 不存在。请先运行 generate_device_configs.py。")
        return []
    
    devices = []
    for f_name in os.listdir(CONFIG_DIR):
        if f_name.endswith(".json"):
            devices.append(f_name[:-5]) # 移除 .json 后缀
    return devices

async def capture_mobile_screenshots(html_file_path, output_dir="screenshots", device_name=None):
    """
    使用 Playwright 截取 HTML 文件中每个“页面”的手机屏幕截图。

    参数:
    html_file_path (str): HTML 文件的路径。
    output_dir (str): 保存截图的目录名称。
    device_name (str, optional): 要使用的设备配置名称 (文件名，不含.json)。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    absolute_html_file_path = os.path.abspath(html_file_path)
    if not os.path.exists(absolute_html_file_path):
        print(f"错误：HTML 文件未找到于 {absolute_html_file_path}")
        return

    device_config_to_use = {}
    if device_name:
        config_file_path = os.path.join(CONFIG_DIR, f"{device_name}.json")
        if not os.path.exists(config_file_path):
            print(f"错误: 设备配置文件 '{config_file_path}' 未找到。")
            print(f"可用的设备有: {', '.join(list_available_devices())}")
            return
        try:
            with open(config_file_path, "r", encoding="utf-8") as f:
                device_config_to_use = json.load(f)
            print(f"使用设备配置: {device_config_to_use.get('name', device_name)}")
        except json.JSONDecodeError:
            print(f"错误: 解析设备配置文件 '{config_file_path}' 失败。")
            return
        except IOError as e:
            print(f"错误: 读取设备配置文件 '{config_file_path}' 失败: {e}")
            return
    else:
        # 如果没有指定设备，可以使用一个默认的简单配置或报错退出
        # 这里我们选择报错并提示用户选择设备
        print("错误: 请使用 '--device <device_name>' 参数指定一个设备。")
        available = list_available_devices()
        if available:
            print(f"可用的设备有: {', '.join(available)}")
        else:
            print(f"配置目录 {CONFIG_DIR} 中没有找到设备配置文件。请先运行 generate_device_configs.py。")
        return


    async with async_playwright() as p:
        # 从配置中移除 'name' 字段，因为它不是 browser.new_context 的有效参数
        # Playwright 的 device descriptors 通常就是 context 参数本身
        context_params = {k: v for k, v in device_config_to_use.items() if k != 'name'}
        
        # 检查 viewport 是否存在，Playwright device descriptors 应该有
        if 'viewport' not in context_params or not context_params['viewport']:
             print(f"警告: 设备配置 '{device_name}' 中缺少有效的 'viewport' 信息。截图可能不按预期。")
             # 可以设置一个默认的viewport以防万一，或者让它失败
             # context_params['viewport'] = {'width': 375, 'height': 667} # 例如 iPhone 8

        try:
            browser = await p.chromium.launch() # 或者根据配置选择 p.firefox / p.webkit
            context = await browser.new_context(**context_params)
        except Exception as e:
            print(f"创建 Playwright 浏览器上下文时出错: {e}")
            print("请检查您的设备配置文件是否包含了 Playwright new_context 所需的有效参数。")
            print(f"使用的参数: {context_params}")
            return
            
        page = await context.new_page()

        await page.goto(f"file://{absolute_html_file_path}")
        await page.wait_for_load_state('networkidle')

        slides = await page.query_selector_all(".slide")
        print(f"找到了 {len(slides)} 个页面。开始截图...")

        for i, slide_handle in enumerate(slides):
            slide_id = await slide_handle.get_attribute("id")
            if not slide_id:
                slide_id = f"slide_{i+1}"

            await slide_handle.scroll_into_view_if_needed()
            await page.wait_for_timeout(500) # 等待滚动和渲染

            screenshot_filename = f"{output_dir}/{device_name}_{slide_id}.png"
            await page.screenshot(path=screenshot_filename)
            print(f"已保存截图: {screenshot_filename}")

        await browser.close()
        print("所有截图已完成。")

async def main():
    parser = argparse.ArgumentParser(description="为 HTML 文件的每一页截取手机屏幕截图。")
    parser.add_argument("html_file", help="要截图的 HTML 文件路径 (例如 爱的法宝phone.html)")
    parser.add_argument("--device", type=str, help="要模拟的设备名称 (例如 iphone_x)。使用 --list-devices 查看可用选项。")
    parser.add_argument("--output-dir", type=str, default="screenshots", help="保存截图的目录 (默认: screenshots)")
    parser.add_argument("--list-devices", action="store_true", help="列出所有可用的设备配置并退出。")

    args = parser.parse_args()

    if args.list_devices:
        print("可用的设备配置 (文件名，不含 .json 后缀):")
        devices = list_available_devices()
        if devices:
            for dev in devices:
                print(f"- {dev}")
        else:
            print(f"在 {CONFIG_DIR} 中未找到设备配置文件。")
            print("请先运行 'python generate_device_configs.py' 生成配置文件。")
        return

    if not args.device:
        parser.error("参数 '--device' 是必需的。使用 '--list-devices' 查看可用选项。")
        return

    await capture_mobile_screenshots(args.html_file, args.output_dir, args.device)

if __name__ == "__main__":
    asyncio.run(main())