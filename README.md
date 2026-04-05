# common-english-words

一个本地可运行的英语单词卡网页，支持分类浏览、翻卡、发音、学习状态标记，以及基于本地 `SQLite` 数据库的持久化保存。

## 单词来源

本项目的 944 个单词来自知乎回答：

- 原始页面：https://www.zhihu.com/question/27584391/answer/2022984490109207601
- 回答内容说明：`Vocabineer 网站总结了 13 类日常最常用的 944 个单词`

项目中保存的结构化词表文件为：

- [data/words.json](C:/Users/yanwei/dev/projects/common-english-words/data/words.json)

说明：

- 回答导语写的是“13 类、944 个单词”
- 实际正文抽取结果为“944 个单词、14 个标题分类”
- 项目按正文实际内容进行展示，并在页面中保留了这个说明

## 项目结构

- [index.html](C:/Users/yanwei/dev/projects/common-english-words/index.html)：页面结构
- [styles.css](C:/Users/yanwei/dev/projects/common-english-words/styles.css)：页面样式
- [app.js](C:/Users/yanwei/dev/projects/common-english-words/app.js)：前端交互逻辑
- [server.py](C:/Users/yanwei/dev/projects/common-english-words/server.py)：本地后端服务，负责静态文件和 API
- [data/words.json](C:/Users/yanwei/dev/projects/common-english-words/data/words.json)：词表数据
- [data/progress.db](C:/Users/yanwei/dev/projects/common-english-words/data/progress.db)：学习进度数据库
- [scripts/extract_zhihu_words.py](C:/Users/yanwei/dev/projects/common-english-words/scripts/extract_zhihu_words.py)：从知乎 HTML 抽取词表的脚本
- [start.bat](C:/Users/yanwei/dev/projects/common-english-words/start.bat)：Windows 一键启动脚本

## 启动方式

### 方式一：双击启动

直接双击：

- [start.bat](C:/Users/yanwei/dev/projects/common-english-words/start.bat)

它会自动：

- 切换到项目目录
- 使用项目内 `.venv` 的 Python 启动后端
- 打开浏览器访问 `http://localhost:8000`

### 方式二：命令行启动

```powershell
cd C:\Users\yanwei\dev\projects\common-english-words
.\.venv\Scripts\python.exe .\server.py
```

启动后访问：

- http://localhost:8000

接口地址示例：

- http://localhost:8000/api/statuses

## 前后端说明

这个项目不是前后端分离部署，而是一个本地 Python 服务统一提供：

- 前端静态页面
- 单词数据文件
- 学习进度 API

也就是说，你只需要启动一个 `server.py`，前端和后端都会一起工作。

## 数据持久化

学习状态不会保存到浏览器 `localStorage`，而是保存到本地 `SQLite` 数据库：

- [data/progress.db](C:/Users/yanwei/dev/projects/common-english-words/data/progress.db)

当前保存的状态有三种：

- `known`
- `fuzzy`
- `unknown`

筛选支持：

- 全部
- 只看未学
- 只看熟词
- 只看模糊
- 只看不会

“未学”表示该单词还没有被标记过任何状态。

## 页面功能

- 按分类展示全部单词卡
- 点击卡片翻面后查看中文、词性、音标
- 调用有道词典 TTS 播放读音
- 对单词进行“熟词 / 模糊 / 不会”标记
- 顶部显示总数与各状态统计
- 支持按状态筛选
- 支持通过分类下拉快速跳转
- 同一台机器上可从数据库恢复上次学习进度

## 重新抽取词表

如果你后续重新抓到了知乎页面 HTML，可以再次生成词表：

```powershell
.\.venv\Scripts\python.exe .\scripts\extract_zhihu_words.py <输入HTML路径> .\data\words.json
```

例如：

```powershell
.\.venv\Scripts\python.exe .\scripts\extract_zhihu_words.py .\edge_profile_dump.html .\data\words.json
```
