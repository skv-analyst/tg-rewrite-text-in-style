import os
import anthropic


class AsqLlm:
    def __init__(self, model, api_key, style, text: str, temperature: float):
        self.model = model
        self.api_key = api_key
        self.style = style
        self.text = text
        self.temperature = temperature

    def asq(self):
        client = anthropic.Anthropic(api_key=self.api_key)

        message = client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=self.temperature,
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': f'Rewrite the following text using the following instructions: {self.style} \n\n'
                                    f'Text:\n {self.text}\n\n'

                        }
                    ]
                }
            ]
        )

        return message


if __name__ == "__main__":
    ...
