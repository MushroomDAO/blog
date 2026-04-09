#!/bin/bash
# Nostr CLI 工具安装与测试脚本

set -e

echo "🚀 Nostr CLI 工具安装脚本"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查代理
if [ -n "$http_proxy" ]; then
    echo -e "${GREEN}✓${NC} 代理已开启: $http_proxy"
else
    echo -e "${YELLOW}⚠${NC} 代理未开启，建议开启代理以加速下载"
    echo "  运行: source ~/.zshrc_proxy && proxy_on"
fi

echo ""
echo "📦 步骤 1/4: 检查 Go 安装"
if command -v go &> /dev/null; then
    echo -e "${GREEN}✓${NC} Go 已安装: $(go version)"
else
    echo -e "${RED}✗${NC} Go 未安装，请先安装 Go"
    exit 1
fi

echo ""
echo "📦 步骤 2/4: 安装 nak"
if command -v nak &> /dev/null; then
    echo -e "${GREEN}✓${NC} nak 已安装: $(nak --version 2>/dev/null || echo 'version unknown')"
else
    echo "  正在安装 nak..."
    go install github.com/fiatjaf/nak@latest
    if command -v nak &> /dev/null; then
        echo -e "${GREEN}✓${NC} nak 安装成功"
    else
        echo -e "${RED}✗${NC} nak 安装失败，尝试使用 Homebrew..."
        brew install nak
    fi
fi

echo ""
echo "📦 步骤 3/4: 安装 algia"
if command -v algia &> /dev/null; then
    echo -e "${GREEN}✓${NC} algia 已安装: $(algia --version 2>/dev/null || echo 'version unknown')"
else
    echo "  正在安装 algia..."
    go install github.com/mattn/algia@latest
    if command -v algia &> /dev/null; then
        echo -e "${GREEN}✓${NC} algia 安装成功"
    else
        echo -e "${RED}✗${NC} algia 安装失败"
    fi
fi

echo ""
echo "📦 步骤 4/4: 验证安装"
echo "-------------------"
echo "PATH 检查:"
echo "  $HOME/go/bin"
echo ""

# 检查 PATH
if [[ ":$PATH:" != *":$HOME/go/bin:"* ]]; then
    echo -e "${YELLOW}⚠${NC} 请将 $HOME/go/bin 添加到 PATH"
    echo "  运行: echo 'export PATH=\$PATH:\$HOME/go/bin' >> ~/.zshrc"
    export PATH=$PATH:$HOME/go/bin
fi

# 验证命令
echo "工具验证:"
NOK=0

if command -v nak &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} nak: $(which nak)"
    echo -n "    版本: "
    nak --version 2>/dev/null || echo "unknown"
    NOK=$((NOK+1))
else
    echo -e "  ${RED}✗${NC} nak: 未找到"
fi

if command -v algia &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} algia: $(which algia)"
    echo -n "    版本: "
    algia --version 2>/dev/null || echo "unknown"
    NOK=$((NOK+1))
else
    echo -e "  ${RED}✗${NC} algia: 未找到"
fi

echo ""
echo "=========================="
if [ $NOK -eq 2 ]; then
    echo -e "${GREEN}✅ 所有工具安装成功!${NC}"
    echo ""
    echo "快速开始:"
    echo "  nak key-gen              # 生成密钥"
    echo "  nak req -k 1 --limit 10 wss://relay.damus.io  # 查询事件"
    echo "  algia timeline           # 查看时间线"
    echo "  algia post 'Hello!'      # 发布笔记"
else
    echo -e "${YELLOW}⚠️ 部分工具安装未完成${NC}"
    echo "请检查网络连接和代理设置"
fi
