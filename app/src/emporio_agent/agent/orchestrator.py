"""Loop de tool calling: envia mensagens ao LLM, executa as tools pedidas via tools.registry, respeita MAX_TOOL_ROUNDS e devolve a resposta final.

Pode importar de: agent.llm_client, agent.prompts, agent.memory, tools.registry
Nao deve importar de: db, services, cli
Fase de implementacao: F6
"""

from emporio_agent.agent.llm_client import LLMClient
from emporio_agent.agent.memory import ConversationMemory
from emporio_agent.agent.prompts import SYSTEM_PROMPT
from emporio_agent.config import Settings
from emporio_agent.tools.registry import dispatch, schemas


class Agent:
    def __init__(self, settings: Settings, session_id: str | None = None):
        self.settings = settings
        self.memory = ConversationMemory(settings, session_id)
        self.llm = LLMClient(settings)

    def respond(self, user_text: str) -> str:
        user_text = user_text.strip()
        if not user_text:
            return "Pode me dizer como posso ajudar?"
        self.memory.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *self.memory.history()]
        for _ in range(self.settings.max_tool_rounds):
            response = self.llm.chat(messages, schemas())
            if not response.choices:
                raise RuntimeError("O provedor retornou uma resposta vazia.")
            message = response.choices[0].message
            tool_calls = getattr(message, "tool_calls", None) or []
            if not tool_calls:
                content = (message.content or "Desculpe, nao consegui formular uma resposta agora.").strip()
                self.memory.append({"role": "assistant", "content": content})
                return content

            assistant_message = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {"id": call.id, "type": "function", "function": {
                        "name": call.function.name, "arguments": call.function.arguments,
                    }} for call in tool_calls
                ],
            }
            messages.append(assistant_message)
            self.memory.append(assistant_message)
            for call in tool_calls:
                output = dispatch(self.settings, call.function.name, call.function.arguments)
                tool_message = {"role": "tool", "tool_call_id": call.id,
                                "name": call.function.name, "content": output}
                messages.append(tool_message)
                self.memory.append(tool_message)
        final_message = "Desculpe, nao consegui concluir essa consulta agora. Tente novamente com mais detalhes."
        self.memory.append({"role": "assistant", "content": final_message})
        return final_message
