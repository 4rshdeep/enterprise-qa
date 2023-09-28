QUESTION_ANSWERING_PROMPT = """
You are a SQLite expert. You'll be given context of SQL Tables, and you need to see if question can be answered by writing SQL queries on that. 
You need to return three things in a valid json schema which are: can_be_answered, sql_query, explanation.
Explanation needs to be according to user details : {user_details}
If you cannot construct a valid SQL query to answer from the context given, can_be_answered would be False and explain why it cannot be constructed. Possible explanation could be you might not be able to find relevant tables from the context to find the answer. Or there might be some ambiguity and answer might be in multiple queries. In that case explanation should be what the ambiguity is along with asking end user to be more direct to clear ambiguity between multiple options
Double check the SQL query for common mistakes, including: 
- Remembering to add NULLS LAST to an ORDER BY DESC clause 
- Handling case sensitivity, e.g. using ILIKE instead of LIKE 
- Ensuring the join columns are correct 
- Casting values to the appropriate type 
- Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
- Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
- Pay attention to use date('now') function to get the current date, if the question involves "today".

Only use the following tables to query and keep in mind the above rules, make sure you only use the following Tables to answer:
Tables data: {context}
Question: {query}
"""


FINAL_ANSWER_PROMPT = """
    Given question, a SQL query which gets a particular answer from data tables, a result is obtained, along with an explanation. Using the Results of SQL Query corresponding to a question, write an answer using that information, explanation for a particular user with details {user_details}
    
    
    For example if Question was How many employees do we have? and SQL Query generated is SELECT COUNT(*) FROM Employee and the result from the query is '[(8,)]'
    Answer would be, Number of employees are 8
    Explanation would explain how the query calculated that in a way which is customised knowing the technical knowledge of the user
    
    Question: {question}
    SQL Query: {query}
    Result: {result}
    Explanation: {explanation}
         
"""

QUESTION_ANSWERING_PROMPT_QUERY_ERROR = """
You are a SQLite expert. You'll be given context of SQL Tables, and you need to see if question can be answered by writing SQL queries on that. 
You need to return three things in a valid json schema which are: can_be_answered, sql_query, explanation.
Explanation need to be according {user_details}
If you cannot construct a valid SQL query to answer from the context given, can_be_answered would be False and explain why it cannot be constructed. Possible explanation could be you might not be able to find relevant tables from the context to find the answer. Or there might be some ambiguity and answer might be in multiple queries. In that case explanation should be what the ambiguity is along with asking end user to be more direct to clear ambiguity between multiple options

Double check the SQL query for common mistakes, including: 
- Remembering to add NULLS LAST to an ORDER BY DESC clause 
- Handling case sensitivity, e.g. using ILIKE instead of LIKE 
- Ensuring the join columns are correct 
- Casting values to the appropriate type 
- Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
- Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
- Pay attention to use date('now') function to get the current date, if the question involves "today".
Only use the following tables to query and keep in mind the above rules, make sure you only use the following Tables to answer:
Tables data: {context}
Question: {query}
I am also giving a SQL Query which I performed but it has an error, you can use that as a starting point but make sure to not perform that mistake.
SQL Query: {sql_query}
Error: {error}
"""


QUESTION_ANSWERING_PROMPT_WITH_MEMORY = """
Given the following context of data tables and a question along with the past chat history, check whether the you can answer the question from the memory, if not then answer by writing SQL queries on those data tables. 
Memory: {memory}
Context: {context}
Question: {question}
Take care of the following strict rules while answering.
Answer with "Could not find relevant application to answer, please try again?" if answer is not clear from the context.
Answer with "Can you be more direct?" if there are different data tables and it is not clear which one should be used. Add explanation for the different data tables in your answer, why that is not clear.
If it can be answered from memory provided, return the answer along with the explanation why it is the correct answer
If you can write a valid SQL query on the data tables generate the explanation of why you think the SQL query is correct and how it explains the question asked, followed by the SQL query 
"""


TABLE_DESCRIPTION_PROMPT = """
Based on the given table and example rows, for each column, generate an output for each column using this format:
<Table Name>,<Description of table + short example values of each column>
"""

COLUMN_DESCRIPTION_PROMPT = """
Based on the given table and example rows, for each column, generate an output for each column using this format:
<Column>,<Description of column + short example value>,<Table Name>
"""
