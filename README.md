# LangChain 轻量化本地向量库检索实验

FAISS + HuggingFace 中文嵌入模型，将 Excel 数据向量化存储(LangChain-faiss向量库)并支持语义检索。

## 项目结构

```
LangChain/
├── common.py          # 公共模块（模型加载、Excel读取、向量库操作）
├── store.py           # 数据存入脚本（Excel → 向量库）
├── search.py          # 语义检索脚本（交互式查询）
├── requirements.txt   # Python 依赖
├── L_Data.xlsx        # Excel 数据文件
├── models/            # 本地嵌入模型目录
│   └── text2vec-base-chinese/
└── faiss_store/       # FAISS 向量库存储目录
```

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载中文嵌入模型

从 [Hugging Face](https://huggingface.co/shibing624/text2vec-base-chinese) 下载模型文件，放入 `models/text2vec-base-chinese/` 目录。

必需文件：`model.safetensors`、`config.json`、`tokenizer_config.json`、`vocab.txt` 等。

## Excel 数据格式

- **第一行为列名**（不会被存入向量库）
- 支持多列数据，自动过滤全空列
- 通过 `SEARCH_COL` 参数指定哪一列用于向量化检索，其余列存入元数据

示例：

| 词条 | 解释 |
|------|------|
| 篮球 | 团队运动，以投篮得分 |
| 游泳 | 水中运动技能 |

## 使用方式

### 存入数据

```bash
python store.py
```

`store.py` 可配置参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `EXCEL_PATH` | Excel 数据文件路径 | `L_Data.xlsx` |
| `SEARCH_COL` | 向量化的列索引（0 = 第一列） | `0` |
| `WRITE_MODE` | 写入模式（0 = 覆盖，1 = 追加） | `0` |

### 语义检索

```bash
python search.py
```

`search.py` 可配置参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `TOP_K` | 返回结果条数 | `5` |

运行后进入交互模式，输入查询文本返回语义最相似的结果，输入 `exit` 退出。

输出示例：

```
查询内容: 运动
共返回 5 条结果:
  [1] 置信度: 0.8523146210 | 篮球
       附加列: {'解释': '团队运动，以投篮得分'}
       来源标记: doc_1
```

## 公共配置（common.py）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `MODEL_NAME` | 嵌入模型名称 | `shibing624/text2vec-base-chinese` |
| `MODEL_DIR` | 本地模型存储路径 | `models/text2vec-base-chinese` |
| `VECTOR_STORE_DIR` | 向量库存储路径 | `faiss_store/` |

支持 CUDA 加速，自动检测 GPU 可用性。

## 测试结果run_(search.py)

查询内容: 我饿了

![image-20260325113712791](C:\Users\25933\AppData\Roaming\Typora\typora-user-images\image-20260325113712791.png)

查询内容:什么是工程师

![image-20260325113951304](C:\Users\25933\AppData\Roaming\Typora\typora-user-images\image-20260325113951304.png)

## 作者

**Jwekki**

## 免责声明

本项目仅供学习和研究用途，不提供任何明示或暗示的保证。作者不对因使用本项目而产生的任何直接或间接损失承担责任。

- 本项目所使用的第三方模型和库（HuggingFace、FAISS、LangChain 等）的版权归各自所有者所有
- 请勿将本项目用于任何违反法律法规的用途
