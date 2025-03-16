# 基于FastAPI和Vue的闲鱼二手商品数据爬取与简易可视化系统
## 后端(localhost:8000)
1、爬虫使用chrome浏览器，在https://googlechromelabs.github.io/chrome-for-testing/ 下载对应版本的驱动或者最新稳定版，并将chromedriver.exe复制到项目的chromedriver文件夹中。\
2、在终端（根目录）输入命令
```
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload # 如果在其他位置启动会导致检测不到backend模块
```
后端启动完成
## 前端(localhost:5000)
（如果5000端口被占用会递增至5001端口）\
1、在网上安装Node.js\
2、新开一个终端（根目录）输入命令
```
cd frontend
npm install
npm run dev
```
前端启动完成
