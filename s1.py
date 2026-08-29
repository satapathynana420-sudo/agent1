import warnings
import streamlit as st
st.header("CURRENCY CONVERTER AI AGENT")
warnings.filterwarnings(
    "ignore",
    message=".*langchain-community.*",
    category=DeprecationWarning,
)
# import json
from langchain_community.tools import tool
from langchain_core.tools import InjectedToolArg
from langchain_core.messages import HumanMessage
from typing import Annotated
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
import os

from dotenv import load_dotenv
load_dotenv()

a=st.text_input('input1')
b=st.text_input('input2')


##creating tool1
@tool
def get_conversion_factor(base_currency:str,target_currency:str)->float:
    """
    This function fetches the currency conversion factor between a given base currency and a target currency
    """

    url=f"https://v6.exchangerate-api.com/v6/{os.environ.get('EXCHANGE_RATE_API')}/pair/{base_currency}/{target_currency}"

    response=requests.get(url)

    return response.json()



##creating tool2
@tool
def convert(base_currency_value: int, conversion_rate: Annotated[float, InjectedToolArg]) -> float:
  """
  given a currency conversion rate this function calculates the target currency value from a given base currency value
  """

  return base_currency_value * conversion_rate





llm=ChatGoogleGenerativeAI(
   model='gemini-3.5-flash-lite'
)
llm_with_tools=llm.bind_tools([get_conversion_factor,convert])


if st.button('convert'):
 messages = [HumanMessage(f'What is the conversion factor between {a} and {b}, and based on that can you convert 1 {a} to {b}')]


 ai_message=llm_with_tools.invoke(messages)





 messages.append(ai_message)

 import json

 for tool_call in ai_message.tool_calls:
  

  if tool_call['name'] == 'get_conversion_factor':
    tool_message1 = get_conversion_factor.invoke(tool_call)

    conversion_rate = json.loads(tool_message1.content)['conversion_rate']

    messages.append(tool_message1)




    ai_message2=llm_with_tools.invoke(messages)


    messages.append(ai_message2)



    for tool_call in ai_message2.tool_calls:
     
      
     if tool_call['name']=='convert':
      

      tool_call['args']['conversion_rate']=conversion_rate

      tool_result=convert.invoke(tool_call)
    

      messages.append(tool_result)



      final_response= llm_with_tools.invoke(messages)


 

      st.success(final_response.text)
