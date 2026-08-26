from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)


# ============================================================
# Milvus 配置
# ============================================================

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

COLLECTION_NAME = "hacker_news"

VECTOR_DIM = 1024


class MilvusManager:
    """
    Milvus 向量数据库管理器
    """

    def __init__(
        self,
        host: str = MILVUS_HOST,
        port: str = MILVUS_PORT,
    ):

        self.host = host
        self.port = port

        print("=" * 60)
        print("正在连接 Milvus...")
        print(f"地址：{host}:{port}")
        print("=" * 60)

        connections.connect(
            alias="default",
            host=self.host,
            port=self.port,
        )

        print("Milvus 连接成功！")
        print()

        self.collection = self._get_or_create_collection()

    # ========================================================
    # todo 创建 Collection
    # ========================================================

    def _get_or_create_collection(self):

        # 如果已经存在
        if utility.has_collection(COLLECTION_NAME):

            print(
                f"发现已有 Collection："
                f"{COLLECTION_NAME}"
            )

            collection = Collection(
                COLLECTION_NAME
            )

            collection.load()

            return collection

        print(
            f"创建 Collection："
            f"{COLLECTION_NAME}"
        )

        # ----------------------------------------------------
        # 主键
        # ----------------------------------------------------

        id_field = FieldSchema(
            name="id",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=True,
        )

        # ----------------------------------------------------
        # Hacker News ID
        # ----------------------------------------------------

        source_id_field = FieldSchema(
            name="source_id",
            dtype=DataType.INT64,
        )

        # ----------------------------------------------------
        # 标题
        # ----------------------------------------------------

        title_field = FieldSchema(
            name="title",
            dtype=DataType.VARCHAR,
            max_length=1024,
        )

        # ----------------------------------------------------
        # 来源
        # ----------------------------------------------------

        source_field = FieldSchema(
            name="source",
            dtype=DataType.VARCHAR,
            max_length=128,
        )

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        url_field = FieldSchema(
            name="url",
            dtype=DataType.VARCHAR,
            max_length=2048,
        )

        # ----------------------------------------------------
        # Chunk 内容
        # ----------------------------------------------------

        content_field = FieldSchema(
            name="content",
            dtype=DataType.VARCHAR,
            max_length=65535,
        )

        # ----------------------------------------------------
        # Chunk 编号
        # ----------------------------------------------------

        chunk_index_field = FieldSchema(
            name="chunk_index",
            dtype=DataType.INT64,
        )

        # ----------------------------------------------------
        # 向量
        # ----------------------------------------------------

        vector_field = FieldSchema(
            name="embedding",
            dtype=DataType.FLOAT_VECTOR,
            dim=VECTOR_DIM,
        )

        # ----------------------------------------------------
        # Schema
        # ----------------------------------------------------

        schema = CollectionSchema(
            fields=[
                id_field,
                source_id_field,
                title_field,
                source_field,
                url_field,
                content_field,
                chunk_index_field,
                vector_field,
            ],
            description="Hacker News RAG Knowledge Base",
        )

        collection = Collection(
            name=COLLECTION_NAME,
            schema=schema,
        )

        # ====================================================
        # todo 创建向量索引
        # ====================================================

        print("正在创建向量索引...")

        index_params = {
            "index_type": "AUTOINDEX",
            "metric_type": "COSINE",
            "params": {},
        }

        collection.create_index(
            field_name="embedding",
            index_params=index_params,
        )

        collection.load()

        print("Collection 创建完成！")
        print()

        return collection

    # ========================================================
    # todo 插入数据
    # ========================================================

    def insert(
        self,
        chunks: list[dict],
    ) -> int:

        if not chunks:
            print("没有数据需要写入 Milvus")
            return 0

        source_ids = []
        titles = []
        sources = []
        urls = []
        contents = []
        chunk_indexes = []
        embeddings = []

        for chunk in chunks:

            source_ids.append(
                int(chunk.get("source_id", 0))
            )

            titles.append(
                chunk.get("title", "")
            )

            sources.append(
                chunk.get("source", "")
            )

            urls.append(
                chunk.get("url", "")
            )

            contents.append(
                chunk.get("content", "")
            )

            chunk_indexes.append(
                int(chunk.get("chunk_index", 0))
            )

            embeddings.append(
                chunk["embedding"]
            )

        data = [
            source_ids,
            titles,
            sources,
            urls,
            contents,
            chunk_indexes,
            embeddings,
        ]

        result = self.collection.insert(data)

        self.collection.flush()

        print()
        print("=" * 60)
        print("Milvus 数据写入完成")
        print(f"写入 Chunk：{len(chunks)}")
        print(f"Collection：{COLLECTION_NAME}")
        print("=" * 60)

        return len(result.primary_keys)

    # ========================================================
    # todo 查询
    # ========================================================

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[dict]:

        self.collection.load()

        results = self.collection.search(
            data=[query_vector],
            anns_field="embedding",
            param={
                "metric_type": "COSINE",
                "params": {},
            },
            limit=limit,
            output_fields=[
                "source_id",
                "title",
                "source",
                "url",
                "content",
                "chunk_index",
            ],
        )

        documents = []

        for hits in results:

            for hit in hits:

                documents.append({
                    "id": hit.id,
                    "score": hit.distance,
                    "source_id": hit.entity.get(
                        "source_id"
                    ),
                    "title": hit.entity.get(
                        "title"
                    ),
                    "source": hit.entity.get(
                        "source"
                    ),
                    "url": hit.entity.get(
                        "url"
                    ),
                    "content": hit.entity.get(
                        "content"
                    ),
                    "chunk_index": hit.entity.get(
                        "chunk_index"
                    ),
                })

        return documents


# ============================================================
# todo 获取 Milvus 管理器
# ============================================================

_milvus_manager = None


def get_milvus_manager() -> MilvusManager:

    global _milvus_manager

    if _milvus_manager is None:

        _milvus_manager = MilvusManager()

    return _milvus_manager


def save_to_milvus(
    chunks: list[dict],
) -> int:

    manager = get_milvus_manager()

    return manager.insert(chunks)