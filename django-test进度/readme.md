
   # Polls 应用

   这是一个基于 Django 框架的投票应用，允许用户创建问题、添加选项并进行投票。

   ## 功能概述

   ### 1. 首页 (`index`)
   - **功能**: 显示所有问题列表，按发布时间倒序排列。
   - **URL**: `/polls/`
   - **视图函数**: `index`
   - **权限**: 需要用户登录。

   ### 2. 创建问题 (`create_question`)
   - **功能**: 允许用户创建一个新的投票问题。
   - **URL**: `/polls/create_question/`
   - **视图函数**: `create_question`
   - **权限**: 需要用户登录。
   - **逻辑**:
     - 如果是 `POST` 请求：
       1. 使用 `QuestionForm` 表单验证用户输入。
       2. 如果表单有效：
          - 保存问题，但不立即提交到数据库（`commit=False`）。
          - 将当前登录用户设置为问题的作者。
          - 保存问题到数据库。
          - 打印调试信息（新问题的 ID）。
          - 重定向到添加选项页面，传递新问题的 ID。
     - 如果是 `GET` 请求：
       - 渲染空的 `QuestionForm` 表单。

   ### 3. 添加选项 (`add_choices`)
   - **功能**: 允许用户为问题添加选项。
   - **URL**: `/polls/<question_id>/add_choices/`
   - **视图函数**: `add_choices`（未提供完整代码，但可以推测其功能）。
   - **权限**: 需要用户登录。

   ## 文件结构

   ### 主要文件
   - **`views.py`**: 包含应用的视图逻辑。
   - **`models.py`**: 定义了 `Question`、`Choice` 和 `Vote` 模型。
   - **`forms.py`**: 定义了 `QuestionForm` 和 `ChoiceForm` 表单，用于处理用户输入。

   ### 模型
   - **`Question`**: 表示一个投票问题。
   - **`Choice`**: 表示一个问题的选项。
   - **`Vote`**: 表示用户对某个选项的投票。

   ## 安装与运行

   ### 环境要求
   - Python 3.x
   - Django 4.x
   - 一个虚拟环境（推荐）

   ### 安装步骤
   1. 克隆项目到本地：
      ```bash
      git clone <repository-url>
      cd <project-directory>
      ```
   
   2. 创建虚拟环境并激活：
      ```bash
      python -m venv .venv
      .venv\Scripts\activate  # Windows
      ```
   
   3. 安装依赖：
      ```bash
      pip install -r requirements.txt
      ```
   
   4. 运行数据库迁移：
      ```bash
      python manage.py migrate
      ```
   
   5. 启动开发服务器：
      ```bash
      python manage.py runserver
      ```
   
   6. 打开浏览器访问：
      ```
      http://127.0.0.1:8000/polls/
      ```

   ## 注意事项
   - 所有视图均需要用户登录，未登录用户会被重定向到登录页面。
   - 在创建问题后，用户需要为问题添加选项，才能进行投票。

   ## 调试信息
   - 在 `create_question` 视图中，使用了 `print` 语句输出新问题的 ID，便于调试：
     ```python
     print(f">>>>>>新问题ID: {question.id}")
     ```

   ## 未来改进
   - 添加投票功能的实现。
   - 提供问题和选项的编辑功能。
   - 增加单元测试，确保代码的稳定性。