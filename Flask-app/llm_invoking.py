import os

from dotenv import load_dotenv
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma

load_dotenv(dotenv_path=Path('.env'))

class LLM_Invoking():
    
    def __init__(self):
        self.__api_key = os.getenv("GEMINI_API_KEY")
        self.__llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=self.__api_key)
        self.__output_parser = StrOutputParser()

        self.__embeddings = GoogleGenerativeAIEmbeddings(google_api_key=self.__api_key, model='models/embedding-001')
        self.__vector_store = Chroma(
            collection_name="bombatronic_collection",
            embedding_function=self.__embeddings,
            persist_directory="../AI/chroma_db"
        )

    def is_rag_needed(self, input_text):
        prompt = ChatPromptTemplate([
            ("system", "You are an LLM that would specialize in answering "
            "questions related to Air Quality Index and its parameters, whilst also"
            "posessing a strong knowledge on Fire Cases worldwide, how to mitigate them, and "
            "the solution behind it if the user were to have a question surrounding it"),
            ("user", "I posses additional information about Air Quality, Fire Incidents, and"
            "a team called Bombatronic, do you think based on my question here can it help"
            "you to get a better understanding of my question, which is, {input} , also JUST ANSWER"
            "AS IN YES OR NO, do not answer anything besides YES or NO")
        ])
        chain = prompt | self.__llm | self.__output_parser
        response = chain.invoke({"input": input_text})
        return response.strip().lower()

    # input_text = str(input())
    # rag_state = is_rag_needed(input_text=input_text)
    # print(rag_state)
    def chatbot_response(self, input_text, rag_state, input_metadata):
        prompt = ChatPromptTemplate([
            ("system", "You are an LLM that would specialize in answering "
            "questions related to Air Quality Index and its parameters, whilst also"
            "posessing a strong knowledge on Fire Cases worldwide, how to mitigate them, and "
            "the solution behind it if the user were to have a question surrounding it. Also you need"
            "to possess an additional information about the team BOMBATRONIC when askes about it thats"
            "given from the context by the user. Keep your answer to the question in a paragaph like "
            "format and make it sweet and intuitive"),
            ("user", "{input}\n\n: {context}")
        ])
        
        chain = prompt | self.__llm | self.__output_parser
        if rag_state == "yes" and input_metadata != []:
            print(input_metadata[0], type(input_metadata[0]))
            retrieved_docs = self.__vector_store.similarity_search(
                query=input_text,
                k=3,
                filter={"title": input_metadata[0]} if input_metadata else None
            )
            print(retrieved_docs)
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        else:
            context = ""

        response = chain.invoke({"input": input_text, "context": context})

        return response
