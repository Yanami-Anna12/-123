from sentence_transformers import SentenceTransformer


# ============================================================
# Embedding 模型配置
# ============================================================

MODEL_NAME = "BAAI/bge-m3"


class EmbeddingModel:
    """
    文本 Embedding 模型
    """

    def __init__(self):
        print("=" * 60)
        print("正在加载 Embedding 模型...")
        print(f"模型：{MODEL_NAME}")
        print("=" * 60)

        self.model = SentenceTransformer(MODEL_NAME)

        print("Embedding 模型加载完成！")
        print()

    def encode(self, texts: list[str]) -> list[list[float]]:
        """
        将多个文本转换成向量
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()


# 全局模型
_embedding_model = None


def get_embedding_model() -> EmbeddingModel:
    """
    获取 Embedding 模型
    """

    global _embedding_model

    if _embedding_model is None:
        _embedding_model = EmbeddingModel()

    return _embedding_model


def embed_chunks(
    chunks: list[dict],
) -> list[dict]:
    """
    对文本 Chunk 进行 Embedding

    输入：
        [
            {
                "source_id": 123,
                "title": "...",
                "content": "..."
            }
        ]

    输出：
        在原数据基础上增加 embedding 字段
    """

    if not chunks:
        return []

    model = get_embedding_model()

    texts = [
        chunk.get("content", "")
        for chunk in chunks
    ]

    embeddings = model.encode(texts)

    result = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
    ):

        item = chunk.copy()

        item["embedding"] = embedding

        result.append(item)

    print()
    print("=" * 60)
    print("Embedding 完成")
    print(f"Chunk 数量：{len(result)}")
    print(f"向量维度：{len(result[0]['embedding'])}")
    print("=" * 60)

    return result