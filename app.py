import streamlit as st
from abc import ABC
import boto3
import json
import re
import requests

#UNSPLASH_ACCESS_KEY = ''

def fetch_image(query):
    url = f'https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}'
    response = requests.get(url)
    data = response.json()
    return data.get('urls', {}).get('regular')




import os
#os.environ["AWS_ACCESS_KEY_ID"]=""
#os.environ["AWS_SECRET_ACCESS_KEY"]=""
#os.environ["AWS_DEFAULT_REGION"]=""



class Prompt(ABC):
    def __init__(self, speaker, text):
        self.speaker = speaker
        self.text = text

    def __str__(self):
        return f"\n\n{self.speaker}: {self.text}"

    def __repr__(self):
        return self.__str__()

class HumanPrompt(Prompt):
    def __init__(self, text):
        super().__init__("Human", text)

class AssistantPrompt(Prompt):
    def __init__(self, text):
        super().__init__("Assistant", text)

class ConversationChain:
    def __init__(self, prompts: list = None, generator = None):
        if prompts is None:
            prompts = []
        self.prompts = prompts
        self.generator = generator

    def __str__(self):
        return "\n".join([str(p) for p in self.prompts])

    def __repr__(self):
        return self.__str__()

    def __add__(self, prompt: Prompt):
        return ConversationChain(self.prompts + [prompt], self.generator)

    # access list elements with []
    def __getitem__(self, index): #-> Prompt | ConversationChain:
        print("Getting item for index", index)
        if isinstance(index, slice):
            return ConversationChain(self.prompts[index], self.generator)
        else:
            return self.prompts[index]

    def generate(self):
        # non mutating self
        prompt = self.__str__() + "\n\Assistant:"
        # print(prompt)
        generated = ''.join(self.generator(prompt))
        return self + AssistantPrompt(generated)

def invoke_bedrock_anthropic_claude_v2(prompt):
    """Invoke Anthropic Claude v2 model."""
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        endpoint_url='https://bedrock.us-east-1.amazonaws.com')
    def body(_prompt: str) -> str:
        return json.dumps(
            {
                'prompt': _prompt,
                'max_tokens_to_sample':2048,
                'temperature':0.0,
                'top_k':250,
                'top_p':0.999,
                'stop_sequences':['Human:'],
            },
        )
    model_id = 'anthropic.claude-v2'
    accept = '*/*'
    content_type = 'application/json'
    try:
        response = bedrock_runtime.invoke_model_with_response_stream(
            body=body(prompt),
            modelId=model_id,
            accept=accept,
            contentType=content_type)

        request_id = response['ResponseMetadata']['RequestId']

        for m in response['body']:
            b = m.get('chunk', {}).get('bytes', b'')
            json_response: dict = json.loads(b)
            resp: str = json_response.get('completion', '')
            # print('🤖 Out <%s>: %s', request_id, repr(resp))
            yield resp
            # relinquish control to the event loop,
            # allowing other tasks and callbacks to run

            if json_response['stop_reason']:
                # print(
                #     '🤖 Stop <%s> with %s',
                #     request_id,
                #     json_response['stop_reason'],
                # )
                break

    except Exception as err:
        raise err
    


# Streamlit app
st.title("VEGAN RECIPIES")

# User inputs
user_ingredients = st.text_input("Enter ingredients separated by commas")
user_restrictions = st.text_input("Enter dietary restrictions")
user_diet_preferences = st.text_input("Enter diet preferences")

if st.button("Find Recipes"):
    ingredients = user_ingredients
    restrictions = user_restrictions
    diet_preferences = user_diet_preferences

    prompt = "Can you please recommend me 5 vegan recipes with these ingredients - "+ingredients+". I also have these restrictions - "+ restrictions+ ". Along with these preferences - "+ diet_preferences

    s1  = HumanPrompt(prompt)
    chain = ConversationChain([s1], generator=invoke_bedrock_anthropic_claude_v2)

    chain = chain.generate()

    chain2 = ConversationChain([chain], generator=invoke_bedrock_anthropic_claude_v2)
    chain3 = ConversationChain([chain], generator=invoke_bedrock_anthropic_claude_v2)
    chain4 = ConversationChain([chain], generator=invoke_bedrock_anthropic_claude_v2)
    chain5 = ConversationChain([chain], generator=invoke_bedrock_anthropic_claude_v2)
    chain6 = ConversationChain([chain], generator=invoke_bedrock_anthropic_claude_v2)
    chain7 = ConversationChain([chain], generator=invoke_bedrock_anthropic_claude_v2)


    st.write(chain[-1])

    chain2 = ConversationChain([chain], generator=invoke_bedrock_anthropic_claude_v2)
    chain2 = chain + \
    HumanPrompt("Extract just the names of all the recipes and provide no other information")+ \
    chain2
    chain2 = chain2.generate()

    l = str(chain2[-1])
    import re

    input_string = l
    # Define a pattern to match the recipe names
    pattern = re.compile(r'\d+\.\s+(.*)')

    # Find all matches in the string
    matches = pattern.findall(input_string)

    items = []

    # Print the extracted recipe names
    for match in matches:
        items.append(match)

    print(items)



    chain3 = chain + \
    HumanPrompt("Ok now generate the entire list of things to do for the first recipe, the quantities of each ingredients, the proportions and the procedure in steps.")+ \
    chain3
    chain3 = chain3.generate()
    st.title(items[0])

    images = fetch_image(str(items[0]))
    if images:
        st.image(images, caption=str(items[0]))
    else:
        st.write(f"No image found for the {str(items[0])} recipe.")

    st.write(chain3[-1])



    chain4 = chain + \
    HumanPrompt("Ok now generate the entire list of things to do for the second recipe, the quantities of each ingredients, the proportions and the procedure in steps.")+ \
    chain4
    chain4 = chain4.generate()
    st.title(items[1])
    images = fetch_image(str(items[1]))
    if images:
        st.image(images, caption=str(items[1]))
    else:
        st.write(f"No image found for the {str(items[1])} recipe.")
    st.write(chain4[-1])



    chain5 = chain + \
    HumanPrompt("Ok now generate the entire list of things to do for the third recipe, the quantities of each ingredients, the proportions and the procedure in steps.")+ \
    chain5
    chain5 = chain5.generate()
    st.title(items[2])
    images = fetch_image(str(items[2]))
    if images:
        st.image(images, caption=str(items[2]))
    else:
        st.write(f"No image found for the {str(items[2])} recipe.")
    st.write(chain5[-1])



    chain6 = chain + \
    HumanPrompt("Ok now generate the entire list of things to do for the fourth recipe, the quantities of each ingredients, the proportions and the procedure in steps.")+ \
    chain6
    chain6 = chain6.generate()
    st.title(items[3])
    images = fetch_image(str(items[3]))
    if images:
        st.image(images, caption=str(items[3]))
    else:
        st.write(f"No image found for the {str(items[3])} recipe.")
    st.write(chain6[-1])


    chain7 = chain + \
    HumanPrompt("Ok now generate the entire list of things to do for the fifth recipe, the quantities of each ingredients, the proportions and the procedure in steps.")+ \
    chain7
    chain7 = chain7.generate()
    st.title(items[4])
    images = fetch_image(str(items[4]))
    if images:
        st.image(images, caption=str(items[4]))
    else:
        st.write(f"No image found for the {str(items[4])} recipe.")
    st.write(chain7[-1])