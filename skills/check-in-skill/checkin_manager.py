#!/usr/bin/env python3
"""
Checkin Manager - 打卡管理工具
管理每周打卡记录（健身、吉他、维生素）
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
REPO_PATH = "/root/clawd/codes/my-ai-memory"
CHECKIN_FILE = f"{REPO_PATH}/memos/checkin.md"
DISCORD_TARGET = "1470416039685656762"

# Weekly goals
GOALS = {
    "健身": 3,
    "吉他": 5,
    "维生素": 5,
    "博客": 4
}

# Item keywords mapping
ITEM_KEYWORDS = {
    "健身": ["健身", "锻炼", "练背", "练胸", "跑步", "举重", "训练", "workout", "gym"],
    "吉他": ["吉他", "练吉他", "弹吉他", "guitar"],
    "维生素": ["维生素", "吃药", "补充剂", "vitamin", "pills"],
    "博客": ["博客", "文章", "写文章", "发文", "blog", "post", "writing"]
}


def get_week_info(date_str=None):
    """获取 ISO 周信息（周一是第一天）"""
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        dt = datetime.now()

    # ISO 周数（周一为第一天）
    year, week, _ = dt.isocalendar()

    # 计算周一和周日的日期
    monday = dt - timedelta(days=dt.weekday())
    sunday = monday + timedelta(days=6)

    week_id = f"{year}-W{week:02d}"
    date_range = f"{monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}"

    return {
        "year": year,
        "week": week,
        "week_id": week_id,
        "monday": monday.strftime('%Y-%m-%d'),
        "sunday": sunday.strftime('%Y-%m-%d'),
        "date_range": date_range,
        "day_of_week": dt.weekday()  # 0=周一, 6=周日
    }


def parse_checkin_file():
    """读取打卡记录文件"""
    if not os.path.exists(CHECKIN_FILE):
        return ""

    with open(CHECKIN_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def write_checkin_file(content):
    """写入打卡记录文件"""
    os.makedirs(os.path.dirname(CHECKIN_FILE), exist_ok=True)
    with open(CHECKIN_FILE, 'w', encoding='utf-8') as f:
        f.write(content)


def get_week_entries(content, week_info):
    """获取指定周的打卡记录"""
    pattern = rf"## {week_info['week_id']} \({week_info['date_range']}\)\n(.*?)(?=\n## |$)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        return match.group(1).strip()
    return None


def parse_week_entries(entries_text):
    """解析一周的打卡记录"""
    completed = {item: [] for item in GOALS}

    for line in entries_text.split('\n'):
        line = line.strip()
        if not line.startswith('- [x]'):
            continue

        # 解析格式：- [x] 健身 2026-02-25 21:00
        match = re.match(r'- \[x\] (\S+)\s+(\S+)\s+(\S+)', line)
        if match:
            item = match.group(1)
            date = match.group(2)
            time = match.group(3)

            if item in completed:
                completed[item].append({
                    'date': date,
                    'time': time
                })

    return completed


def add_checkin(item):
    """添加打卡记录"""
    content = parse_checkin_file()
    week_info = get_week_info()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 检查或创建周记录
    week_header = f"## {week_info['week_id']} ({week_info['date_range']})"

    if week_header not in content:
        # 创建新的周记录
        content += f"\n{week_header}\n"
    else:
        # 确保周记录后有换行
        if not content.endswith('\n'):
            content += '\n'

    # 添加打卡记录
    checkin_line = f"- [x] {item} {timestamp}\n"

    # 找到周记录的位置，插入打卡记录
    pattern = rf"(## {re.escape(week_header)})\n"
    match = re.search(pattern, content)

    if match:
        # 在周标题后添加
        insert_pos = match.end()
        content = content[:insert_pos] + checkin_line + content[insert_pos:]
    else:
        # 追加到文件末尾
        content += checkin_line

    write_checkin_file(content)
    return week_info


def get_week_stats(week_info=None):
    """获取本周统计"""
    if week_info is None:
        week_info = get_week_info()

    content = parse_checkin_file()
    entries_text = get_week_entries(content, week_info)

    if entries_text is None:
        # 本周还没有记录
        completed = {item: [] for item in GOALS}
    else:
        completed = parse_week_entries(entries_text)

    stats = {}
    for item in GOALS:
        count = len(completed[item])
        goal = GOALS[item]
        remaining = max(0, goal - count)
        progress = min(100, int(count / goal * 100)) if goal > 0 else 100

        stats[item] = {
            "count": count,
            "goal": goal,
            "remaining": remaining,
            "progress": progress,
            "completed": completed[item]
        }

    return stats


def identify_item(text):
    """识别用户要打卡的项目"""
    text_lower = text.lower()

    for item, keywords in ITEM_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return item

    return None


def generate_daily_reminder(stats, week_info):
    """生成每日提醒消息"""
    is_weekend = week_info['day_of_week'] >= 5  # 周六=5, 周日=6

    lines = [
        f"📊 **本周打卡进度** ({week_info['week_id']})"
    ]

    total_items = len(stats)
    critical_count = 0  # 快到周末且剩余次数>50%
    good_count = 0

    for item, stat in stats.items():
        emoji = "✅" if stat['remaining'] == 0 else "⏳"

        # 判断是否严重
        if is_weekend and stat['remaining'] > stat['goal'] * 0.5:
            emoji = "❌" if stat['remaining'] >= stat['goal'] * 0.8 else "⚠️"
            critical_count += 1
        elif stat['progress'] >= 50:
            emoji = "✅"
            good_count += 1

        status = f"{stat['count']}/{stat['goal']}"
        lines.append(f"- {item}：{status} {emoji}")

    # 添加反馈
    if critical_count > 0:
        lines.append("\n⚠️ 警告！今天是周末，你还剩很多任务没完成！")
        lines.append("别再拖了，抓紧时间！🔥")
    elif good_count == total_items:
        lines.append("\n表现不错！继续保持！💪🎉")
    elif stats["健身"]["progress"] >= 50 and stats["吉他"]["progress"] >= 50:
        lines.append("\n进度还可以，继续加油！💪")
    else:
        lines.append("\n加油！不要放弃！🌟")

    return "\n".join(lines)


def generate_weekly_summary(week_info, stats):
    """生成周总结消息"""
    lines = [
        f"📋 **上周打卡总结** ({week_info['week_id']})"
    ]

    all_done = True
    total_progress = 0

    for item, stat in stats.items():
        if stat['remaining'] > 0:
            all_done = False
            emoji = "❌" if stat['remaining'] > stat['goal'] * 0.5 else "⚠️"
        else:
            emoji = "✅"

        status = f"{stat['count']}/{stat['goal']}"
        lines.append(f"- {item}：{status} {emoji}")
        total_progress += stat['progress']

    avg_progress = int(total_progress / len(stats))

    if all_done:
        lines.append("\n🎉 完美！所有项目都达标了！继续保持！")
    elif avg_progress >= 90:
        lines.append(f"\n👏 很棒！总体完成率 {avg_progress}%，表现优秀！")
    elif avg_progress >= 70:
        lines.append(f"\n不错！总体完成率 {avg_progress}%，继续努力！")
    else:
        lines.append(f"\n⚠️ 完成率 {avg_progress}%，下周要加油！")

    return "\n".join(lines)


def checkin_command(user_text):
    """处理打卡命令"""
    item = identify_item(user_text)

    if item is None:
        return None

    week_info = add_checkin(item)
    stats = get_week_stats(week_info)

    # 鼓励语
    encouragements = {
        "健身": [
            "练得好！每一滴汗水都不会白费！💪🔥",
            "坚持健身，身体会感谢你的！🏋️‍♂️",
            "今天又变强了一点！继续加油！✨"
        ],
        "吉他": [
            "练琴很棒！音乐点亮生活！🎸🎵",
            "今天的练习会让手指更灵活！✨",
            "保持热爱，琴技日日精进！🌟"
        ],
        "维生素": [
            "按时补充，保持健康！💊✨",
            "好习惯，身体是革命的本钱！💪",
            "坚持摄入，活力满满每一天！🌟"
        ],
        "博客": [
            "写得好！坚持输出，积累影响力！✍️✨",
            "每次写作都是一次成长！📚",
            "保持思考，用文字分享价值！🌟"
        ]
    }

    import random
    encouragement = random.choice(encouragements.get(item, ["继续加油！💪"]))

    lines = [f"✅ 已记录：{item} {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    lines.append(f"\n{encouragement}\n")
    lines.append("本周进度：")

    for item_name, stat in stats.items():
        emoji = "✅" if stat['remaining'] == 0 else "⏳"
        lines.append(f"- {item_name}：{stat['count']}/{stat['goal']} 次 {emoji}")

    return "\n".join(lines)


def daily_reminder_command():
    """处理每日提醒命令"""
    week_info = get_week_info()
    stats = get_week_stats(week_info)
    return generate_daily_reminder(stats, week_info)


def weekly_summary_command():
    """处理周总结命令（上周）"""
    # 上周
    last_week_date = datetime.now() - timedelta(weeks=1)
    week_info = get_week_info(last_week_date.strftime('%Y-%m-%d'))
    stats = get_week_stats(week_info)
    return generate_weekly_summary(week_info, stats)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: checkin_manager.py <command> [args]")
        print("Commands: checkin <text>, daily-reminder, weekly-summary")
        sys.exit(1)

    command = sys.argv[1]

    if command == "checkin" and len(sys.argv) >= 3:
        user_text = " ".join(sys.argv[2:])
        result = checkin_command(user_text)
        print(result)
    elif command == "daily-reminder":
        result = daily_reminder_command()
        print(result)
    elif command == "weekly-summary":
        result = weekly_summary_command()
        print(result)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)