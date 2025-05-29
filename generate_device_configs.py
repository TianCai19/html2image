import json
import os
from playwright.sync_api import sync_playwright

# 定义要为其生成配置文件的设备列表 (从 Playwright.devices 中选取，以及自定义的设备键名)
# 您可以根据需要添加或修改这个列表
DEVICES_TO_GENERATE = [
    # Playwright 内置设备示例
    "iPhone X", "iPhone 11 Pro", "iPhone 12", "iPhone 13 Pro Max",
    "Pixel 5", "Pixel 7",
    "Galaxy S8", "Galaxy S9+",
    # "Galaxy Tab S4", # 平板，如果需要可以取消注释
    # "iPad Mini",     # 平板，如果需要可以取消注释

    # 自定义通用移动设备键名
    "generic_mobile",

    # 新增：为小红书优化的设备键名
    "xiaohongshu_3_4_1080p",
    "xiaohongshu_9_16_1080p",
    "xiaohongshu_1_1_1080p"
]

# 自定义一个通用移动设备
CUSTOM_GENERIC_MOBILE = {
    "generic_mobile": {
        "name": "Generic Mobile (390x844)", # 描述性名称
        "user_agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
        "viewport": {"width": 390, "height": 844}, # 一个常见的手机分辨率
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
    }
}

# 新增：为小红书优化的设备配置
CUSTOM_XIAOHONGSHU_DEVICES = {
    "xiaohongshu_3_4_1080p": { # 目标输出 1080x1440px
        "name": "Xiaohongshu 3:4 (1080x1440px)", # 描述性名称
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 360, "height": 480}, # 360*3=1080, 480*3=1440
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "xiaohongshu_9_16_1080p": { # 目标输出 1080x1920px
        "name": "Xiaohongshu 9:16 (1080x1920px)",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 360, "height": 640}, # 360*3=1080, 640*3=1920
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "xiaohongshu_1_1_1080p": { # 目标输出 1080x1080px
        "name": "Xiaohongshu 1:1 (1080x1080px)",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 360, "height": 360}, # 360*3=1080
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    }
}

CONFIG_DIR = os.path.join("configs", "devices")

def sanitize_filename(name):
    """将设备名称转换为适合做文件名的字符串 (使用配置键名，通常已符合要求)"""
    return name.lower().replace(" ", "_").replace("+", "plus").replace("-", "_")

def generate_configs():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        print(f"创建目录: {CONFIG_DIR}")

    generated_files = []
    skipped_devices = []

    with sync_playwright() as p:
        # 合并 Playwright 设备和所有自定义设备
        available_playwright_devices = p.devices
        all_potential_devices = {
            **available_playwright_devices,
            **CUSTOM_GENERIC_MOBILE,
            **CUSTOM_XIAOHONGSHU_DEVICES
        }

        print("开始生成设备配置文件...")
        for device_key in DEVICES_TO_GENERATE:
            if device_key not in all_potential_devices:
                print(f"警告: 设备键名 '{device_key}' 在 Playwright 或自定义设备定义中未找到，跳过。")
                skipped_devices.append(device_key)
                continue
            
            device_descriptor = all_potential_devices[device_key]

            # 确保是移动设备 (检查 is_mobile 属性)
            # Playwright 的设备描述符中已经有 is_mobile
            # 自定义的也应该有，如果想严格筛选，可以在这里加判断
            if not device_descriptor.get("is_mobile", False): # 对于非严格移动设备（如平板）也生成
                print(f"提示: 设备 '{device_key}' (is_mobile={device_descriptor.get('is_mobile')}) 正在生成配置。")

            # 如果原始描述符中没有 'name' 字段 (例如来自 p.devices 的)，则使用键名作为 name
            # 如果自定义描述符中有 'name' 字段，则使用它
            config_data = {
                "name": device_descriptor.get("name", device_key), # 优先使用配置中定义的name，否则用key
                **device_descriptor
            }
            
            # 使用原始的 device_key (通常已经是良好格式) 作为文件名基础
            # sanitize_filename 主要是为了处理 Playwright devices 中可能存在的空格等
            # 但由于我们现在用 DEVICES_TO_GENERATE 中的键名，这些键名设计时就应适合做文件名
            file_name_base = sanitize_filename(device_key) # device_key 如 "xiaohongshu_3_4_1080p"
            file_path = os.path.join(CONFIG_DIR, file_name_base + ".json")

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=4, ensure_ascii=False)
                generated_files.append(file_name_base + ".json")
            except IOError as e:
                print(f"错误: 无法写入文件 {file_path}: {e}")

    if generated_files:
        print(f"\n成功生成以下设备配置文件到 '{CONFIG_DIR}':")
        for fname in generated_files:
            print(f"- {fname}")
    
    if skipped_devices:
        print(f"\n以下设备键名由于未找到定义而被跳过:")
        for device_name in skipped_devices:
            print(f"- {device_name}")
            
    if not generated_files and not skipped_devices:
        print("没有生成任何配置文件。请检查 DEVICES_TO_GENERATE 列表以及自定义设备字典。")

if __name__ == "__main__":
    generate_configs()
    print("\n提示: 您现在可以在主截图脚本中使用 '--device <device_filename_without_extension>' 参数了。")
    print("例如: '--device iphone_x' 或 '--device xiaohongshu_3_4_1080p'")
    print("使用 '--list-devices' 查看可用设备。")