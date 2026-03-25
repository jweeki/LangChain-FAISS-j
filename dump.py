from common import create_embeddings, get_storage_paths, load_vector_store


def format_vector(values: list[float], precision: int = 6) -> str:
    formatted = ", ".join(f"{value:.{precision}f}" for value in values)
    return f"[{formatted}]"


def dump_vector_store() -> None:
    paths = get_storage_paths()
    print(f"本地向量模型目录: {paths['model_dir']}")
    print(f"向量库目录: {paths['vector_store_dir']}")
    print("正在加载模型和向量库，请稍候...")

    embeddings = create_embeddings()
    vector_store = load_vector_store(embeddings)

    index = vector_store.index
    docstore = vector_store.docstore
    mapping = vector_store.index_to_docstore_id

    print("模型和向量库加载完成。")
    print("\n向量库结构信息")
    print(f"索引类型: {type(index).__name__}")
    print(f"向量总数: {index.ntotal}")

    vector_dim = getattr(index, "d", None)
    if vector_dim is not None:
        print(f"向量维度: {vector_dim}")

    print(f"文档数量: {len(mapping)}")
    print(f"文档存储类型: {type(docstore).__name__}")

    print("\n向量库数据内容")
    for position, docstore_id in sorted(mapping.items()):
        document = docstore.search(docstore_id)
        vector = index.reconstruct(position)

        print("-" * 80)
        print(f"索引位置: {position}")
        print(f"Docstore ID: {docstore_id}")
        print(f"Metadata: {document.metadata}")
        print(f"文本内容: {document.page_content}")
        print(f"向量长度: {len(vector)}")
        print(f"向量数据: {format_vector(vector.tolist())}")


if __name__ == "__main__":
    dump_vector_store()
