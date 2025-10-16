import os
import json
import sys
import requests

def final_correction_update(config):
    """
    执行最终的、与手动验证结果完全一致的修正：
    1. 修正所有 rule_set 的格式错误（从列表变为字符串）。
    2. 将 dns.rules 中的 geosite:cn 替换为 rule_set:China-Site。
    """
    print("执行最终的、经过验证的配置修正脚本...")

    # --- 步骤 1: 修正 dns.rules 中的所有问题 ---
    if 'dns' in config and 'rules' in config['dns']:
        print("正在检查和修正 dns.rules...")
        new_dns_rules = []
        geosite_replaced = False
        for i, rule in enumerate(config['dns']['rules']):
            # 修正 rule_set 格式错误
            if 'rule_set' in rule and isinstance(rule['rule_set'], list):
                if rule['rule_set']:
                    rule['rule_set'] = rule['rule_set'][0]
                    print(f"  - 已修正 dns.rules 中第 {i+1} 条规则的 rule_set 格式。")

            # 替换 geosite:cn 为现代的、兼容的等效规则
            if not geosite_replaced and 'geosite' in rule and rule['geosite'] == 'cn':
                del rule['geosite']
                rule['rule_set'] = 'China-Site' # 使用服务商自己的规则集
                geosite_replaced = True
                print(f"  - 已将 dns.rules 中第 {i+1} 条规则的 geosite:cn 替换为 rule_set:China-Site。")
            
            new_dns_rules.append(rule)
        
        config['dns']['rules'] = new_dns_rules

    # --- 步骤 2: 修正 route.rules 中的所有 rule_set 格式错误 ---
    if 'route' in config and 'rules' in config['route']:
        print("正在检查和修正 route.rules...")
        new_route_rules = []
        for i, rule in enumerate(config['route']['rules']):
            if 'rule_set' in rule and isinstance(rule['rule_set'], list):
                if rule['rule_set']:
                    rule['rule_set'] = rule['rule_set'][0]
                    print(f"  - 已修正 route.rules 中第 {i+1} 条规则的 rule_set 格式。")
            new_route_rules.append(rule)
            
        config['route']['rules'] = new_route_rules
            
    print("所有修正已完成。")
    return config

def main():
    subscription_url = os.environ.get("SUB_URL")
    if not subscription_url:
        print("错误：环境变量 SUB_URL 未设置！")
        sys.exit(1)
    
    # 容错机制：当获取失败时，使用上一次成功的配置
    print("正在从订阅链接获取配置...")
    try:
        response = requests.get(subscription_url, timeout=15)
        response.raise_for_status()
        original_config = response.json()
        print("成功获取并解析 JSON 配置。")
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"警告：获取或解析新配置失败 - {e}")
        print("将跳过本次更新，以保留上一次成功的配置。")
        sys.exit(0) 

    updated_config = final_correction_update(original_config)
    
    output_filename = "optimized_config.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(updated_config, f, ensure_ascii=False, indent=2)
    
    print(f"优化后的配置已保存到 {output_filename}")

if __name__ == "__main__":
    main()
