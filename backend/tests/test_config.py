from app.core.config import Settings


def test_settings_load_with_defaults_and_no_secrets():
    settings = Settings(_env_file=None)

    assert settings.APP_ENV == "development"
    assert settings.GROQ_API_KEY == ""
    assert settings.TOP_K == 5
    assert settings.SIMILARITY_THRESHOLD == 0.0
    assert settings.MAX_COMPLAINT_LENGTH == 5000


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("TOP_K", "8")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")

    settings = Settings(_env_file=None)

    assert settings.APP_ENV == "test"
    assert settings.TOP_K == 8
    assert settings.cors_origins_list == [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


def test_cors_origins_list_single_value():
    settings = Settings(_env_file=None, CORS_ORIGINS="http://localhost:3000")

    assert settings.cors_origins_list == ["http://localhost:3000"]
