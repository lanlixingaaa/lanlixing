# 大麦网抢票系统 - 用户指南

## 1. 系统概述

大麦网抢票系统是一款强大的自动化工具，旨在简化大麦平台上的购票流程。它具备实时票源监控、智能选座和反检测机制，确保在高需求活动期间的可靠性能。

### 核心功能
- **自动登录**：支持用户名/密码和手机号两种认证方式
- **实时监控**：可配置刷新间隔的持续票源检查
- **智能选座**：基于用户定义的偏好（价格范围、区域、排数、座位类型）
- **自动结账**：简化的订单提交和支付方式选择
- **反检测机制**：随机延迟、用户代理轮换和浏览器指纹混淆
- **全面错误处理**：带指数退避的智能重试逻辑
- **详细日志记录**：实时进度跟踪和故障排除信息

## 2. 前置条件

在安装和使用系统之前，请确保您的环境满足以下要求：

| 要求 | 规格 |
|------|------|
| **操作系统** | Windows 10/11, macOS, Linux |
| **Python 版本** | Python 3.8 或更高版本 |
| **Pip 包管理器** | 最新版本 |
| **网络连接** | 稳定的宽带连接 |
| **存储空间** | 至少 500MB 用于 Playwright 浏览器 |

## 3. 安装指南

按照以下步骤安装大麦网抢票系统：

### 步骤1：下载或克隆项目

```bash
# 使用 Git 克隆（如果可用）
git clone <repository-url>
cd d:\T-code

# 或直接下载并解压项目文件到 d:\T-code
```

### 步骤2：安装所需依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

### 步骤3：安装 Playwright 浏览器

```bash
# 为 Playwright 安装 Chromium 浏览器
playwright install chromium
```

### 步骤4：验证安装

```bash
# 检查 Python 是否正确安装
python --version

# 检查 Playwright 是否正确安装
playwright --version
```

## 4. 初始配置

系统使用 YAML 配置文件 (`config.yaml`) 进行所有设置。根据您的需要自定义它：

### 访问配置文件

```bash
# Windows
notepad config.yaml

# macOS/Linux
nano config.yaml
```

### 配置部分

#### 4.1 认证设置

```yaml
login:
  username: "your_damai_username"      # 您的大麦用户名（可选）
  password: "your_damai_password"      # 您的大麦密码（可选）
  phone_number: "13800138000"          # 用于短信登录的手机号（可选）
```

**注意**：请提供用户名/密码或手机号其中一种，不要同时提供。

#### 4.2 活动设置

```yaml
event:
  event_id: "12345678"                 # 大麦 URL 中的活动 ID
  venue_id: ""                         # 可选：场馆 ID（不确定则留空）
  performance_id: ""                   # 可选：场次 ID（不确定则留空）
  ticket_quantity: 2                   # 购买票数（1-6）
```

**如何查找活动 ID**：
- 导航到大麦网的活动页面
- 从 URL 中提取 ID：`https://detail.damai.cn/item.htm?id=12345678`

#### 4.3 票券偏好

```yaml
ticket_preferences:
  price_ranges: ["380", "580"]        # 首选价格范围（例如：["180", "380"]）
  sections: ["内场", "看台"]             # 首选区域（例如：["内场A区", "看台1层"]）
  rows: ["1-10"]                       # 首选排数（例如：["1-5", "VIP"]）
  seat_type: "内场"                     # 首选座位类型（例如："内场", "看台"）
```

#### 4.4 监控设置

```yaml
monitoring:
  refresh_interval: 5                   # 检查可用性的间隔时间（秒）（最小值：5）
  max_monitoring_time: 3600             # 最大监控时间（秒）
  check_in_advance: 300                 # 开售前开始检查的时间（秒）
```

#### 4.5 反检测设置

```yaml
anti_detect:
  random_delay_min: 0.5                 # 操作间的最小随机延迟
  random_delay_max: 3.0                 # 操作间的最大随机延迟
  rotate_user_agent: true               # 启用用户代理轮换
  use_proxy: false                      # 启用代理使用（实验性）
  proxy_list: []                        # 代理列表（如果 use_proxy 为 true）
```

#### 4.6 结账设置

```yaml
checkout:
  auto_submit_order: true               # 选座后自动提交订单
  payment_method: "alipay"             # 支付方式："alipay" 或 "wechat"
  timeout: 30                           # 结账等待超时（秒）
```

## 5. 基本使用

### 5.1 运行系统

```bash
# 基本使用（使用默认 config.yaml）
python damai_ticket.py

# 使用自定义配置文件
python damai_ticket.py custom_config.yaml
```

### 5.2 预期工作流程

1. **初始化**：系统加载配置并设置日志
2. **浏览器设置**：启动带有反检测设置的 Chrome 浏览器
3. **登录**：使用配置的凭据自动登录大麦网
4. **监控**：持续检查目标活动的票源可用性
5. **选座**：根据用户偏好自动选择票券
6. **结账**：进入结账流程并选择支付方式
7. **完成**：通知用户并记录结果

### 5.3 监控流程

系统在控制台提供实时日志，并将日志保存到 `damai_ticket.log`。关键日志消息包括：

```
2026-03-30 13:30:03.970 | INFO     | Configuration loaded successfully
2026-03-30 13:30:04.576 | INFO     | Browser initialized successfully
2026-03-30 13:30:04.576 | INFO     | Starting login process
2026-03-30 13:30:07.481 | INFO     | Login successful
2026-03-30 13:30:07.481 | INFO     | Starting ticket availability monitoring
2026-03-30 13:35:22.123 | INFO     | Tickets are now available! Starting purchase process
```

## 6. 高级功能

### 6.1 自定义配置文件

为不同活动创建多个配置文件：

```bash
# 为演唱会创建配置
cp config.yaml concert_config.yaml

# 编辑演唱会配置
notepad concert_config.yaml

# 使用演唱会配置运行
python damai_ticket.py concert_config.yaml
```

### 6.2 代理使用（实验性）

```yaml
anti_detect:
  use_proxy: true
  proxy_list:
    - "http://proxy1:8080"
    - "http://proxy2:8080"
    - "socks5://proxy3:1080"
```

### 6.3 无头模式（生产环境）

```yaml
# 编辑 damai_ticket.py 中的 initialize_browser 方法
# 将 headless: False 改为 headless: True
```

### 6.4 自定义日志

```yaml
logging:
  level: "DEBUG"                         # 日志级别：DEBUG, INFO, WARNING, ERROR
  log_file: "custom_log.log"             # 自定义日志文件名
  max_log_size: 20                       # 日志文件最大大小（MB）
  backup_count: 10                       # 保留的备份日志文件数
```

## 7. 常见使用场景

### 7.1 场景1：演唱会门票

**配置示例**：
```yaml
event:
  event_id: "12345678"                 # 演唱会活动 ID
  ticket_quantity: 2                   # 购买 2 张票
ticket_preferences:
  price_ranges: ["580", "880"]        # 偏好中等价位
  sections: ["内场", "看台1层"]           # 偏好内场或下层看台
  rows: ["1-20"]                       # 偏好前排
  seat_type: "内场"                     # 优先内场座位
monitoring:
  refresh_interval: 5                   # 每 5 秒检查一次
  max_monitoring_time: 3600             # 最多监控 1 小时
```

### 7.2 场景2： theater演出

**配置示例**：
```yaml
event:
  event_id: "87654321"                 # 话剧活动 ID
  ticket_quantity: 4                   # 为家庭购买 4 张票
ticket_preferences:
  price_ranges: ["180", "280"]        # 预算友好型价格
  sections: ["二楼", "三楼"]             # 包厢区域，视野更好
  rows: ["1-10"]                       # 包厢前排
  seat_type: "看台"                     # 剧院座位类型
checkout:
  payment_method: "wechat"             # 使用微信支付
```

### 7.3 场景3：体育赛事

**配置示例**：
```yaml
event:
  event_id: "98765432"                 # 体育赛事 ID
  ticket_quantity: 1                   # 单张票
ticket_preferences:
  price_ranges: ["280", "480"]        # 中等价位
  sections: ["主场区", "VIP区"]           # 主队区域
  rows: ["5-15"]                       # 中间排，平衡视野和价格
  seat_type: "看台"                     # 体育场座位类型
anti_detect:
  random_delay_min: 1.0                 # 更长的延迟以避免检测
  random_delay_max: 4.0
```

## 8. 故障排除

### 8.1 常见问题及解决方案

#### 问题1：登录失败
**症状**：`ERROR | Login failed: No login credentials provided`
**解决方案**：确保您在 `config.yaml` 中提供了有效的登录凭据。使用用户名/密码或手机号其中一种。

#### 问题2：浏览器初始化错误
**症状**：`ERROR | Failed to initialize browser: BrowserType.launch() got an unexpected keyword argument 'user_agent'`
**解决方案**：确保 Playwright 浏览器已正确安装：`playwright install chromium`

#### 问题3：被大麦网检测
**症状**：浏览器显示 "Access Denied" 或验证码挑战
**解决方案**：
- 在配置中增加随机延迟：`random_delay_min: 2.0`, `random_delay_max: 5.0`
- 减少刷新间隔：`refresh_interval: 10`
- 启用代理使用
- 使用真实浏览器行为（测试时避免无头模式）

#### 问题4：选座失败
**症状**：`ERROR | Ticket selection failed: Element not found`
**解决方案**：大麦网可能更新了页面结构。检查并更新代码中的 CSS 选择器。

#### 问题5：网络超时
**症状**：`ERROR | Monitoring error: TimeoutError`
**解决方案**：
- 检查您的网络连接
- 增加重试次数：`retry_attempts: 10`
- 启用代理使用

### 8.2 调试模式

启用调试日志以进行详细故障排除：

```yaml
logging:
  level: "DEBUG"
```

### 8.3 手动登录解决方法

如果自动登录失败：
1. 手动运行脚本
2. 当浏览器打开时，手动登录大麦网
3. 关闭浏览器并使用相同配置重新启动脚本

## 9. 法律和道德考虑

**重要**：本工具仅用于个人使用。请确保您遵守大麦网的服务条款和所有适用法律。

### 关键准则
- **公平使用**：请勿使用该工具购买过多门票或从事黄牛活动
- **合规性**：尊重大麦网的反自动化政策
- **责任**：用户对使用本工具产生的任何后果负全部责任
- **无恶意使用**：请勿使用该工具进行 DDoS 攻击或过度请求

### 大麦网服务条款
- 禁止使用自动化脚本
- 过度请求可能导致账号被暂停
- 在许多司法管辖区，转售通过自动化方式购买的门票是非法的

## 10. 预期结果

### 10.1 成功购票

```
2026-03-30 13:30:03.970 | INFO     | Starting Damai Ticket Purchasing System
2026-03-30 13:30:04.576 | INFO     | Browser initialized successfully
2026-03-30 13:30:07.481 | INFO     | Login successful
2026-03-30 13:35:22.123 | INFO     | Tickets are now available! Starting purchase process
2026-03-30 13:35:23.456 | INFO     | Selecting 2 tickets
2026-03-30 13:35:25.789 | INFO     | Selecting ticket type: 580元内场
2026-03-30 13:35:28.123 | INFO     | Starting checkout process
2026-03-30 13:35:30.456 | INFO     | Order submitted successfully! Please complete payment within 15 minutes.
2026-03-30 13:35:30.612 | INFO     | Checkout process completed. Please complete payment manually if needed.
```

### 10.2 监控结果

```
2026-03-30 13:30:07.481 | INFO     | Starting ticket availability monitoring
2026-03-30 13:30:07.623 | INFO     | Checking ticket availability for event 12345678
2026-03-30 13:30:10.890 | INFO     | Tickets not available yet. Checking again in 5 seconds
2026-03-30 13:30:15.901 | INFO     | Checking ticket availability for event 12345678
2026-03-30 13:30:18.123 | INFO     | Tickets not available yet. Checking again in 5 seconds
...
```

### 10.3 错误处理结果

```
2026-03-30 13:30:07.481 | INFO     | Starting ticket availability monitoring
2026-03-30 13:30:07.623 | INFO     | Checking ticket availability for event 12345678
2026-03-30 13:30:10.890 | WARNING  | Attempt 1/5 failed: Network timeout
2026-03-30 13:30:12.901 | INFO     | Retrying...
2026-03-30 13:30:15.123 | INFO     | Checking ticket availability for event 12345678
2026-03-30 13:30:17.456 | INFO     | Tickets not available yet. Checking again in 5 seconds
```

## 11. 性能优化技巧

1. **减少资源使用**：生产环境使用无头模式
2. **优化监控**：使用合理的刷新间隔（5-10 秒）
3. **最小化浏览器交互**：减少不必要的点击和页面加载
4. **使用高效选择器**：将 CSS 选择器更新为更具体和快速的选择器
5. **监控系统资源**：运行脚本时关闭不必要的应用程序

## 12. 支持和维护

### 12.1 更新系统

```bash
# 拉取最新更改（如果使用 Git）
git pull

# 更新依赖
pip install -r requirements.txt --upgrade

# 更新 Playwright 浏览器
playwright install --with-deps chromium
```

### 12.2 自定义开发

系统采用模块化架构，便于扩展：
- **添加新认证方式**：修改 `login` 方法
- **实现高级选座**：更新 `_select_ticket_type`
- **添加支付方式**：增强 `checkout` 方法
- **改进反检测**：更新 `_setup_anti_detect`

## 13. 结论

大麦网抢票系统为自动化购票流程提供了强大而灵活的解决方案。通过遵循本指南，您可以配置系统以满足您的特定需求，并增加您在高需求活动中成功购票的机会。

请始终负责任地使用该系统，遵守所有适用法律和网站服务条款，并优先考虑所有用户公平获取门票的权利。

---

**免责声明**：本工具仅用于教育和研究目的。作者不鼓励或纵容任何非法或不道德使用本软件。用户对使用本工具的行为负全部责任。

**版本**：1.0.0
**最后更新**：2026-03-30
**作者**：自动售票系统团队
