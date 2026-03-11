---
name: collector
description: Collect and organize articles/files into markdown format with metadata. Triggered when user says "标记" (mark) followed by sentence, file or URL. Stores articles in my-ai-memory/collect/YYYY-MM-DD/ with title, date, tags, summary, content separated by ---. Supports search by tag/title/summary.
---

# Article Collector

## 使用方式

当用户说"标记"时，收藏灵感片段、文件或网页。

## 工作流程

### 1. 接收输入

用户说"标记"后，会提供：
- **句子文本**：文本
- **文件路径**：本地文件
- **网页 URL**：需用 `web_fetch` 获取内容

### 2. 提取内容

**URL:**
- 用 `web_fetch` 工具获取（extractMode: markdown）
- 提取标题（HTML title 或内容首行）

**文件:**
- 用 `read` 工具读取
- 从文件名提取标题

### 3. 生成元数据

必填字段（单独一行）：
- **标题**
- **创建日期**（YYYY-MM-DD）
- **标签**（3-5 个关键词）
- **摘要**（50-100 字）
- **原文**

用 `---` 分隔元数据和原文。

### 4. 存储文件

**路径：** `/root/clawd/codes/my-ai-memory/collect/YYYY-MM-DD/文件名.md`

**文件名规则：**
- 文件：原文件名（替换扩展名为 .md）
- URL：标题转连字符

### 5. Git 同步

```bash
cd /root/clawd/codes/my-ai-memory
git add collect/
git commit -m "Collect article: [标题]"
git push
```

## 脚本工具

使用 `scripts/article-collector.py`:

```bash
# 收藏文章
python3 /root/clawd/skills/article-collector/scripts/article-collector.py collect \
  --title "标题" --content "内容"

# 搜索文章
python3 /root/clawd/skills/article-collector/scripts/article-collector.py search "关键词"

# 列出所有文章
python3 /root/clawd/skills/article-collector/scripts/article-collector.py list
```