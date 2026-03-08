# Todo Manager Skill

## Description
Manage a categorized and tagged todo list in the `my-ai-memory` repository. Use this skill when the user mentions "待办" (todo) or "todo" to add new tasks, complete tasks, or search/filter tasks.

## Configuration
- **Repo Path**: `/root/clawd/codes/my-ai-memory`
- **File Path**: `memos/todo.md` (relative to repo root)

## File Format

The todo list is organized into categories with tagged tasks:

```
## 工作
- [ ] 任务内容 #标签1 #标签2 ：截止时间/备注
- [x] 已完成任务 #标签 ：完成时间

## 生活
- [ ] 任务内容 #标签 ：截止时间/备注
```

**Format rules:**
- Categories: `## 工作` (Work) and `## 生活` (Life)
- Tags: Start with `#`, can be multiple on one task
- Delimiter: Use `：` (full-width colon) to separate task content from time/notes
- Status: `- [ ]` for incomplete, `- [x]` for completed

## Usage

### 1. Analyze Intent
Determine if the user wants to **Add**, **Complete**, **List**, or **Search** tasks.

### 2. File Setup
1. Verify the repository exists at `/root/clawd/codes/my-ai-memory`.
2. Ensure the directory `memos` exists inside it.
3. Ensure `memos/todo.md` exists. If not, create it with category headers.

### 3. Handle Actions

#### A. Add Task
**Trigger**: User says "todo <content>" or "待办 <content>" (may include time, category, tags).

**Infer category:**
- Default: `工作` (Work) for professional tasks
- Use `生活` (Life) for personal/hobby tasks
- Check for explicit category mentions like "工作" or "生活"

**Infer tags** (optional but recommended):
- Extract hashtags from input: `#tag`
- Auto-tag based on keywords:
  - `#会议` (meeting) - 会议、开会、讨论
  - `#专利` (patent) - 专利、申请、IP
  - `#AI` - AI、模型、大模型、LLM
  - `#展会` (exhibition) - 展会、MWC、巴塞罗那
  - `#培训` (training) - 培训、学习、教程
  - `#开发` (dev) - 开发、代码、接口、API
  - `#部署` (deploy) - 部署、上线、配置
  - `#财务` (finance) - 费用、分摊、账单、付款

**Format**: Append to the appropriate category section:
`- [ ] <content> #tag1 #tag2 ：<time/notes>`

#### B. Complete Task
**Trigger**: User says "finish/complete <content>" or "完成 <content>".

**Action:**
1. Read `memos/todo.md`.
2. Find the line containing the `<content>` (partial match OK).
3. Replace `- [ ]` with `- [x]` at the start of that line.
4. Write the changes back to the file.

#### C. List Tasks
**Trigger**: User says "list todos", "待办列表", or similar.

**Action:**
1. Read `memos/todo.md`.
2. Display tasks organized by category.
3. Optional: Filter by completion status or category if specified.

**Display format:**
```
## 📋 待办列表

### 工作
- [ ] 任务1 #tag ：时间
- [x] 任务2 #tag ：完成

### 生活
- [ ] 任务3 #tag ：时间
```

#### D. Search/Filter Tasks
**Trigger**: User says "search todo <tag>", "待办搜索 <tag>", or "show work todos".

**Supported filters:**
- By category: `工作` / `生活`
- By tag: `#会议`, `#AI`, `#开发`, etc.
- By status: `未完成` / `已完成`
- Combined: `工作 未完成` (show incomplete work tasks)

**Action:**
1. Read `memos/todo.md`.
2. Filter tasks based on criteria.
3. Display matching tasks.

### 4. Git Sync (Mandatory)
After any modification:
1. Navigate to the repo: `cd /root/clawd/codes/my-ai-memory`
2. Stage the file: `git add memos/todo.md`
3. Commit: `git commit -m "Update todo list via Todo Manager Skill"`
4. Push: `git push`

### 5. Response
Reply to the user confirming the action:
- **Add**: Show the added task with category and tags
- **Complete**: Show the completed task
- **List/Search**: Display matching tasks in a clean format

**Example responses:**

Add:
```
✅ 已添加任务到 [工作]:
- [ ] 作业批改替换好未来新的接口 #开发 #好未来 ：最晚3月12日交付
```

Complete:
```
✅ 已完成任务:
- [x] 部署一个公用的openclaw给同事用 #部署
```

Search:
```
📋 搜索结果 [#会议]:
- [x] 确认去不去阿里北京会议 #会议 #阿里 ：2月27日
```

## Tag Guidelines

- **Be specific**: Use `#好未来` instead of just `#合作`
- **Use English tags for technical terms**: `#API`, `#LLM`, `#MWC`
- **Keep tags short**: 2-8 characters preferred
- **Use consistent tags**: Same concept should use same tag across tasks