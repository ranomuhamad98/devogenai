import chromadb

import pandas as pd

from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.embeddings import VertexAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatVertexAI

from genaiapp.modules.utils.ocr_confidence import spredConf

class InformationChat:
    def __init__(self,df_path):
        self.df        = pd.read_csv(df_path)
        self.documents = self.databaseCreate()
        # print(self.documents)

        self.embedding = VertexAIEmbeddings()
        self.new_client = chromadb.EphemeralClient()

        self.vectordb = Chroma.from_documents(documents=self.documents,embedding=self.embedding,client=self.new_client,collection_name="docs_collection",persist_directory="vector-db")

        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 5})

        self.llm = ChatVertexAI(model_name="chat-bison",max_output_tokens = 2000)
        
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm,chain_type="stuff",retriever=self.retriever,return_source_documents=True)

    def process_llm_response(self,llm_response):
        output = llm_response['result']
        output+='\n\nSources:'
        for source in llm_response["source_documents"]:
            output+=source.metadata['source']+'\n\n'
        return output

    def databaseCreate(self):
        documents = []
        for i in range(len(self.df)):
            data            = self.df.iloc[[i]]

            page_content    = spredConf(data['documents'].values[0])
            page            = data['page'].values[0]
            source          = data['path_data'].values[0]

            source          = source.replace(".pdf",'')
            source          = source+"_Page_"+str(page)+".pdf"

            documents.append(Document(page_content=page_content, metadata={"source": source}))

        return documents

    def qaInformationSearch(self,query):
        llm_response = self.qa_chain(query)
        return self.process_llm_response(llm_response)