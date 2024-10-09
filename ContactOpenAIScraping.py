from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

class ContactOpenAIScraping:

    def __init__(self):
        self.api_key = ''
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-1106",
            temperature=.3,
            max_tokens=None,
            timeout=None,
            max_retries=3,
            api_key = self.api_key,
        )
        messages = [
            (
                "system", """You are an agent tasked with extracting contact information (emails, phone numbers, fax numbers, WhatsApp numbers, and addresses) from a contact page text. 
            
                => Only extract valid information that is actually present in the provided text. Do not generate or include any placeholder data such as 'info@company.com', 'support@company.com', '123-456-7890', '+1234567890', or any similar non-existent contacts.
                => Make sure the value of the key "phones" contains all valid phone numbers, fax numbers, and WhatsApp numbers.
                => Ensure the value of the key "addresses" contains valid, identifiable addresses.
                => Ensure you identify and extract the relevant information accurately.
                """
            ),
            (
                "human", """Extract the contact information (emails, phone numbers, and addresses) and format it into a JSON object from the following text. Make sure not to create any additional keys—only 'emails' and 'phones' and 'addresses'. Ensure the value of the key 'phones' contains all phone, fax, and WhatsApp numbers from the contact page text. If no information is found for any of the keys, the value should be an empty list (e.g., "emails": [], "phones": [], "addresses": [])."""
            ),
            (
                "human","{contact_page_text}"
            )
            ]
        
        self.json_llm = self.llm.bind(response_format={"type": "json_object"})
        self.template = ChatPromptTemplate.from_messages(messages)
        self.chain = self.template | self.json_llm
        
    def predict(self, input_contact_page_text):
        ai_msg = self.chain.invoke({'contact_page_text':input_contact_page_text})
        results = {}
        results['content'] = json.loads(ai_msg.content)
        results['completion_tokens'] = ai_msg.response_metadata['token_usage']['completion_tokens']
        results['prompt_tokens'] = ai_msg.response_metadata['token_usage']['prompt_tokens']
        results['total_tokens'] = ai_msg.response_metadata['token_usage']['total_tokens']
        results['model_name'] = ai_msg.response_metadata['model_name']
        return results