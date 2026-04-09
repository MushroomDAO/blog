# Network Switch Skill

网络代理切换工具，用于在需要连接外网(GitHub/Google等)时快速开启代理，完成后关闭代理。

## 快速使用

```bash
# 加载代理配置
source ~/.zshrc_proxy

# 开启代理
proxy_on

# 查看代理状态
proxy_status

# 关闭代理
proxy_off
```

## 配置详情

`~/.zshrc_proxy` 文件内容：

```bash
# 代理快捷命令
proxy_on() {
    export https_proxy=http://127.0.0.1:7890
    export http_proxy=http://127.0.0.1:7890
    export all_proxy=socks5://127.0.0.1:7890
    echo "✅ 代理已开启: $http_proxy"
}

proxy_off() {
    unset https_proxy
    unset http_proxy
    unset all_proxy
    echo "❌ 代理已关闭"
}

proxy_status() {
    echo "http_proxy:  ${http_proxy:-未设置}"
    echo "https_proxy: ${https_proxy:-未设置}"
    echo "all_proxy:   ${all_proxy:-未设置}"
}

# 默认自动开启代理
# proxy_on
proxy_off
```

## 使用场景

### 场景1: 安装 Go 工具
```bash
source ~/.zshrc_proxy && proxy_on
go install github.com/fiatjaf/nak@latest
go install github.com/mattn/algia@latest
proxy_off
```

### 场景2: 下载 GitHub Release
```bash
source ~/.zshrc_proxy && proxy_on
curl -L -o tool.tar.gz "https://github.com/.../release.tar.gz"
proxy_off
```

### 场景3: 在命令中使用代理
```bash
# 单行设置
export https_proxy=http://127.0.0.1:7890 && curl https://api.github.com/...

# 或使用 env
env http_proxy=http://127.0.0.1:7890 curl https://api.github.com/...
```

## 环境变量说明

| 变量 | 协议 | 地址 | 用途 |
|------|------|------|------|
| http_proxy | HTTP | http://127.0.0.1:7890 | HTTP 请求代理 |
| https_proxy | HTTP | http://127.0.0.1:7890 | HTTPS 请求代理 |
| all_proxy | SOCKS5 | socks5://127.0.0.1:7890 | 全局代理 |

## 注意事项

1. **代理端口 7890** 默认是 Clash 的 mixed-port
2. **单条命令**中设置的环境变量只对当前命令有效
3. **多条命令**需要先 source 再执行
4. **用完关闭**代理以避免影响本地服务访问

## 故障排查

```bash
# 测试代理是否工作
curl -s --connect-timeout 5 -x http://127.0.0.1:7890 https://github.com

# 检查端口是否监听
lsof -i :7890

# 查看当前代理设置
env | grep -i proxy
```
