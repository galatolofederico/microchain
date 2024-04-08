import unittest
from microchain import OpenAIChatGenerator, LLM

class TestOpenAI(unittest.TestCase):
    def test_oai_error(self):
        generator = OpenAIChatGenerator(
            model="gpt-3.5-turbo",
            api_key="WRONG_API_KEY",
            api_base="https://api.openai.com/v1",
            temperature=0.7
        )

        llm = LLM(generator=generator)
        error = llm([dict(role="user", content="First message"),])
        self.assertEqual(error, "Error: timeout")

if __name__ == '__main__':
    unittest.main()