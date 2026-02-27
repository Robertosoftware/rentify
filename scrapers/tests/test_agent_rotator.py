from scrapers.src.anti_detection.agent_rotator import AgentRotator
from scrapers.src.anti_detection.user_agents import USER_AGENTS


def test_agent_rotator_returns_headers():
    rotator = AgentRotator()
    headers = rotator.get_headers()
    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "Accept-Language" in headers


def test_agent_rotator_rotates():
    rotator = AgentRotator()
    agents = {rotator.get_user_agent("funda") for _ in range(20)}
    assert len(agents) > 1


def test_user_agent_pool_size():
    assert len(USER_AGENTS) >= 50
