from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
import torch

def read_paragraph_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        paragraph = file.read()
    return paragraph

def answer_question(question, paragraph, tokenizer, model):
    # Tokenize and encode input
    inputs = tokenizer(question, paragraph, return_tensors="pt", truncation=True)

    # Perform model inference
    start_positions, end_positions = model(**inputs).values()

    # Get answer span from positions
    answer_start = torch.argmax(start_positions, dim=1).item()
    answer_end = torch.argmax(end_positions, dim=1).item() + 1
    answer_tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end])

    # Remove special tokens from the answer
    answer_tokens = [token for token in answer_tokens if token not in tokenizer.all_special_tokens]
    
    # Convert tokens back to string
    answer = tokenizer.convert_tokens_to_string(answer_tokens)

    # If no answer is found, return a message
    if answer.strip() == "":
        raise ValueError("Sorry, I couldn't find an answer in the paragraph.")

    return answer

def main():
    # Example file path
    file_path = r"C:\Users\91988\Downloads\Large Scale Question Answering\ai paragraph.txt"

    # Read paragraph from file
    paragraph = read_paragraph_from_file(file_path)

    # Load fine-tuned DistilBERT model and tokenizer
    model_name = "distilbert-base-cased-distilled-squad"  # Replace with your fine-tuned model
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForQuestionAnswering.from_pretrained(model_name)

    while True:
        # Question to ask
        question = input("Ask a question (type 'exit' to stop): ")

        if question.lower() == 'exit':
            break

        try:
            # Get the answer
            answer = answer_question(question, paragraph, tokenizer, model)
            print("Answer:", answer)
        except ValueError as e:
            print(e)

if __name__ == "__main__":
    main()
