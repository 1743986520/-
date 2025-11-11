#!/bin/bash
set -euo pipefail  # 严格模式，出错立即退出

# ==================== 颜色输出函数 ====================
green() { echo -e "\033[32m$1\033[0m"; }
red() { echo -e "\033[31m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }

# ==================== 前置检查 ====================
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        red "❌ 错误：必须以 root 权限运行（请加 sudo）"
        exit 1
    fi
}

check_network() {
    yellow "🔍 检查网络连接..."
    if ! ping -c 2 tailscale.com >/dev/null 2>&1; then
        red "❌ 网络连接失败，请确保树莓派能访问外网"
        exit 1
    fi
}

# ==================== 核心安装与配置 ====================
install_tailscale() {
    yellow "📥 安装 Tailscale..."
    if command -v tailscale >/dev/null 2>&1; then
        green "✅ Tailscale 已安装，跳过安装步骤"
        return
    fi
    # 自动适配系统的安装脚本
    curl -fsSL https://tailscale.com/install.sh | sh
    green "✅ Tailscale 安装完成"
}

auth_tailscale() {
    yellow "🔐 启动 Tailscale 并获取认证链接..."
    if tailscale status >/dev/null 2>&1; then
        green "✅ Tailscale 已认证，跳过认证步骤"
        return
    fi
    sudo tailscale up  # 生成认证链接
    green "✅ 认证链接已显示，请用浏览器打开并登录（Google/GitHub）"
    read -p "📌 认证完成后按 Enter 继续..."
}

get_tailscale_ip() {
    yellow "📋 获取树莓派 Tailscale 内网 IP..."
    TS_IP=$(tailscale ip | head -n 1)
    if [ -z "$TS_IP" ]; then
        red "❌ 无法获取 Tailscale IP，请检查认证是否成功"
        exit 1
    fi
    green "✅ 树莓派 Tailscale IP：$TS_IP"
    echo -e "\n⚠️  请记下此 IP（后续可能用到）：$TS_IP"
}

config_exit_node() {
    yellow "🚀 配置出口节点（VPN 网关功能）..."
    # 开启出口节点并允许 IP 转发
    sudo tailscale up \
        --advertise-exit-node \
        --accept-routes \
        --allow-default-route
    green "✅ 出口节点功能已启用"

    # 配置 iptables 流量转发（伪装为树莓派公网 IP）
    yellow "🔧 配置 iptables 流量转发..."
    # 检测外网网卡（优先 eth0，没有则用 wlan0）
    if ip link show eth0 >/dev/null 2>&1; then
        OUTPUT_INTERFACE="eth0"
    elif ip link show wlan0 >/dev/null 2>&1; then
        OUTPUT_INTERFACE="wlan0"
    else
        red "❌ 无法识别外网网卡，请手动指定"
        exit 1
    fi
    # 添加 NAT 转发规则
    sudo iptables -t nat -A POSTROUTING -o "$OUTPUT_INTERFACE" -j MASQUERADE
    green "✅ iptables 转发规则添加完成（网卡：$OUTPUT_INTERFACE）"

    # 持久化 iptables 规则（防止重启失效）
    yellow "💾 持久化 iptables 配置..."
    if ! command -v iptables-save >/dev/null 2>&1; then
        sudo apt install iptables-persistent -y -qq  # 静默安装
    fi
    sudo netfilter-persistent save
    sudo netfilter-persistent reload
    green "✅ iptables 配置已持久化（重启不丢失）"
}

enable_ip_forward() {
    yellow "🔄 启用系统 IP 转发（必需）..."
    # 临时启用（立即生效）
    sudo sysctl -w net.ipv4.ip_forward=1
    sudo sysctl -w net.ipv6.conf.all.forwarding=1
    # 永久启用（重启生效）
    if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
        echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
    fi
    if ! grep -q "net.ipv6.conf.all.forwarding=1" /etc/sysctl.conf; then
        echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.conf
    fi
    sudo sysctl -p  # 加载配置
    green "✅ 系统 IP 转发已启用"
}

final_check() {
    yellow "✅ 进行最终状态检查..."
    if tailscale status | grep -q "Exit node: yes"; then
        green "🎉 Tailscale 出口节点部署成功！"
        echo -e "\n📋 后续操作指引："
        echo "1. 访问 Tailscale 管理后台（https://login.tailscale.com/admin）"
        echo "2. 找到你的树莓派设备 → 点击「...」→ 选择「Enable Exit Node」授权"
        echo "3. 国内设备安装 Tailscale 客户端，用同一账号登录"
        echo "4. 在客户端中选择树莓派作为「Exit Node」，即可通过树莓派上网"
    else
        red "❌ 部署失败，请查看日志或重新运行脚本"
        exit 1
    fi
}

# ==================== 主流程 ====================
clear
echo -e "=================================================="
echo -e "📡 Tailscale 出口节点一键部署脚本（树莓派专用）"
echo -e "=================================================="
echo -e "⚠️  运行前请确保："
echo -e "1. 树莓派已联网（能访问外网）"
echo -e "2. 拥有 Google/GitHub 账号（用于认证）"
echo -e "3. 以 root 权限运行（加 sudo）"
echo -e "==================================================\n"

check_root
check_network
install_tailscale
auth_tailscale
get_tailscale_ip
enable_ip_forward
config_exit_node
final_check

echo -e "\n🎉 操作完成！如有问题请参考 Tailscale 官方文档：https://tailscale.com/kb/1103/exit-nodes/"
