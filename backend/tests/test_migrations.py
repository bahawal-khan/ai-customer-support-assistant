import sqlalchemy as sa

EXPECTED_TABLES = {
    "documents",
    "document_chunks",
    "complaints",
    "analyses",
    "retrieved_sources",
    "generated_responses",
}


def test_migration_creates_all_tables(test_engine):
    inspector = sa.inspect(test_engine)
    assert EXPECTED_TABLES.issubset(set(inspector.get_table_names()))


def test_vector_extension_enabled(test_engine):
    with test_engine.connect() as conn:
        result = conn.execute(
            sa.text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        ).scalar()
    assert result == "vector"


def test_foreign_keys_present(test_engine):
    inspector = sa.inspect(test_engine)

    chunk_fks = inspector.get_foreign_keys("document_chunks")
    assert any(fk["referred_table"] == "documents" for fk in chunk_fks)

    analysis_fks = inspector.get_foreign_keys("analyses")
    assert any(fk["referred_table"] == "complaints" for fk in analysis_fks)

    retrieved_source_fks = inspector.get_foreign_keys("retrieved_sources")
    referred_tables = {fk["referred_table"] for fk in retrieved_source_fks}
    assert referred_tables == {"analyses", "document_chunks"}

    generated_response_fks = inspector.get_foreign_keys("generated_responses")
    assert any(fk["referred_table"] == "analyses" for fk in generated_response_fks)


def test_analyses_complaint_id_is_unique(test_engine):
    inspector = sa.inspect(test_engine)
    unique_constraints = inspector.get_unique_constraints("analyses")
    indexes = inspector.get_indexes("analyses")
    columns_marked_unique = {
        column
        for constraint in unique_constraints
        for column in constraint["column_names"]
    } | {
        column
        for index in indexes
        if index.get("unique")
        for column in index["column_names"]
    }
    assert "complaint_id" in columns_marked_unique
