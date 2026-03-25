from common import (
    create_embeddings,
    get_storage_paths,
    load_vector_store,
    search_documents,
)

# TODO: 修改为可配置的参数
TOP_K = 5


def run_search_loop(k: int = TOP_K) -> None:
    paths = get_storage_paths()
    print(f"本地向量模型目录: {paths['model_dir']}")
    print(f"向量库读取目录: {paths['vector_store_dir']}")
    print("模型和向量库加载中，请稍候...")

    embeddings = create_embeddings()
    vector_store = load_vector_store(embeddings)

    print("* 所有加载已完成。")

    while True:
        query = input("\n请输入查询内容: ").strip()
        if query.lower() == "exit":
            print("检索已结束。")
            break
        if not query:
            print("输入不能为空，请重新输入。")
            continue

        results = search_documents(vector_store, query, k=k)

        print(f"查询内容: {query}")
        if results:
            print(f"共返回 {len(results)} 条结果:")
            for i, (doc, score) in enumerate(results, 1):
                confidence = 1 / (1 + score)
                print(f"  [{i}] 置信度: {confidence:.10f} | {doc.page_content}")
                extra = {k: v for k, v in doc.metadata.items() if k != "source"}
                if extra:
                    print(f"       附加列: {extra}")
                print(f"       来源标记: {doc.metadata.get('source')}")
        else:
            print("没有检索到匹配内容")


if __name__ == "__main__":
    run_search_loop()
