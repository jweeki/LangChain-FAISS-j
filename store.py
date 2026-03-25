from common import (
    BASE_DIR,
    build_documents_from_excel,
    build_vector_store,
    create_embeddings,
    get_storage_paths,
    load_vector_store,
    save_vector_store,
)

# TODO: 存入数据可配置的参数(不存列名)
EXCEL_PATH = BASE_DIR / "L_Data.xlsx"
# 配置向量化的列（0 表示第一列）
SEARCH_COL = 0
# 写入模式：0 = 覆盖原有数据，1 = 追加数据
WRITE_MODE = 0

def run_store() -> None:
    paths = get_storage_paths()
    print(f"Excel 数据文件: {EXCEL_PATH}")
    print(f"本地向量模型目录: {paths['model_dir']}")
    print(f"向量库存储目录: {paths['vector_store_dir']}")
    print(f"写入模式: {'追加' if WRITE_MODE else '覆盖'}")

    embeddings = create_embeddings()
    documents = build_documents_from_excel(EXCEL_PATH, search_col=SEARCH_COL)

    if WRITE_MODE == 1 and paths['vector_store_dir'].exists():
        print("正在加载已有向量库并追加数据...")
        vector_store = load_vector_store(embeddings)
        vector_store.add_documents(documents)
    else:
        vector_store = build_vector_store(documents, embeddings)

    save_vector_store(vector_store)

if __name__ == "__main__":
    run_store()
