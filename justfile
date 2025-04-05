run_agents:
  langgraph dev --config ./agents/langgraph.json

run_web:
  cd web && npx vite serve --port=7070

run_browseruse:
  uv run -m agents.supervisor_with_browseruse_agent.agent