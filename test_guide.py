from rag.guide import INTERVIEW_GUIDE


for item in INTERVIEW_GUIDE:
    print(f"{item.question_id} | {item.topic}")
    print(item.question)
    print()