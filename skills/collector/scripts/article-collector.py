#!/usr/bin/env python3
"""
Article Collector Script

This script helps collect and organize articles/files into markdown format.
Usage:
    python3 article-collector.py collect --title <title> --content <content>
    python3 article-collector.py search <query>
    python3 article-collector.py list
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
import argparse

# Configuration
COLLECT_ROOT = "/root/clawd/codes/my-ai-memory/collect"
DATE_FORMAT = "%Y-%m-%d"


def sanitize_filename(text):
    """Convert text to safe filename (English/ASCII only)."""
    # Remove or replace non-ASCII characters
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    # Strip leading/trailing hyphens and spaces
    text = text.strip('- ')
    # Limit length
    return text[:100]


def extract_tags(content):
    """Extract 3-5 keywords/tags from content."""
    # Simple keyword extraction
    words = re.findall(r'\b\w{3,}\b', content.lower())
    
    # Common words to filter (incomplete set, can be expanded)
    common_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'with', 'this', 'that', 'from',
        'they', 'have', 'been', 'more', 'will', 'would', 'there', 'what',
        'about', 'which', 'their', 'when', 'could', 'than', 'into', 'your',
        'some', 'just', 'like', 'also', 'very', 'only', 'most', 'such',
        'other', 'over', 'even', 'make', 'much', 'because', 'these', 'first',
        'being', 'after', 'where', 'those', 'should', 'does', 'were', 'before',
        'through', 'while', 'between', 'under', 'again', 'still', 'every',
        'might', '应该', '可以', '这个', '那个', '就是', '都是', '这里', '那里',
        '什么', '怎么', '这样', '那样', '因为', '所以', '但是', '如果', '或者',
        '虽然', '而且', '不过', '已经', '正在', '将要', '能够', '需要', '想要',
        '喜欢', '认为', '觉得', '知道', '发现', '看到', '听到', '收到', '使用',
        '进行', '实现', '完成', '开始', '结束', '停止', '继续', '保持', '发展',
        '增加', '减少', '提高', '降低', '改善', '优化', '设计', '制作', '创建',
        '建立', '删除', '修改', '更新', '保存', '读取', '写入', '处理', '分析',
        '研究', '学习', '工作', '生活', '时间', '问题', '方法', '方式', '结果',
        '效果', '影响', '作用', '意义', '价值', '内容', '信息', '数据', '技术',
        '系统', '平台', '服务', '产品', '市场', '用户', '客户', '公司', '企业',
        '团队', '项目', '计划', '目标', '需求', '要求', '标准', '规范', '流程'
    }
    
    # Get top 5 most frequent words
    word_counts = {}
    for word in words:
        if word not in common_words and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and get top 5
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [word for word, count in sorted_words]


def extract_summary(content):
    """Extract summary from first 1-2 sentences (50-100 chars)."""
    # Remove newlines and extra spaces
    content = re.sub(r'\s+', ' ', content.strip())
    # Split by sentence endings
    sentences = re.split(r'[.!?。！？\n]', content)
    
    summary = ""
    for sent in sentences[:2]:  # First 2 sentences
        if len(sent) > 5:  # Skip very short sentences
            summary += sent + "。"
            if len(summary) >= 50:
                break
    
    return summary.strip()[:100]


def collect_article(title, content, source_type="manual"):
    """
    Collect an article into markdown format.

    Args:
        title: Article title
        content: Article content
        source_type: "url" or "file" or "manual"
    """
    # Create date string
    date_str = datetime.now().strftime(DATE_FORMAT)
    
    # Extract metadata
    tags = extract_tags(content)
    tags_str = ", ".join(tags)
    summary = extract_summary(content)
    
    # Create markdown content
    markdown_content = f"""标题：{title}
创建日期：{date_str}
标签：{tags_str}
摘要：{summary}
---
{content}"""
    
    # Determine filename
    filename = sanitize_filename(title) + ".md"
    
    # Create directory structure
    date_dir = os.path.join(COLLECT_ROOT, date_str)
    os.makedirs(date_dir, exist_ok=True)
    
    # Write file
    filepath = os.path.join(date_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ 文章已保存: {filepath}")
    print(f"   标题: {title}")
    print(f"   标签: {tags_str}")
    print(f"   日期: {date_str}")
    
    return filepath


def search_articles(query):
    """
    Search articles by query.

    Args:
        query: Search query (tag, title, or keyword)
    """
    results = []
    collect_path = Path(COLLECT_ROOT)
    
    if not collect_path.exists():
        print("❌ 收藏目录不存在")
        return results
    
    # Search through all markdown files
    for md_file in collect_path.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse metadata
            metadata = {}
            body_start = content.find('---')
            if body_start != -1:
                metadata_section = content[:body_start]
                body = content[body_start+3:]
                
                for line in metadata_section.strip().split('\n'):
                    if '：' in line:
                        key, value = line.split('：', 1)
                        metadata[key.strip()] = value.strip()
            else:
                body = content
            
            # Check if query matches
            query_lower = query.lower()
            match = False
            match_reason = []
            
            if query_lower in metadata.get('标题', '').lower():
                match = True
                match_reason.append("标题")
            
            if query_lower in metadata.get('标签', '').lower():
                match = True
                match_reason.append("标签")
            
            if query_lower in metadata.get('摘要', '').lower():
                match = True
                match_reason.append("摘要")
            
            if query_lower in body.lower():
                match = True
                match_reason.append("内容")
            
            if match:
                results.append({
                    'file': str(md_file),
                    'title': metadata.get('标题', md_file.stem),
                    'date': metadata.get('创建日期', ''),
                    'tags': metadata.get('标签', ''),
                    'summary': metadata.get('摘要', ''),
                    'reason': match_reason
                })
        except Exception as e:
            print(f"⚠️  读取文件失败 {md_file}: {e}")
    
    return results


def list_all_articles():
    """List all collected articles."""
    results = []
    collect_path = Path(COLLECT_ROOT)
    
    if not collect_path.exists():
        print("❌ 收藏目录不存在")
        return results
    
    for md_file in collect_path.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {}
            body_start = content.find('---')
            if body_start != -1:
                metadata_section = content[:body_start]
                for line in metadata_section.strip().split('\n'):
                    if '：' in line:
                        key, value = line.split('：', 1)
                        metadata[key.strip()] = value.strip()
            
            results.append({
                'file': str(md_file),
                'title': metadata.get('标题', md_file.stem),
                'date': metadata.get('创建日期', ''),
                'tags': metadata.get('标签', ''),
                'summary': metadata.get('摘要', '')
            })
        except Exception as e:
            print(f"⚠️  读取文件失败 {md_file}: {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Article Collector')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect an article')
    collect_parser.add_argument('--title', required=True, help='Article title')
    collect_parser.add_argument('--content', required=True, help='Article content')
    collect_parser.add_argument('--type', choices=['url', 'file', 'manual'], default='manual', help='Source type')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search articles')
    search_parser.add_argument('query', help='Search query')
    
    # List command
    subparsers.add_parser('list', help='List all articles')
    
    args = parser.parse_args()
    
    if args.command == 'collect':
        collect_article(args.title, args.content, args.type)
    elif args.command == 'search':
        results = search_articles(args.query)
        if results:
            print(f"\n📚 找到 {len(results)} 篇文章:\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. [{r['date']}] {r['title']}")
                print(f"   文件: {r['file']}")
                print(f"   标签: {r['tags']}")
                print(f"   匹配: {', '.join(r['reason'])}\n")
        else:
            print(f"❌ 未找到与 '{args.query}' 相关的文章")
    elif args.command == 'list':
        results = list_all_articles()
        if results:
            print(f"\n📚 所有收藏文章 ({len(results)} 篇):\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. [{r['date']}] {r['title']}")
                print(f"   标签: {r['tags']}\n")
        else:
            print("❌ 暂无收藏文章")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()