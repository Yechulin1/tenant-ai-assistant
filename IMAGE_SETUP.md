# 如何添加握手图片

## 方法1: 直接保存图片（推荐）

1. 将握手图片保存到以下位置：
   ```
   /Users/linziqing/Downloads/DSS5105-feature-contract-assistant-update-3/assets/handshake.jpg
   ```

2. 刷新浏览器页面即可看到图片

## 方法2: 使用Python脚本

1. 将握手图片保存为项目根目录下的 `handshake_temp.jpg`

2. 运行脚本：
   ```bash
   python save_image.py
   ```

3. 刷新浏览器页面

## 图片要求

- 格式: JPG 或 PNG
- 建议尺寸: 600x400 像素或类似比例
- 文件大小: 建议小于 500KB

## 当前状态

如果没有提供图片，系统会显示一个优雅的渐变背景替代设计，包含：
- 🤝 握手图标
- 📄 文档图标
- 🏢 建筑物
- 🌳 树木装饰

这个设计与原图片的主题一致，提供良好的视觉效果。
