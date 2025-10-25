#!/bin/bash

echo "🔄 重启 Reader 服务..."

# 提示用户当前操作
echo ""
echo "📌 操作步骤："
echo "1. 停止当前的前端和后端服务 (Ctrl+C)"
echo "2. 运行以下命令重启："
echo ""

# 前端重启命令
echo "# 前端 (新终端):"
echo "cd /data/ht/workspace/Reader_QAQ"
echo "npm run dev"
echo ""

# 后端重启命令
echo "# 后端 (新终端):"
echo "cd /data/ht/workspace/Reader_QAQ/src"
echo "python main.py"
echo ""

# 测试访问
echo "✅ 服务启动后访问："
echo "   前端: http://10.0.169.144:3004/knowledge"
echo "   后端: http://10.0.169.144:8000/docs"
echo ""

echo "🎉 优化内容："
echo "  ✓ 移除订阅的知识库部分"
echo "  ✓ 调大「我的知识库」字体"
echo "  ✓ 知识库可以重命名和删除"
echo "  ✓ 新用户注册时自动创建默认知识库"
echo "  ✓ 参考 Notes 页面的设计风格"
echo ""

