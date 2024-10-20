class Response:
    def __init__(self, answer, action, info):
        """
        answer: will contain the actual string that the user will read
        action: will contain the token that is used to navigate the agent behaviour
        info: will be used to pass additiona information between different phases of the agent

        If answer is blank this mean tah the produced output will be routed toward another pahse of the agent
        """
        self.answer = answer
        self.action = action
        self.info = info
