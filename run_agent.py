from agents.sunbeam_agent import get_agent

agent = get_agent()

while True:
    q = input("\nAsk ▶ ")
    if q.lower() in ["exit", "quit"]:
        break

    res = agent.invoke({"input": q})
    print("\n🤖", res["output"])