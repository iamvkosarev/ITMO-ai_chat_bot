import time

from ai_chat_bot.model.llm_chat_data import LLMDialog, LLMRole, LLMMessage
from ai_chat_bot.services.llm.llm import LLMType
from ai_chat_bot.services.llm_operator import LLMOperator


class LLMResearchService:
    def __init__(self, llm_operator: LLMOperator):
        self.llm_operator = llm_operator

    async def process_file(self, file_path: str) -> str:
        loaded_dialog = LLMDialog.load_from_json(file_path)

        start_model: LLMType = self.llm_operator.current_type

        sum_points = 0
        sum_time = 0
        requests_count = self.get_assistents_phrases_count(loaded_dialog)
        for i in range(requests_count):
            prompt_to_test, before_response, question = self.get_dialog_until_assistent_index(loaded_dialog, i)

            start_time = time.time()
            result = await self.llm_operator.handle_prompt(prompt_to_test, loaded_dialog.context)
            end_time = time.time()

            self.llm_operator.switch_current_llm(LLMType.OPEN_AI_CHATGPT_3_5_TURBO)

            difference = await self.check_difference(before_response.text, result)
            sum_points += int(difference)
            self.llm_operator.switch_current_llm(start_model)
            elapsed_time = end_time - start_time
            sum_time += elapsed_time
            print(f"Вопрос: {question.text}\n1){before_response.text}\n2){result}\nОценка сходства: {difference}, время выполнения: {elapsed_time:.4f}\n")
        return f"{self.llm_operator.current_llm_name()}:\nочков - {sum_points}\nср. время - {sum_time/requests_count}"

    def get_assistents_phrases_count(self, llm_dialog: LLMDialog):
        count = 0
        for message in llm_dialog.messages:
            if message.role == LLMRole.ASSISTANT:
                count += 1
        return count

    def get_dialog_until_assistent_index(self, llm_dialog: LLMDialog, index: int) -> (LLMDialog, LLMMessage, LLMMessage):
        new_dialog = LLMDialog()
        count = 0
        question: LLMMessage = None
        for message in llm_dialog.messages:
            if message.role == LLMRole.ASSISTANT:
                if index <= count:
                    return new_dialog, message, question
                count += 1
            if message.role == LLMRole.USER:
                question = message
            new_dialog.add_message(message)
        return new_dialog, None, None

    async def check_difference(self, before_response, result) -> str:
        new_dialog = LLMDialog()
        new_dialog.add_message(LLMMessage(f"1) {before_response}\n2) {result}", LLMRole.USER))
        return await self.llm_operator.handle_prompt(new_dialog,
                                                     "Ты система, которая сравнивает две фразы на соответсвие друг "
                                                     "к другу. В качестве результата всегда идёт число от 0 до 10, где 0 "
                                                     "- полное не соответсвие по смыслу и 10 это полное соответсвие по смыслу, то есть слава могут не совпадать, но мыль будет той же. Никакого текста, только число от 0 до 10")
