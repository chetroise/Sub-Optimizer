import os
import json
import sys
import requests

def final_correction_update(config):
    """
    执行基础的兼容性修正：
    1. 修正所有 rule_set 的格式错误（从列表变为字符串）。
    2. 将 dns.rules 中的 geosite:cn 替换为 rule_set:China-Site。
    """
    print("执行基础兼容性修正...")
    
    # 修正 dns.rules
    if 'dns' in config and 'rules' in config['dns']:
        new_dns_rules = []
        geosite_replaced = False
        for rule in config['dns']['rules']:
            if 'rule_set' in rule and isinstance(rule['rule_set'], list):
                if rule['rule_set']:
                    rule['rule_set'] = rule['rule_set'][0]
            if not geosite_replaced and 'geosite' in rule and rule['geosite'] == 'cn':
                del rule['geosite']
                rule['rule_set'] = 'China-Site'
                geosite_replaced = True
            new_dns_rules.append(rule)
        config['dns']['rules'] = new_dns_rules

    # 修正 route.rules
    if 'route' in config and 'rules' in config['route']:
        new_route_rules = []
        for rule in config['route']['rules']:
            if 'rule_set' in rule and isinstance(rule['rule_set'], list):
                if rule['rule_set']:
                    rule['rule_set'] = rule['rule_set'][0]
            new_route_rules.append(rule)
        config['route']['rules'] = new_route_rules
            
    print("基础兼容性修正完成。")
    return config

# ----------------------------------------------------
# ↓↓↓ 这是我们新增的“涡轮增压”功能 ↓↓↓
# ----------------------------------------------------
def optimized_dns_injection(config):
    """
    注入一个并行的、动态优选的DNS系统，以获得最佳性能。
    """
    print("开始注入动态DNS优化配置...")

    if 'dns' not in config:
        print("警告：原始配置中无'dns'模块，无法注入优化。")
        return config

    # 1. 定义我们自己的高性能DNS服务器
    # 动态国内DNS组 (自动测速选择最快的)
    dynamic_domestic_dns = {
        "tag": "DNS-Domestic-URLTest",
        "type": "urltest",
        "servers": [
            "DNS-Ali",
            "DNS-DNSPod",
            "DNS-Baidu"
        ],
        "url": "https://www.baidu.com",
        "interval": "10m"
    }
    # 具体的国内DNS服务器定义
    ali_dns = {"tag": "DNS-Ali", "address": "https://dns.alidns.com/dns-query", "detour": "Direct"}
    dnspod_dns = {"tag": "DNS-DNSPod", "address": "https://doh.pub/dns-query", "detour": "Direct"}
    baidu_dns = {"tag": "DNS-Baidu", "address": "https://doh.360.cn", "detour": "Direct"}
    
    # 安全的国外DNS (强制走代理)
    secure_foreign_dns = {
        "tag": "DNS-Foreign-Proxied",
        "address": "https://dns.google/dns-query",
        "detour": "🌏️主代理" # 重要：确保这个tag存在于你的outbounds中，通常是主代理选择器
    }

    # 2. 将我们的DNS服务器“添加”到现有服务器列表中 (无损注入)
    # 先删除可能存在的同名旧服务器，防止重复
    existing_servers = config['dns'].get('servers', [])
    tags_to_add = ["DNS-Domestic-URLTest", "DNS-Ali", "DNS-DNSPod", "DNS-Baidu", "DNS-Foreign-Proxied"]
    config['dns']['servers'] = [s for s in existing_servers if s.get('tag') not in tags_to_add]
    
    # 添加我们的新服务器
    config['dns']['servers'].extend([dynamic_domestic_dns, ali_dns, dnspod_dns, baidu_dns, secure_foreign_dns])
    print("  - 已成功注入5个新的DNS服务器定义。")

    # 3. 定义我们的新DNS规则
    # 国内网站规则
    china_rule = {
        "rule_set": "China-Site",
        "server": "DNS-Domestic-URLTest" # 指向我们动态测速的DNS组
    }
    # 其他所有网站的规则 (作为最终规则的补充)
    # 注意：这里我们不设置final，而是让它 fallback 到服务商自己的 final 规则
    
    # 4. 将我们的新规则“插入”到现有规则列表的顶端 (最高优先级)
    if 'rules' in config['dns']:
        # 同样，先删除可能存在的旧规则
        config['dns']['rules'] = [r for r in config['dns']['rules'] if r.get('server') != 'DNS-Domestic-URLTest']
        config['dns']['rules'].insert(0, china_rule)
        print("  - 已成功将动态国内DNS规则插入到规则列表顶部。")
    
    print("动态DNS优化注入完成！")
    return config

def main():
    subscription_url = os.environ.get("SUB_URL")
    if not subscription_url:
        print("错误：环境变量 SUB_URL 未设置！")
        sys.exit(1)
    
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

    # 先执行兼容性修正
    compatible_config = final_correction_update(original_config)
    # 再在修正后的基础上，注入DNS性能优化
    optimized_config = optimized_dns_injection(compatible_config)
    
    output_filename = "optimized_config.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(optimized_config, f, ensure_ascii=False, indent=2)
    
    print(f"优化后的配置已保存到 {output_filename}")

if __name__ == "__main__":
    main()
