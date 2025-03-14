import autogen
import dotenv

from autogen_transcribe_video_with_captions.functions import recognize_transcript_from_video

dotenv.load_dotenv()

config_list = autogen.config_list_from_dotenv(
    dotenv_file_path=".",
    filter_dict={
        "model": ["gpt-4"],
    }
)

llm_config = {
    "functions": [
        {
            "name": "recognize_transcript_from_video",
            "description": "recognize the speech from video and transfer into a txt file",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_filepath": {
                        "type": "string",
                        "description": "path of the video file",
                    }
                },
                "required": ["audio_filepath"],
            },
        }
    ],
    "config_list": config_list,
    "timeout": 120,
}

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the "
                   "task is done.",
    llm_config=llm_config,
    code_execution_config={"work_dir": "scripts"},
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "scripts"},
)

user_proxy.register_function(
    function_map={
        "recognize_transcript_from_video": recognize_transcript_from_video,
    }
)


def initiate_chat():
    video_file = input("What is the file you want to caption?: ")
    audio_file = input("What is your captioned filename?: ")

    user_proxy.initiate_chat(
        chatbot,
        message=f"For the video this project named {video_file}, recognize the speech and transfer it into a script "
                f"file, then take that script file and create captions overtop the video and save the video in the "
                f"captioned directory with the name {audio_file}. "
    )


initiate_chat()
