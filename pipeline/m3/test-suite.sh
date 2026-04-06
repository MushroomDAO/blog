#!/bin/bash
# M3 Xiaohongshu Pipeline Test Suite
# 完整的测试脚本套件

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# MCP URL
MCP_URL="${XHS_MCP_URL:-http://localhost:3456}"
TEST_DIR="/tmp/xhs-tests"
mkdir -p "$TEST_DIR"

# 测试计数
TESTS_PASSED=0
TESTS_FAILED=0

# 打印函数
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# ==================== 1. MCP 连接测试 ====================

test_mcp_health() {
    print_header "Test 1: MCP Health Check"
    
    if curl -s "${MCP_URL}/health" > /dev/null 2>&1; then
        print_success "MCP server is healthy"
        return 0
    else
        print_error "MCP server is not responding at ${MCP_URL}"
        return 1
    fi
}

test_mcp_login_status() {
    print_header "Test 2: Login Status Check"
    
    local response
    response=$(curl -s "${MCP_URL}/api/v1/login/status" 2>/dev/null || echo '{"success":false}')
    
    if echo "$response" | grep -q '"is_logged_in":true'; then
        print_success "Already logged in"
        return 0
    elif echo "$response" | grep -q '"is_logged_in":false'; then
        print_info "Not logged in - QR code login required"
        return 1
    else
        print_error "Failed to check login status"
        return 1
    fi
}

test_mcp_get_qrcode() {
    print_header "Test 3: Get Login QR Code"
    
    local response
    response=$(curl -s "${MCP_URL}/api/v1/login/qrcode" 2>/dev/null || echo '{"success":false}')
    
    if echo "$response" | grep -q '"success":true'; then
        print_success "QR code generated successfully"
        # 保存二维码图片
        echo "$response" | grep -o '"img":"[^"]*"' | cut -d'"' -f4 | head -1 | base64 -d > "$TEST_DIR/qrcode.png" 2>/dev/null || true
        print_info "QR code saved to: $TEST_DIR/qrcode.png"
        return 0
    else
        print_error "Failed to generate QR code"
        return 1
    fi
}

# ==================== 2. 内容优化器测试 ====================

test_optimizer() {
    print_header "Test 4: Content Optimizer"
    
    # 创建测试内容
    cat > "$TEST_DIR/test-content.md" << 'EOF'
---
title: "AI技术解析：大语言模型的工作原理"
date: 2024-01-15
---

# 大语言模型的工作原理

大语言模型（LLM）是近年来人工智能领域最重要的突破之一。

## 核心概念

这些模型通过海量文本数据进行训练，学习语言的模式和结构。

## 应用场景

从聊天机器人到代码生成，LLM正在改变我们的工作方式。
EOF

    if python3 pipeline/m3/optimizer.py "$TEST_DIR/test-content.md" > "$TEST_DIR/optimized.json" 2>&1; then
        print_success "Content optimized successfully"
        
        # 验证输出
        if [ -s "$TEST_DIR/optimized.json" ]; then
            print_info "Optimized content saved to: $TEST_DIR/optimized.json"
            echo "Sample output:"
            head -5 "$TEST_DIR/optimized.json"
        fi
        return 0
    else
        print_error "Content optimization failed"
        cat "$TEST_DIR/optimized.json" 2>/dev/null || true
        return 1
    fi
}

# ==================== 3. 封面生成器测试 ====================

test_cover_generator() {
    print_header "Test 5: Cover Generator"
    
    if python3 pipeline/m3/cover_generator.py "测试标题" --output "$TEST_DIR/test-cover.jpg" 2>&1; then
        if [ -f "$TEST_DIR/test-cover.jpg" ]; then
            local filesize
            filesize=$(ls -lh "$TEST_DIR/test-cover.jpg" | awk '{print $5}')
            print_success "Cover generated: $filesize"
            print_info "Cover saved to: $TEST_DIR/test-cover.jpg"
            return 0
        else
            print_error "Cover file not found"
            return 1
        fi
    else
        print_error "Cover generation failed"
        return 1
    fi
}

# ==================== 4. 渲染器测试 ====================

test_renderer() {
    print_header "Test 6: Content Renderer"
    
    # 创建测试输入
    cat > "$TEST_DIR/render-test.json" << 'EOF'
{
    "title": "测试标题",
    "content": "🎯 核心要点\n\n📌 第一点内容\n📌 第二点内容\n\n🎉 结束语",
    "tags": ["AI", "技术"]
}
EOF

    if node pipeline/m3/renderer/xiaohongshu-renderer.js "$TEST_DIR/render-test.json" > "$TEST_DIR/rendered.html" 2>&1; then
        if [ -s "$TEST_DIR/rendered.html" ]; then
            print_success "Content rendered successfully"
            print_info "Rendered HTML saved to: $TEST_DIR/rendered.html"
            return 0
        else
            print_error "Rendered output is empty"
            return 1
        fi
    else
        print_error "Rendering failed"
        cat "$TEST_DIR/rendered.html" 2>/dev/null || true
        return 1
    fi
}

# ==================== 5. 完整集成测试 ====================

test_full_pipeline() {
    print_header "Test 7: Full Pipeline Integration"
    
    # 创建测试文章
    cat > "$TEST_DIR/full-test.md" << 'EOF'
---
title: "测试文章：AI发展趋势"
date: 2024-01-15
tags: ["AI", "技术", "趋势"]
---

# AI发展趋势分析

人工智能正在快速发展，以下是几个关键趋势：

## 大语言模型

ChatGPT等大语言模型改变了人机交互方式。

## 多模态AI

AI不仅能处理文本，还能理解图像、音频和视频。

## AI应用落地

从医疗到教育，AI正在各行各业落地应用。
EOF

    print_info "Running full pipeline..."
    
    # Step 1: Optimize
    if ! python3 pipeline/m3/optimizer.py "$TEST_DIR/full-test.md" > "$TEST_DIR/full-optimized.json" 2>&1; then
        print_error "Pipeline failed at optimizer step"
        return 1
    fi
    
    # Step 2: Generate cover
    local title
    title=$(cat "$TEST_DIR/full-optimized.json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('title',''))" 2>/dev/null || echo "测试")
    
    if ! python3 pipeline/m3/cover_generator.py "$title" --output "$TEST_DIR/full-cover.jpg" 2>&1; then
        print_error "Pipeline failed at cover generation step"
        return 1
    fi
    
    # Step 3: Render
    if ! node pipeline/m3/renderer/xiaohongshu-renderer.js "$TEST_DIR/full-optimized.json" > "$TEST_DIR/full-rendered.html" 2>&1; then
        print_error "Pipeline failed at renderer step"
        return 1
    fi
    
    print_success "Full pipeline completed successfully"
    return 0
}

# ==================== 6. 发布测试（可选，需要登录） ====================

test_publish_dry_run() {
    print_header "Test 8: Publisher Module (Dry Run)"
    
    # 测试 publisher 模块是否可以加载
    if python3 -c "import sys; sys.path.insert(0, 'pipeline/m3'); from publisher import XiaohongshuPublisher; print('Publisher module loaded')" 2>&1; then
        print_success "Publisher module loads correctly"
        return 0
    else
        print_error "Failed to load publisher module"
        return 1
    fi
}

# ==================== 7. MCP API 功能测试 ====================

test_mcp_search() {
    print_header "Test 9: MCP Search API"
    
    local response
    response=$(curl -s "${MCP_URL}/api/v1/feeds/search?keyword=AI" 2>/dev/null || echo '{"success":false}')
    
    if echo "$response" | grep -q '"success":true'; then
        local count
        count=$(echo "$response" | grep -o '"count":[0-9]*' | cut -d':' -f2 || echo "0")
        print_success "Search API working (found $count results)"
        return 0
    else
        print_info "Search API may require login (expected if not logged in)"
        return 0  # 不要求登录，所以不算失败
    fi
}

test_mcp_list_feeds() {
    print_header "Test 10: MCP List Feeds API"
    
    local response
    response=$(curl -s "${MCP_URL}/api/v1/feeds/list" 2>/dev/null || echo '{"success":false}')
    
    if echo "$response" | grep -q '"success":true'; then
        print_success "List feeds API working"
        return 0
    else
        print_info "List feeds API may require login"
        return 0
    fi
}

# ==================== 主函数 ====================

run_all_tests() {
    print_header "🧪 M3 Xiaohongshu Pipeline Test Suite"
    print_info "MCP URL: ${MCP_URL}"
    print_info "Test Directory: ${TEST_DIR}"
    
    # MCP 连接测试
    test_mcp_health || true
    test_mcp_login_status || true
    test_mcp_get_qrcode || true
    
    # 模块测试
    test_optimizer || true
    test_cover_generator || true
    test_renderer || true
    
    # 集成测试
    test_full_pipeline || true
    test_publish_dry_run || true
    
    # MCP API 测试
    test_mcp_search || true
    test_mcp_list_feeds || true
    
    # 汇总
    print_header "📊 Test Summary"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed!${NC}"
        return 0
    else
        echo -e "\n${YELLOW}⚠️  Some tests failed. Check output above.${NC}"
        return 1
    fi
}

# 运行单个测试
run_single_test() {
    case "$1" in
        health) test_mcp_health ;;
        login) test_mcp_login_status ;;
        qrcode) test_mcp_get_qrcode ;;
        optimizer) test_optimizer ;;
        cover) test_cover_generator ;;
        renderer) test_renderer ;;
        pipeline) test_full_pipeline ;;
        publisher) test_publish_dry_run ;;
        search) test_mcp_search ;;
        feeds) test_mcp_list_feeds ;;
        *) echo "Unknown test: $1"; exit 1 ;;
    esac
}

# 主入口
case "${1:-all}" in
    all)
        run_all_tests
        ;;
    *)
        run_single_test "$1"
        ;;
esac
