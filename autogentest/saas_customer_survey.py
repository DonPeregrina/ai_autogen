from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChat, GroupChatManager
import openai

openai.api_key = "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"
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

llm_config = {
    "api_key": openai.api_key,
    "seed": 53,
    "temperature": 0,
    "request_timeout": 300
}

user_proxy = UserProxyAgent(
   name="Admin",
   system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved "
                  "by this admin.",
   code_execution_config=False,
)

engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the 
    code in a code block that specifies the script type. The user can't modify your code. So do not suggest 
    incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by 
    the executor. Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. 
    Check the execution result returned by the executor. If the result indicates there is an error, fix the error and 
    output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed 
    or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your 
    assumption, collect additional info you need, and think of a different approach to try.''',
)

planner = AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin 
    approval. The plan may involve an engineer who can write code and an executor and critic who doesn't write code. 
    Explain the plan first. Be clear which step is performed by an engineer, executor, and critic.''',
    llm_config=llm_config,
)

executor = AssistantAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    code_execution_config={"last_n_messages": 3, "work_dir": "feedback"},
)

critic = AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback.",
    llm_config=llm_config,
)

groupchat = GroupChat(agents=[user_proxy, engineer, planner, executor, critic], messages=[], max_round=50)
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

user_proxy.initiate_chat(manager, message='''Quiero que construyas una aplicacion en streamlit que le pida al usuario que ingrese un
                         excel o csv , est  o lo usaras para crear un dataframe y tambien que sea parte del knowledge retrieval
                         dado, dejaras la aplicacion lista para que el usuario le haga preguntas a open ai de este dataframe y 
                         que el sistema le responda hallazgos matematicos sobre estos datos. Crearas codigo para que se genere un 
                         agente con las herramientas de open ai para que pueda darle las respuestas al usuario sobre esos datos ''')
