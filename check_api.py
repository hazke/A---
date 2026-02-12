"""
API连接诊断工具
"""
import requests
import sys

def check_backend():
    """检查后端API是否可访问"""
    print("=" * 50)
    print("API连接诊断")
    print("=" * 50)
    print()
    
    base_url = "http://localhost:8000"
    
    # 1. 检查健康检查端点
    print("[1/4] 检查后端服务...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✓ 后端服务运行正常")
        else:
            print(f"  ✗ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ 无法连接到后端服务")
        print(f"  请确保后端已启动: python start_backend.py")
        return False
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False
    
    # 2. 检查API文档
    print("\n[2/4] 检查API文档...")
    try:
        response = requests.get(f"{base_url}/api/docs", timeout=5)
        if response.status_code == 200:
            print(f"  ✓ API文档可访问: {base_url}/api/docs")
        else:
            print(f"  ⚠ API文档响应异常: {response.status_code}")
    except Exception as e:
        print(f"  ⚠ 无法访问API文档: {e}")
    
    # 3. 检查策略列表API
    print("\n[3/4] 检查策略API...")
    try:
        response = requests.get(f"{base_url}/api/v1/strategies", timeout=5)
        if response.status_code == 200:
            strategies = response.json()
            print(f"  ✓ 策略列表API正常，当前有 {len(strategies)} 个策略")
        else:
            print(f"  ✗ 策略列表API异常: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ 策略列表API失败: {e}")
        return False
    
    # 4. 检查策略类型API
    print("\n[4/4] 检查策略类型...")
    try:
        response = requests.get(f"{base_url}/api/v1/strategy-types", timeout=5)
        if response.status_code == 200:
            types_data = response.json()
            available = types_data.get('available', [])
            registered = types_data.get('registered', [])
            print(f"  ✓ 可用策略类型:")
            for st in available:
                status = "✓" if st['registered'] else "✗"
                print(f"    {status} {st['label']} ({st['value']})")
            print(f"  已注册: {', '.join(registered) if registered else '无'}")
        else:
            print(f"  ⚠ 策略类型API异常: {response.status_code}")
    except Exception as e:
        print(f"  ⚠ 策略类型API失败: {e}")
    
    print()
    print("=" * 50)
    print("诊断完成")
    print("=" * 50)
    print()
    print("如果后端服务无法连接，请：")
    print("1. 确保后端已启动: python start_backend.py")
    print("2. 检查端口8000是否被占用")
    print("3. 检查防火墙设置")
    print()
    
    return True

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("[错误] 需要安装 requests 库")
        print("运行: pip install requests")
        sys.exit(1)
    
    success = check_backend()
    sys.exit(0 if success else 1)

