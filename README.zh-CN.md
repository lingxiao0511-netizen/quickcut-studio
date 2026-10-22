# QuickCut Studio（快剪工作室）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://www.python.org/)

**把截图 + 一句话字幕，一键变成竖屏短视频。**

QuickCut Studio 是一个轻量 Python 命令行工具，专为抖音、快手、小红书、
视频号、TikTok、Reels、Shorts 上"截图讲解类"内容设计：你只需要写一个
YAML 配置文件——标题、图片列表、每张图一句字幕和时长——就能生成一条
可以直接发布的 **1080×1920、30fps、H.264 MP4**。

不用打开剪辑软件，不用拉时间线，不用手动排版。

## 为什么做这个

做截图类资讯/科普短视频的创作者，每条片子都在重复同样的排版劳动：
放截图、保证看得清、加标题、加字幕。QuickCut 把这套版式一次固定成模板：

- **三区模板**——上方标题区（全程常亮）、中间素材区、下方字幕条，三区永不重叠；
- **素材不裁切**——图片等比缩放完整放入素材区，从第 0 帧就出现，不会被标题或字幕挡住；
- **霓虹描边卡**——每张素材图自动加发光边框，在背景上清晰醒目；
- **程序化背景**——深色科技风渐变 + 缓慢呼吸的脉冲光环，全部由 Pillow 逐帧生成，
  不需要任何视频素材文件，一个配置文件就能完整复现一条片子。

## 快速开始

环境要求：Python ≥ 3.10，且 [ffmpeg](https://ffmpeg.org/) 已在 PATH 中。

```bash
pip install quickcut-studio   # 或在克隆的仓库里 pip install -e .
cd examples/demo
python make_samples.py        # 生成演示图片（全程本地生成，无需下载）
quickcut build config.yaml    # -> examples/demo/output.mp4
```

## 用法

```bash
quickcut build 配置文件.yaml [-o 输出.mp4] [--width W] [--height H] [--fps N]
```

最小配置示例：

```yaml
title:
  - "大标题"
  - "可选的第二行"
segments:
  - image: shots/公告截图.png
    caption: "一句话说清变化是什么"
    duration: 3.0
  - image: shots/数据图.png
    caption: "最关键的那个数字"
    duration: 4.0
output: out.mp4   # 可选；相对路径以配置文件所在目录为准
```

图片与输出路径都相对于配置文件所在目录解析；同样字段的 JSON 配置也可以。

## 配置说明

| 键 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `title` | 字符串或字符串列表 | —（必填） | 1–3 行，第一行字号最大 |
| `segments` | 列表 | —（必填） | 至少一个片段 |
| `segments[].image` | 路径 | —（必填） | PNG/JPG 等 Pillow 可读格式 |
| `segments[].caption` | 字符串 | `""` | 显示在底部字幕条 |
| `segments[].duration` | 秒 | `3.0` | 必须大于 0 |
| `output` | 路径 | `output.mp4` | |
| `width` / `height` | int | `1080` / `1920` | 可覆盖为其他画幅 |
| `fps` | int | `30` | |

## 工作原理

`quickcut/layout.py` 负责计算三区布局与素材的等比适配；`quickcut/render.py`
用 Pillow 逐帧绘制（背景、标题、素材卡、字幕条），再以原始帧流送入 ffmpeg
编码为 H.264。"三区不重叠、素材不出区"等布局不变量都有自动化测试覆盖。

## 开发

```bash
pip install -e ".[dev]"
pytest
```

## 路线图

- [ ] 更多背景主题（浅色、极简、自定义图片/视频背景）
- [ ] 可选配音轨混入（每片段一段预录音频）
- [ ] 素材图轻微推近（Ken Burns 效果）
- [ ] 批量模式：一次渲染多个配置
- [ ] 配置中自定义字体与主题色

## 许可证

MIT，见 [LICENSE](LICENSE)。English documentation: [README.md](README.md).
