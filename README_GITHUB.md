# RentalPeace - AI Contract Assistant

## 📋 项目简介
RentalPeace 是一个基于 AI 的智能租赁合同助手，帮助租客和房东更好地理解和管理租赁合同。

## ✨ 主要功能
- 🏠 **角色选择**：租客 (Tenant) 或房东 (Landlord) 专属体验
- 📄 **PDF 上传**：支持租赁合同 PDF 文件上传
- 💬 **智能问答**：基于 OpenAI GPT 的合同问答系统
- 🔐 **用户管理**：完整的注册、登录、登出功能
- 🎨 **美观界面**：专业的渐变色设计（黄绿色调）

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件：
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. 运行应用
```bash
streamlit run frontend_rental_peace.py --server.port 8502
```

然后访问：http://localhost:8502

## 📁 项目结构
```
DSS5105-feature-contract-assistant-update-3/
├── frontend_rental_peace.py    # 主前端文件（推荐使用）
├── backend.py                   # 后端逻辑
├── langchain_rag_system.py      # RAG 系统
├── requirements.txt             # Python 依赖
├── user_data/                   # 用户数据目录
└── assets/                      # 静态资源
```

## 🎯 页面流程
1. **Marketing Page** - 产品介绍页面
2. **Role Selection** - 选择用户角色（租客/房东）
3. **Login** - 登录或注册
4. **Dashboard** - 上传合同并进行问答

## 👥 团队成员
- linziqing
- yechulin

## 🛠️ 技术栈
- **前端**: Streamlit
- **AI**: OpenAI GPT-3.5/GPT-4
- **向量数据库**: FAISS
- **PDF 处理**: pdfplumber, pymupdf, pypdf
- **数据库**: SQLite

## 📝 版本历史
- v1.0 - 初始版本（frontend_new.py）
- v2.0 - RentalPeace 品牌化设计（frontend_rental_peace.py）

## 📄 License
MIT License

---
Created with ❤️ by DSS5105 Team
